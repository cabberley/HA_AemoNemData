"""Exercise the integration against the pinned library and real HA classes."""

import asyncio
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from aiohttp import ClientSession, web
from aiohttp.test_utils import TestServer
from aemonemdata.exceptions import AuthError, ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.aemo_nem import binary_sensor, sensor
from custom_components.aemo_nem.const import AEMONEM_COORDINATOR, DOMAIN, STATES
from custom_components.aemo_nem.coordinator import AemoNemUpdateCoordinator
from custom_components.aemo_nem.sensor_properties import ENTITY_DETAILS


START = datetime(2026, 11, 11, 8, tzinfo=timezone(timedelta(hours=10)))
REGIONS = {"NSW1", "QLD1", "VIC1", "SA1", "TAS1"}


class CompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config_dir = tempfile.TemporaryDirectory()
        self.addCleanup(config_dir.cleanup)
        self.hass = HomeAssistant(config_dir.name)
        self.session = ClientSession()
        self.addAsyncCleanup(self.session.close)
        self.entry = Mock(
            spec=ConfigEntry,
            data={"au_states": STATES},
            options={"polling_interval": 15},
            entry_id="compatibility",
        )
        with patch(
            "custom_components.aemo_nem.coordinator.async_get_clientsession",
            return_value=self.session,
        ):
            self.coordinator = AemoNemUpdateCoordinator(self.hass, self.entry)
        self.addAsyncCleanup(self.coordinator.async_shutdown)
        self.hass.data[DOMAIN] = {
            self.entry.entry_id: {AEMONEM_COORDINATOR: self.coordinator}
        }

    async def entities(self):
        sensors, flags = [], []
        await sensor.async_setup_entry(self.hass, self.entry, sensors.extend)
        await binary_sensor.async_setup_entry(self.hass, self.entry, flags.extend)
        flow_count = sum(
            len(summary["interconnector_flows"])
            for summary in self.coordinator.data["current_30min_forecast"].values()
        )
        self.assertEqual(len(sensors), len(REGIONS) * len(ENTITY_DETAILS) + flow_count)
        self.assertEqual(len(flags), len(REGIONS) * 2)
        self.assertEqual(len({entity.unique_id for entity in sensors}), len(sensors))
        for entity in sensors:
            self.assertRegex(entity.entity_id, r"^sensor\.[a-z0-9_]+$")
            self.assertTrue(entity.name)
            self.assertTrue(entity.available)
            self.assertIn(entity.device_key, REGIONS)
            entity.native_value
            entity.extra_state_attributes
            entity.native_unit_of_measurement
            entity.device_class
            entity.state_class
        for entity in flags:
            self.assertIsInstance(entity.is_on, bool)
        return sensors, flags

    async def test_dashboard_to_entities_and_repeated_updates(self):
        demand = 7000

        async def dashboard(request):
            endpoint = request.match_info["endpoint"]
            if endpoint == "config.json":
                return web.json_response({"xApiKey": "test-key"})
            self.assertEqual(request.headers["x-api-key"], "test-key")
            if endpoint == "cumulativePrice":
                data = {"items": [
                    {
                        "r": region,
                        "dt": (START + timedelta(minutes=minutes)).isoformat(),
                        "a": actual,
                        "p": price,
                        "cp": 123456,
                    }
                    for region in REGIONS
                    for minutes, actual, price in (
                        (5, 1, 100), (10, 1, -50), (30, 0, 400), (60, 0, 600)
                    )
                ]}
            elif endpoint == "marketPriceLimits":
                data = {"items": [
                    {"key": key, "value": value}
                    for key, value in (
                        ("AdministeredPriceCap", 600),
                        ("MarketPriceCap", 23200),
                        ("CumulativePriceThreshold", 2000000),
                    )
                ]}
            elif endpoint == "elecSummary":
                data = {
                    "summary": [
                        {
                            "regionId": region,
                            "settlementDate": "2026-11-11T08:10:00",
                            "apcFlag": int(region == "SA1"),
                            "marketsuspendedFlag": int(region == "TAS1"),
                            "totalDemand": demand,
                            "netInterchange": -100,
                            "scheduledGeneration": 4000,
                            "semischeduledGeneration": 3000,
                            "interconnectorFlows": json.dumps([{
                                "name": "V-SA", "value": -100,
                                "exportlimit": 500, "importlimit": -600,
                            }]),
                        }
                        for region in REGIONS
                    ],
                    "prices": [{"regionId": region, "rrp": None} for region in REGIONS],
                }
            else:
                self.fail(f"Unexpected endpoint: {endpoint}")
            return web.json_response({"data": data, "errors": []})

        app = web.Application()
        app.router.add_get("/{endpoint}", dashboard)
        app.router.add_get("/NEM/v1/PWS/NEMDashboard/{endpoint}", dashboard)
        server = TestServer(app)
        await server.start_server()
        self.addAsyncCleanup(server.close)
        with (
            patch("aemonemdata.aemonem.BaseUrl", SimpleNamespace(
                API=str(server.make_url("/")).rstrip("/")
            )),
            patch("aemonemdata.aemonem.current_30min_window", return_value=(
                START, START + timedelta(minutes=30)
            )),
            patch("custom_components.aemo_nem.coordinator.datetime") as clock,
        ):
            clock.now.return_value = START + timedelta(minutes=1)
            await self.coordinator.async_refresh()
            sensors, flags = await self.entities()
            for entity in sensors:
                with self.subTest(region=entity.device_key, entity=entity.entity_name):
                    if entity.entity_name == "period_1":
                        self.assertEqual(entity.native_value, 0.1)
                    elif entity.entity_name == "period_2":
                        self.assertEqual(entity.native_value, -0.05)
                    elif entity.entity_name.startswith("period_"):
                        self.assertIsNone(entity.native_value)
                    elif entity.entity_name == "current_30min_avg":
                        self.assertEqual(entity.native_value, 0.025)
                    elif entity.entity_name == "settlement_date":
                        self.assertEqual(entity.native_value.utcoffset(), timedelta(hours=10))
                    elif entity.entity_name == "V-SA":
                        self.assertEqual(entity.native_value, -100)
                        self.assertEqual(entity.extra_state_attributes, {
                            "export_limit": 500, "import_limit": -600
                        })
                    elif entity.entity_name == "current_30min_forecast":
                        forecasts = entity.extra_state_attributes["forecast"]
                        self.assertEqual(len(forecasts), 2)
                        self.assertEqual(forecasts[0]["price"], 0.4)
                        self.assertEqual(
                            forecasts[0]["end_time"] - forecasts[0]["start_time"],
                            timedelta(minutes=30),
                        )
            for entity in flags:
                expected_region = "SA1" if entity.entity_name == "apc_flag" else "TAS1"
                self.assertEqual(entity.is_on, entity.device_key == expected_region)
            demand = 7100
            await self.coordinator.async_refresh()
            for entity in sensors:
                if entity.entity_name == "total_demand":
                    self.assertEqual(entity.native_value, 7100)
            self.assertFalse(self.session.closed)

    async def test_errors_remain_unavailable_until_successful_retry(self):
        self.coordinator.data = {"cached": True}
        with patch("custom_components.aemo_nem.coordinator.datetime") as clock:
            clock.now.return_value = START + timedelta(minutes=1)
            for exception in (ClientError, AuthError):
                with self.subTest(exception=exception.__name__):
                    error = exception("dashboard unavailable")
                    fetch = AsyncMock(side_effect=error)
                    with patch.object(self.coordinator.client, "get_aemo_data", fetch):
                        with self.assertRaises(UpdateFailed) as raised:
                            await self.coordinator._async_update_data()
                        self.assertIs(raised.exception.__cause__, error)
                        await self.coordinator.async_refresh()
                        self.assertFalse(self.coordinator.last_update_success)
                        clock.now.return_value = START + timedelta(minutes=4)
                        await self.coordinator.async_refresh()
                        self.assertFalse(self.coordinator.last_update_success)
                        self.assertEqual(fetch.await_count, 3)
                    result = {"recovered": True}
                    with patch.object(
                        self.coordinator.client, "get_aemo_data",
                        AsyncMock(return_value=result),
                    ) as fetch:
                        await self.coordinator.async_refresh()
                        self.assertTrue(self.coordinator.last_update_success)
                        self.assertIs(self.coordinator.data, result)
                        await self.coordinator.async_refresh()
                        fetch.assert_awaited_once_with(STATES)
                    clock.now.return_value = START + timedelta(minutes=1)

    async def test_cancellation_propagates(self):
        with patch.object(
            self.coordinator.client, "get_aemo_data",
            AsyncMock(side_effect=asyncio.CancelledError),
        ):
            with self.assertRaises(asyncio.CancelledError):
                await self.coordinator._async_update_data()
        self.assertFalse(self.session.closed)

    @unittest.skipUnless(os.environ.get("AEMONEM_LIVE_TESTS") == "1", "Live API opt-in")
    async def test_live_all_regions(self):
        await self.coordinator.async_refresh()
        sensors, _ = await self.entities()
        data = self.coordinator.data
        self.assertEqual(set(data["current_30min_forecast"]), REGIONS)
        for region in REGIONS:
            summary = data["current_30min_forecast"][region]
            self.assertIsInstance(summary["current_5min_period_price"], (int, float))
            self.assertTrue(summary["forecast"])
            self.assertEqual(summary["settlement_date"].utcoffset(), timedelta(hours=10))
        self.assertTrue(sensors)
        self.assertFalse(self.session.closed)
