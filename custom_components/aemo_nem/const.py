"""Constants for the aemo_nem integration."""

from enum import StrEnum
from datetime import timedelta
import logging
from homeassistant.const import Platform

LOGGER = logging.getLogger(__package__)

DOMAIN = "aemo_nem"


DEFAULT_NAME = "Aemo Nem"
POLLING_INTERVAL = "polling_interval"
UPDATE_LISTENER = "update_listener"
SCAN_INTERVAL = 60
TIMEOUT = 20
LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(minutes=1)
AEMONEM_COORDINATOR = "aemo_nem_coordinator"
AEMO_WWW = "https://aemo.com.au/"
MANUFACTURER = "Australian Energy Market Operator"
ATTRIBUTION = "Data provided by AEMO"

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

REGIONS = [
    "NSW1",
    "QLD1",
    "SA1",
    "TAS1",
    "VIC1",
]

STATES = [
    "NSW",
    "QLD",
    "SA",
    "TAS",
    "VIC",
]