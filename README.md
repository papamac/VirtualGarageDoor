![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/doubleDoor.png)
## Monitoring and control of conventional garage door openers in Indigo

The Virtual Garage Door plugin monitors one or more Indigo devices to track the
garage door motion as it moves through its operational cycles. The plugin
reports the door state in the states dictionary of a Virtual Garage Door Opener
device.  The states are displayed in the Indigo devices display and are
available for use in triggers and scripts.  The plugin also provides actions
to open, close and toggle the garage door.

The plugin can monitor a wide variety of optional devices that are already
available in Indigo as supported devices or through existing 3rd party plugins.
These include both z-wave devices and custom/wired devices. Device types
include contact sensors, relays, tilt sensors, and multisensors. The garage
door tracking accuracy depends upon the selected devices and the door's
operational cycle.

Virtual Garage Door opener devices are compatible with the HomeKit Bridge
plugin and Siri. After setup, you can say "Hey Siri, check the garage doors" or
"Hey Siri, open the garage main door".

| Requirement            |                       |
|------------------------|-----------------------|
| Minimum Indigo Version | 2022.1                |
| Python Library (API)   | Official              |
| Requires Local Network | Yes                   |
| Requires Internet      | Yes                   |
| Hardware Interfaces    | Various z-wave/custom |


Please see the
[Virtual Garage Door wiki](https://github.com/papamac/VirtualGarageDoor/wiki)
for details on the design, configuration, and use of the plugin.

You can download the latest version of the plugin at the 
[Indigo Plugin Store](https://indigodomo.com/pluginstore).
Your bug reports, comments and suggestions will be greatly appreciated.  Please
post them on papamac's
[Virtual Garage Door User Forum](https://forums.indigodomo.com/viewforum.php?f=374).

