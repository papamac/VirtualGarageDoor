![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/doubleDoor.png)

# Monitoring and control of conventional garage door openers in Indigo

The Virtual Garage Door plugin monitors one or more Indigo devices to track the
garage door motion as it moves through its operational cycles. The plugin
reports the door state in the states dictionary of a Virtual Garage Door Opener
device.  The states are displayed in the Indigo devices display and are
available for use in triggers and scripts. The plugin also provides actions
to open, close and toggle the garage door.

The plugin can monitor a wide variety of optional devices that are already
available in Indigo as supported devices or through existing 3rd party plugins.
These include both z-wave devices and custom/wired devices. Device types
include relays, contact sensors, tilt sensors, and multisensors. Please see the
latest list of
[supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices)
in the Virtual Garage Door wiki.

The garage door tracking accuracy depends upon the selected devices and the
door's operational cycle.
[Section 3.4](https://github.com/papamac/VirtualGarageDoor/wiki/3.-Design)
of the wiki contains a detailed discussion of the tracking performance under a
wide range of conditions. This allows the user to select the set of monitored
devices that meets his specific needs.

Virtual Garage Door Opener devices are compatible with the HomeKit Bridge
plugin and Siri. After setup, you can say "Hey Siri, check the garage doors" or
"Hey Siri, open the garage main door".

The following table lists the top level requirements for the Virtual Garage
Door plugin:

| Requirement            | Description                                                                                                                                |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Minimum Indigo Version | 2022.1                                                                                                                                     |
| Python Library (API)   | Official (3.X)                                                                                                                             |
| Requires Local Network | Yes                                                                                                                                        |
| Requires Internet      | Yes                                                                                                                                        |
| Hardware Interfaces    | Various z-wave / custom devices from the [supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices) list. |

Please see the
[Virtual Garage Door wiki](https://github.com/papamac/VirtualGarageDoor/wiki)
for details on the design, configuration, and use of the plugin.

You can download the latest version of the plugin at the 
[Indigo Plugin Store](https://indigodomo.com/pluginstore/267/).
Your bug reports, comments and suggestions will be greatly appreciated.  Please
post them on papamac's
[Virtual Garage Door user forum](https://forums.indigodomo.com/viewforum.php?f=374).

