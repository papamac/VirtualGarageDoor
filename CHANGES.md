# Release Notes #

Releases and major changes to the Virtual Garage Door plugin are described in
this CHANGES.md file.  Changes of lesser importance may be described in the
changes section of individual module docstrings if appropriate.

Your bug reports, comments and suggestions will be greatly appreciated.  Please
post them on papamac's
[Virtual Garage Door User Forum](https://forums.indigodomo.com/viewforum.php?f=374).

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
