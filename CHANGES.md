# Release Notes #

Releases and major changes to the Virtual Garage Door plugin are described in
this CHANGES.md file.  Changes of lesser importance may be described in the
changes section of individual module docstrings if appropriate.

Your bug reports, comments and suggestions will be greatly appreciated.  Please
post them on papamac's
[Virtual Garage Door User Forum](https://forums.indigodomo.com/viewforum.php?f=374).

## GitHub Release v1.1.1, January 12, 2023

### New door state and documentation to support full-capability HomeKit integration

This release updates the wiki to document the changes introduced in the interim 
version v1.1.0.  The v1.1.1 Python code is identical to v1.1.0.  Code changes
from the prior release (v1.0.6) are described in the interim version v1.1.0
release note below.

GitHub release v1.1.1 provides a fully documented, formally released Virtual
Garage Door (VGD) plugin that can fully integrate with Apple HomeKit. The
version allows the use of the Apple Home app to close the door when it is not
fully open. This facilitates recovery from obstructed states after the
obstruction has been cleared.  It also enables two new capabilities using the
Home application: (1) continuous state tracking, and (2) obstruction detection
and reporting. To use these new capabilities, the VGD opener devices must
interface to HomeKit using a future release of the HomeKitLink Siri (HKLS)
plugin. The HomeKit capabilities provided by the various combinations of VGD
versions and HomeKit integration plugins is explained in the
[Design pages](https://github.com/papamac/VirtualGarageDoor/wiki/3.-Design)
of the wiki (see Table 2).

## Interim Version v1.1.0, December 18, 2022

### New door state to improve future integration with Apple HomeKit

Interim version v1.1.0 is not an official GitHub release and it is not included
in the Indigo Plugin Store. Although it is tested and capable of user
deployment, it is intended primarily for developer use. Also, the changes in
v1.1.0 are not reflected in the wiki, which continues to describe v1.0.6. In
short, v1.0.6 is still the official released version. When things settle down,
a new official release v1.1.1 with final HomeKit integration changes and an
updated wiki will replace v1.0.6 and v1.1.0.

v1.1.0 captures a number of changes that will enable an improved interface with
Apple HomeKit in the future. It maintains compatibility with current versions
of the HomeKit Bridge (HKB) and HomeKitLink Siri (HKLS) plugins and should
continue to do so as these plugins evolve. If enabled by future HKLS changes,
however, the HomeKit application will recognize opening and closing states (as
well as open and closed) and will detect both opening and closing door
obstruction.  This is the goal.

v1.1.0 includes the following changes:

(1) Add an integer doorState to the device states dictionary to support full
integration with Apple HomeKit. Re-structure plugin.py around the integer
doorState instead of the text doorStatus. The integer doorStates are defined
by: OPEN, CLOSED, OPENING, CLOSING, STOPPED, REVERSING = range(6).

(2) Add state tracking logic for the new REVERSING doorState (and "reversing"
doorStatus) to detect and report interrupted (obstructed) door closing. Update
the transitions in the DOOR_STATE_TRANSITIONS tuple to implement the new
REVERSING state. Immediately transition the REVERSING state to OPENING to
reflect the auto-reversing behavior of the physical door.

(3) Improve error detection and reporting during ConfigUi validation, device
startup, and runtime.
                    
(4) Allow the openGarageDoor action (and indigo.device.turnOff) regardless of
the opener onOffState. This enables recovery from obstructed door conditions
using the Apple HomeKit application.

## GitHub Release v1.0.6, September 8, 2022

### Wiki updates, new devices and plugins, and a bug fix

This release provides a significant update to the wiki, organizing it into
multiple pages, and including new supported devices and references pages.

The supported devices page includes an number of new devices and plugins that
are now usable with the Virtual Garage Door plugin, but have not all been
tested. The specs for these devices and plugins have been reviewed by papamac
and they seem to be suitable for the functions listed. The new deviceTypeIds
are included in the plugin so they will be available in device selection, but
they are not guaranteed to work. If you use any of these with the plugin please
share experience (positive or negative) on papamac's
[Virtual Garage Door user forum](https://forums.indigodomo.com/viewforum.php?f=374). 

This change is intended to satisfy user requests to support a number of Aeotec
devices, Shelly devices, Zooz devices, Virtual Devices, Masqueraded devices,
et al. papamac does not have the resources to test all of these. If users
provide feedback on their experiences, however, we should be able to update the
supported devices page to include only fully-tested devices and plugins in
future releases.

Release v1.0.6 also fixes a bug in state tracking that incorrectly equated a
timer inactive event (tt-off) with an expired timer.  The fix definitively
detects a new timer expired event (tt-exp) to simplify tracking.  The old
tt-off event is ignored.

The release also increases the default value for the vibration sensor reset
delay time from 1.5 to 2 seconds. This was needed to eliminate false vs-on
activations in papamac's home system. The user must set this value for each of
his door openers.

## GitHub Release v1.0.5, August 16, 2022

### Add support for z-wave relay devices

This release allows supported z-wave relay devices to be used with the plugin.
It was specifically added to support the ZooZ Zen 17 z-wave relay, but should
now work with other z-wave relays as well.

## GitHub Release v1.0.4, August 5, 2022

### Improve the README and Wiki documentation

## GitHub Release v1.0.3, July 27, 2022

### Increase maximum value of the vibration sensor reset delay time

This release increases the maximum value of the vibration sensor reset delay
time from 2 to 5 seconds. The default delay remains at 1.5 seconds. Recent
experience with papamac's vibration sensor suggests that the user should have
more lattitude in setting this value.

v1.0.3 also removes the plugin bundle zip file from the repo. A new
indigoplugin.zip file will now be attached to each release for the user's
convenience when downloading from the Indigo Plugin Store.

## GitHub Release v1.0.2, July 25, 2022

### Cleanup for the initial Indigo release

This release changes some comments and URLs for the initial Indigo release.

## GitHub Release v1.0.1, July 23, 2022

### vibration sensor reset bug fix

This release adds a new user-specified vibration sensor reset delay time to
delay the sensor reset after the door stops. This prevents false vibration
sensor activations from residual actuator shaking. The delay time defaults to
1.5 seconds. This value works for papamac's opener, but may not be sufficient
for yours. You may need to increase it if you experience false vibration sensor
activations after the door stops.

The change adds a new field in the opener device configuration UI. This
requires that you delete and re-create your opener devices to use the change.

## Initial GitHub release v1.0.0, July 22, 2022

This is the initial version of the Virtual Garage Door plugin for Indigo.
It is fully functional and documented in README.md and GitHub WIKI. Code
documentation in plugin.py is still in work.

The activation sensor feature that was implemented in version 0.9.1 is no
longer supported because of its limited usefulness.
