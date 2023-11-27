![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/doubleDoor.png)

# Monitoring and control of conventional garage door openers in Indigo

The Virtual Garage Door (VGD) plugin monitors one or more Indigo devices to
track the garage door as it moves through its operational cycles. It saves the
door states in the states dictionary of a VGD opener device. The states are
displayed in the Indigo Home window and are available for use by scripts,
action groups, control pages, triggers, and other plugins. The VGD plugin also
provides actions to open, close and toggle the garage door.

VGD opener devices work with Apple HomeKit by using the HomeKitLink Siri (HKLS)
plugin. After installation and setup, you can use the Apple Home application to
monitor and control your garage doors.  With any Apple device, you can also
monitor and control your doors verbally using Siri. Say "Siri, check the garage
door status" or "Siri, open the garage main door".

The VGD plugin can monitor a wide variety of optional devices that are already
available in Indigo as supported devices or through existing 3rd party plugins.
These include both z-wave devices and custom/wired devices. Device types
include relays, contact sensors, tilt sensors, and multisensors. Please see the
latest list of
[supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices).

The garage door tracking accuracy depends upon which _monitored devices_ are
selected and the door's operational cycle. The wiki
[Design page](https://github.com/papamac/VirtualGarageDoor/wiki/3.-Design)
(Section 3.4) contains a detailed discussion of the tracking performance under a
wide range of conditions. This allows the user to select the set of _monitored
devices_ to best meet his specific needs.

The following table lists the top level requirements for the Virtual Garage
Door plugin:

| **Requirement**        | **Description**                                                                                                                            |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Indigo Version         | 2022.1.0 or higher                                                                                                                         |
| Python Library (API)   | Official (3.x)                                                                                                                             |
| Requires Local Network | Yes                                                                                                                                        |
| Requires Internet      | Yes                                                                                                                                        |
| Hardware Interfaces    | Various z-wave / custom devices from the [supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices) list. |

Please see the
[VGD wiki](https://github.com/papamac/VirtualGarageDoor/wiki)
for details on the design, configuration, and use of the plugin.

You can download the latest version of the plugin at the 
[Indigo Plugin Store](https://indigodomo.com/pluginstore/267/).
Your bug reports, comments and suggestions will be greatly appreciated.  Please
post them on papamac's
[VGD user forum](https://forums.indigodomo.com/viewforum.php?f=374).

