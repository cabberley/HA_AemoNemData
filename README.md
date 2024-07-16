<h1 align="center">
  <a href="https://aemo.com.au/"><img src="https://raw.githubusercontent.com/cabberley/ha_aemonemdata/main/ha_aemonem_logo.png" width="480"></a>
  <br>
  <i>AEMO NEM data Home Assistant Integration</i>
  <br>
  <h3 align="center">
    <i> Custom Home Assistant component for collecting AEMO NEM pricing and monitoring Price Caps. </i>
    <br>
  </h3>
</h1>

<p align="center">
  <img src="https://img.shields.io/github/v/release/cabberley/HA_aemonemdata?display_name=tag&include_prereleases&sort=semver" alt="Current version">
  <img alt="GitHub" src="https://img.shields.io/github/license/cabberley/HA_aemonemdata"> <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/cabberley/ha_aemonemdata/main.yml">
  <img alt="GitHub Issues or Pull Requests" src="https://img.shields.io/github/issues/cabberley/ha_aemonemdata"> <img alt="GitHub User's stars" src="https://img.shields.io/github/stars/cabberley">

</p>
<p align="center">
    <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg"></a>
</p>
<p align="center">
  <a href="https://www.buymeacoffee.com/cabberley" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
</p>

This integration collects data for the National Electricity Market (NEM) from the Australian Energy Market Operator (AEMO). Creating a set of sensors for each Region of the market. The integration currently focuses on the data that is normally found on the NEM Price and Demand dashboard.
I created this Integration as I use Amber Energy for my retail electricity supply which is billed on the spot prices in my region. However, while Amber has access to additional data points I found that the pricing estimates sometimes were overly ambitious prices which ultimately collapsed and ended up being closer to the AEMO NEM forecast prices. So I use this to help provide some context and additional data that may or may not support the forecast Amber pricing when deciding in particular to discharge my Hybrid Inverter battery to the Grid.

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=cabberley&repository=HA_AemoNemData&category=integration)

To install this Home Assistant Custom Integration, either Click on the open HACS Repository or by manually copying the `custom_components/aemo_nem` folder into your Home assistant `custom_components` folder.

> [!TIP]
> Don't forget to restart your Home Assistant after adding the integration to your HACS!

## Configuration

After adding the Integration to HACS go to your settings and add the Integration.
Complete the form and submit.

- Give your integration a name or leave the default
- Select which Market Regions you want to monitor

If successful you should now find a device for each market and the current data for it.

### Additional configuration options/steps

After your initial integration setup is complete, there is an optional settings you can adjust for the polling interval. Navigate to the Device screen and click on Configure, an options dialog will pop up.

> [!NOTE]
> The HASS update coordinator polling frequency has been adjusted to reflect the data update timing that the AEMO NEM normally has. AEM NEM data is updated once every 5 minutes as each new 5min dispatch period begins. Typically it is normally not before about 40 seconds afer the interval has commenced that the data refreshes on the NEM dashboard. The default HASS coordinator has been set to poll the NEM data every 15 seconds commencing after 20 seconds past the 5 minute interval and continue for the first 2 minutes. It will then pause until the next 5 minute period starts.

# Sensor explanations

The integration create a set of sensors the provide both actual data and several calculated values to provide some insight as to what is occurring during the 30min "billing" period. 
**Most peoples $ per kw is based on the average of the 6 x 5min spot price intervals.**

## Pricing Data

### Current 5min Period Price

This is the set spot price for the current 5min spot period.

### Current 30min Average

This is the average price so far for the 30 minute pricing period. 
Sum of the price for the 5 minute periods so far/the number of periods so far

### Current 30min Forecast

This is the forecast price for the current 30 min period, normal it is the next forecast price that is at the end of the current period (either the 0 or 30 minute time)

#### Additional data in attributes for 30min Forecast

In the attributes for this sensor you will find the current forecast price for all future current 30min periods.
The attribute structure is similar to other Integrations like Amber Electric and Solcast. Enabling you to generate a comparison set of future time period pricing.

### Current 30min Estimate

This combines the actual prices for the current 30 minute period with the current price of the forecast of the 30 min period used for the remaining periods.
(Sum of current 5min prices + 30min price forecast times (6 minus the number of actual 5min periods so far)) divided by 6

### Period 1 - 6

For the 5 minute periods which have had their price set this is the value for each 5 minute period of the 30 minutes. For periods which have not yet had their price set the value will be 0

### Current Cumulative Price

This is the rolling value of the cumulative price that AEMO uses to determine if the market will be suspended or a price cap will be imposed. When the value of this equals or exceeds the Cumulative Price Threshold it will trigger the suspension and Price Cap.

## Other Data

### 5min periods of current 30mi window

The number of completed 5 minute spot prices of the current 30min pricing period.

### Active Price Cap

On or Off if the markets price cap has been activated

### Market Suspended

On or Off if the market has been suspended

### Administered Price Cap

The Regions current Price Cap, if a market suspension of Price Cap is triggered by the cumulative pricing then this is the current price per MW for all pricing until the suspension is lifted.

### Cumulative Price Threshold

The value that if the rolling cumulative price reaches it will trigger the Market Suspension and Active Price Caps. Increases normally each 1st of July

### Current Percent Cumulative Price

This is the current percentage of the rolling cumulative price with the Cumulative Price Threshold. If the percentage is getting high there is a chance of the Market Suspension and Price Caps being implemented.

### Market Price Cap

The Regions current maximum price per MW that the 5 minute pricing can reach. Increases normally each year on the 1st of July.
