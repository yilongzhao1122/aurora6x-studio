# Data sources and displayed values

Calories use `ActivityMonitor.getInfo().calories`, the device-provided total for the current day. A single recorded activity is not the full day's active calories. The project does not estimate active or resting calories.

Steps, goals, distance and daily total calories come from ActivityMonitor; battery and solar intensity from System; heart rate, oxygen saturation and altitude use available current values or SensorHistory samples; weather comes from Garmin Weather. Exact fields and expiry handling are in `source/Metrics.mc`. Availability depends on the device, permissions, sensors and phone synchronization. Solar intensity is not charging power.

Valid zero values are retained. Missing or expired values display `--`. Simulator fixtures are sample values, not the wearer's data. Bundled lunar/solar-term and moon-phase tables cover 2020–2040.

See the [Chinese data notes](数据说明.md) for official API documentation links and the [validation statement](Validation.en.md) for testing limits.
