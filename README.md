![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/doubleDoor.png)

# Monitoring and control of conventional garage door openers in Indigo

## Baseline Capabilities

The Virtual Garage Door (VGD) plugin monitors one or more Indigo devices to
track the garage door as it moves through its operational cycles. It saves the
door states in the states dictionary of a VGD opener device. The states are
displayed in the Indigo Home window and are available for use by scripts,
action groups, control pages, triggers, and other plugins. The VGD plugin logs
the door's status and also provides actions to open/close the door.

VGD opener devices work with Apple HomeKit by using the HomeKitLink Siri (HKLS)
plugin. After installation and setup, you can use the Apple Home application to
monitor and control your garage doors.  With any Apple device, you can also
monitor and control your doors verbally using Siri. Say "Siri, check the garage
doors" or "Siri, open the Garage Main Door".

The VGD plugin can monitor a wide variety of optional devices that are
available in Indigo as built-in devices or 3rd party plugin devices. These
include both Z-wave devices and custom/wired devices. Device types include
relays, contact sensors, tilt sensors, and multisensors. Please see the latest
list of
[supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices).

The garage door tracking accuracy depends upon which _monitored devices_ are
selected and the door's operational cycle. The VGD Design wiki
[Section 3,4](https://github.com/papamac/VirtualGarageDoor/wiki/3.-Design)
contains a detailed discussion of the tracking performance under a wide range
of conditions. This allows the user to select a set of _monitored devices_ that
best meets his specific needs.


## Optional Safety and Security Capabilities

VGD v2.0 includes two optional capabilities that provide improved user safety
and security:

The first capability provides opening/closing action groups and delays. It
allows users to optionally specify an action group and/or a delay to be
executed before the garage door is opened or closed.  It can be used for any
purpose, but is well suited to mitigate the safety issue inherent in unattended
door operation (see the VGD wiki
[Section 5.1](https://github.com/papamac/VirtualGarageDoor/wiki/5.-User-Notes)).
In this case, an action group that sounds an alarm and a delay of 5 seconds
will meet the the Consumer Product Safety Commission's requirements for safe
unattended door operations.

The second capability provides VGD lock devices and optional locking/unlocking
action groups. The VGD plugin creates a new lock device for each opener device.
Locking the lock device will disable all opener/lock actions (except unlock and
request status), effectively locking the door. It will then optionally disable
power to the door opener and/or engage a separate mechanical lock to physically
secure the door. See the latest list of
[supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices)
for compatible power switch and mechanical lock devices. Additionally, optional
locking/unlocking action groups can be configured to meet any other user
security needs.


## Top Level Requirements

| **Requirement**        | **Description**                                                                                                                            |
|------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Indigo Version         | v2022.1.0 or later                                                                                                                         |
| Python Library (API)   | v3.0 or later                                                                                                                              |
| HKLS Version           | v0.6.61 or later                                                                                                                           |
| Requires Local Network | Yes                                                                                                                                        |
| Requires Internet      | Yes                                                                                                                                        |
| Hardware Interfaces    | Various z-wave / custom devices from the [supported devices](https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices) list. |


