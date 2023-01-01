![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/doubleDoor.png)

# Monitoring and control of conventional garage door openers in Indigo

The Virtual Garage Door (VGD) plugin monitors one or more Indigo devices to
track the garage door motion as it moves through its operational cycles. It
reports the door state in the states dictionary of a VGD opener device.  The
states are displayed in the Indigo devices display and are available for use in
triggers, scripts, and other plugins. The VGD plugin also provides actions
to open, close and toggle the garage door.

VGD opener devices are compatible with the HomeKit Bridge (HKB) plugin (being
deprecated) and the HomeKitLink Siri (HKLS) plugin. After installation and
setup of either plugin, you can use the Apple Home application to monitor and
control your garage door.  With any Apple device, you can also monitor and
control the door verbally using Siri. Say "Hey Siri, check the garage door
status" or "Hey Siri, open the garage main door".

The VGD plugin can monitor a wide variety of optional devices that are already
available in Indigo as supported devices or through existing 3rd party plugins.
These include both z-wave devices and custom/wired devices. Device types
include relays, contact sensors, tilt sensors, and multisensors. Please see the
latest list of
[supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices)
in this wiki.

The garage door tracking accuracy depends upon the selected devices and the
door's operational cycle.
[Section 3.4](https://github.com/papamac/VirtualGarageDoor/wiki/3.-Design)
of this wiki contains a detailed discussion of the tracking performance under a
wide range of conditions. This allows the user to select the set of monitored
devices to best meet his specific needs.

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

