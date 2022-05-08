Release Notes
==========
Major changes to the Virtual Garage Door plugin are described in this
CHANGES.md file.  Changes of lesser importance may be described in individual
module docstrings if appropriate.

Version 1.2
---------------
* Added ability for temperature sensors to use ANY device that has a state named "temp", "temperature" or "Temperature", this opens up compatibility to a large number of plugins and sensors that use this state name without having to support those plugin individually.  As a result, direct support for certain plugins was removed if they had been coded to use the "temperature" or "temp" states, such as wunderground.wunderground, piBeacon.i2cTMP102, piBeacon.i2cBMExx, piBeacon.i2cMS5803 and fantasticwWeather.Weather (these devices should continue to work just fine but no longer need special integration).
* Added ability for humidity sensors to use ANY device that has a state named "relativeHumidity", "humidity" or "Humidity", opening up compatibility to any plugin device or sensor that uses this state name without having to support those plugins specifically.  As a result, direct support for certain plugins was removed if they had been coded to use one of these states, such as piBeacon.i2cBMExx, fantasticwWeather.Weather and wunderground.wunderground
* Changed behavior of the HomeKit name field so that each time a device is changed it will change the HomeKit name to match unless editing an existing item, in which case the HomeKit name will not change unless done so manually
* Changed the UI button "Add to HomeKit" to "Save Device" so that it better represents the action to take when both adding and editing a HomeKit device
* Changed Speaker description to "3rd Party, Mute control in Home, Full Siri" because HomeKit updates since HomePod have allowed this device type to be used by Home but only in a mute/unmute capacity but no volume control.  Volume can still be changed via Siri.

