# Release Notes #

Releases and major changes to the Virtual Garage Door plugin are described in
this CHANGES.md file.  Changes of lesser importance may be described in the
changes section of individual module docstrings if appropriate.

## GitHub Release v1.0.1, July 23, 2022 ##

### vibration sensor reset bug fix ###

This release adds a new user-specified vibration sensor reset delay time to
delay the sensor reset after the door stops. This prevents false vibration
sensor activations from residual actuator shaking. The delay time defaults to
1.5 seconds. This value works for papamac's opener, but may not be sufficient
for yours. You may need to increase it if you experience false vibration sensor
activations after the door stops.

The change adds a new field in the opener device configuration UI. This
requires that you delete and re-create your opener devices to use the change.

## Initial GitHub release v1.0.0, July 22, 2022 ##

This is the initial version of the Virtual Garage Door plugin for Indigo.
It is fully functional and documented in README.md and GitHub WIKI. Code
documentation in plugin.py is still in work.

The activation sensor feature that was implemented in version 0.9.1 is no
longer supported because of its limited usefulness.

Your bug reports, comments and suggestions will be greatly appreciated.  Send
them to papamac on the Indigo user forum.