![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/READMEfigures/DoubleDoor.png)

Monitoring and control of conventional garage door openers in Indigo
==========

Overview
----------

The Virtual Garage Door plugin monitors multiple Indigo devices to track garage
door motion and report the door state in the states dictionary of a Virtual
Garage Door Opener device.  The states are displayed in the Indigo devices
display and are available for use in triggers and scripts.  The plugin also
provides actions to open, close and toggle the garage door.

The plugin can monitor a wide variety of sensor devices to track the door
state/status. The tracking accuracy will depend upon the selected sensor
devices and the user's door operation modes (use cases). In general, accurate
tracking through all use cases will require more sensors. Tracking performance
is discussed in detail later in this README.

Virtual Garage Door Opener devices are compatible with the HomeKit Bridge
plugin and Siri. After setup, you can say "Hey Siri, check the garage doors" or
"Hey Siri, open the garage main door".

Theory of Operation
----------

The end-to-end operation of the Virtual Garage Door plugin and its supporting
plugins/devices is illustrated in Figure 1. It shows the data flow between the
various Indigo plugins and z-wave drivers (yellow) and the Indigo device
objects (green) that are needed for the overall Virtual Garage Door operation.
All interaction between the Virtual Garage Door plugin and other plugin/driver
software occurs through the attributes and methods of the Indigo device
objects.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/READMEfigures/Figure1.png)

### Virtual Garage Door Plugin and Virtual Garage Door Opener Devices ###

The Virtual Garage Door plugin creates Virtual Garage Door Opener devices using
GUIs specified in the Devices.xml. The GUIs allow the user to specify the door
travel time and identify all the sensor devices that are to be used by the
plugin to monitor and control the door. The user can optionally select an
activation relay (used as both a sensor and a control device), a closed sensor,
an open sensor, and a vibration sensor. Each sensor (except the relay) can have
a custom onOffState and a polarity inversion option. A travel timer is created
by the plugin for each opener device and initialized with the specified door
travel time. Data for these monitored devices are saved in the pluginProps
for the opener device. During startup, the device id and state data for all
selected devices are saved in a local monitored devices dictionary. 

Once the opener device is started, the plugin uses the Indigo deviceUpdated
callback to continuously monitor onOffState state changes for the monitored
devices in the monitored devices dictionary. Selected transition events (e.g.,
closedSensor off) are used along with the current door state (from the states
directory) to dynamically update the door state as the door moves through its
operational sequence. The new door state is obtained from a global
DOOR_STATE_TRANSITIONS dictionary in plugin.py. The dictionary is keyed by the
current door state and the monitored device transition events for that
state.

Note that the opener device state is called "doorStatus" in the states 
dictionary for compatibility with other plugins. The door status can be open,
closed, stopped, opening, or closing. The states dictionary also includes an
"onOffState" that is set to on (True) when the door is closed and off (False)
otherwise. This can be confusing in the Indigo device action display. The user
must click "Turn Off" to open the garage door and "Turn On" to close it. 

If an activation relay is selected the opener plugin can execute open, close,
or toggle actions.  It does this through callback methods that invoke relay
actions to activate the opener. The plugin also responds to device actions
(turn on, turn off, toggle) and a universal status request.

### Other Plugins and Monitored/Control Devices ###

For completeness, Figure 1 shows the other plugins and devices that support the
Virtual Garage Door plugin.  Monitored/control devices are managed by their
plugins and/or z-wave drivers to interface to their respective device hardware.
These devices then interact with the opener plugin through their device states
and actions. Examples of actual device hardware are shown. All the examples
have been tested with the Virtual Garage Door plugin except the Aeotec and
FortrezZ devices.

Finally, the HomeKit Bridge plugin provides the interface between the Virtual
Garage Door opener devices and Apple HomeKit/Siri. Because the HomeKit Bridge 
plugin only uses the opener device's onOffState, the HomeKit accessory
only knows whether the door is open or closed. The opening, closing, and
stopped states are ignored.

Doors and Devices
----------
A conventional garage door/opener is illustrated if Figure 1.  When activated
by pressing the activation wall button (or an RF remote), the opener begins to
raise the door from the closed position. It stops when the door becomes fully
open, after a time that is approximately the travel time. Another activation
will reverse the process, closing the door until it becomes fully closed in
roughly the same travel time. Thus, a normal operational cycle is:

>closed ---> (activation) opening ---> (travel time) open ---> (activation)
> closing ---> (travel time) closed

The normal operational cycle may be interrupted if the door is obstructed,
the safety sensors are tripped, or any manual activations occur while the door
is in motion.  The interrupted opening cycle stops on interruption then, on
activation, it reverses into a closing cycle:

>closed ---> (activation) opening ---> (interrupting activation) stopped --->
>(activation) closing ---> (travel time) closed

In the interrupted closing cycle, the opener immediately auto-reverses and
returns to open:

>open ---> (activation) closing ---> (interrupting activation) opening ---> 
>(travel time) open ---> (activation) closing ---> (travel time) closed



To track these cycles through their various states, the Virtual Garage Door
plugin requires data from multiple sensor devices. It also requires an opener
relay device that is connected to the activation wall switch if Indigo/HomeKit
are to be used to open and close the door. Figure 1 includes a table of
optional sensor/control devices color coded to show their approximate
placement/connection to the door. The following paragraphs describe these
optional devices in more detail. Also, examples of specific z-wave/custom/wired
devices are referenced in Figure 2.

1. closed sensor - The closed sensor is a device whose primary state is on when
the door is stopped and fully closed.  It may be a z-wave/wired/custom contact
sensor or a z-wave tilt sensor. Most wired security systems use a closed
contact sensor as a garage door alarm zone. In some cases, this sensor can be
connected to a z-wave/wired digital input device for use as Virtual Garage Door
closed sensor. If the alarm panel is interfaced directly to Indigo (see the
AD2USB plugin) the closed alarm zone device may be used directly as a Virtual
Garage Door closed sensor.
2. open sensor - The open sensor is a device whose primary state is on when
the door is stopped and fully open.  Like the closed sensor, it may be a
z-wave/wired/custom contact sensor or a z-wave tilt sensor.
3. activation sensor - The activation sensor is a device that momentarily turns
on whenever the garage door opener is activated. This is usually done by
interfacing the two wires from the activation wall button to a digital input.
Normally, when the button is not pressed, there is a DC voltage across these
wires that can be adapted to turn a digital input device on. When the button
is pressed, the wires are shorted and the input will momentarily turn off.
Inverting the polarity of this input provides the desired activation sensor.
On some older door openers it is possible that this scheme may work when
activation results from pressing an RF remote or from door blockage... but
don't count on it. Normally the activation sensor will go on only when the
activation wall button or the is pressed or the opener relay is closed.  If you
don't care about tracking activations from the wall switch, there is an
alternative to the digital input. You can specify the opener relay device as
the activation sensor. Its onOffState will go on when the relay is closed and
then off when the relay opens. This makes a fine activation sensor, but does
not include activations from the wall button, the RF remote or door blockage.
This limitation limits the usefulness of the activation sensor in tracking door
states because it does not cover all activations. It is nevertheless useful in
some sensor configurations... more on this later.
4. travel timer - The travel timer is an Indigo Timers and Pesters plugin
device. A unique timer device is created by the Virtual Garage Door plugin for
each door opener device and initialized with a time that is slightly longer
than the actual travel time for that door.  The travel timer is restarted
(turned on) whenever the door is set in motion. Timeout events (timer off) are
used in two different ways depending on the sensor configuration. If closed
and/or open sensors are in the device configuration, a travel timeout indicates
a door blockage because the door did not complete its opening/closing in the
travel timer interval. If there is no closed and/or open sensor, a travel
timeout is interpreted as a completion of the motion. For example, during
opening if there is no open sensor, a travel timeout will change the door state
to open. Similarly, during closing if there is no closed sensor, the door state
will become closed. Door blockage will not be detected in these cases. These
rules are detailed in Figure 3 below.
5. opener relay - The opener relay is a normally open relay that is connected
across the two wires of the activation wall switch. It is used by the Virtual
Garage Door plugin to activate the garage door opener in response to plugin
actions. This device is optional, but is needed if Indigo/HomeKit are to be
used to open and close the door.

----------
### Safety Issue - Unattended Operation ###
**Unattended operation is defined as activation of the garage door opener when
the person (or software) causing the activation has no line of sight to the
door. There is an obvious physical injury or entrapment issue for any person
that may be in the garage or near/under the door during unattended
opening/closing. The US Consumer Product Safety Commission has specified a
number of requirements for unattended operation of residential garage doors.
These include flashing lights and audio alarm signals for five seconds before
the unattended activation. Details are available online at
<https://ecfr.io/Title-16/Section-1211.14>.**

**When using the Virtual Garage Door plugin with an opener relay device there
is nothing to prohibit unattended operation. It is up to the user (you) to do
the right thing. YOU MAY NOT USE THIS VIRTUAL GARAGE DOOR PLUGIN FOR UNATTENDED
OPERATION AS DEFINED ABOVE. IF YOU REALLY REQUIRE UNATTENDED OPERATION YOU
SHOULD INVEST IN A NEWER DOOR OPENER THAT IS ACTIVATED VIA MOBILE PHONE AND
HAS THE REQUIRED SAFETY FEATURES BUILT IN.**

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/READMEfigures/Figure2.png)





Figure 3 illustrates the state transitions that are coded in the
DOOR_STATE_TRANSITIONS dictionary. The blue and orange circles are the five
dynamic door states and the arrows are the monitored device transition events
that change the door states. The numbers in the small yellow circles are
reference numbers that correlate the events to entries in the dictionary.

Figure 3 also shows a green start state end the logic that selects the door
state at opener device startup. If, for whatever reason, the garage door opener
state gets out of synch with the actual door position, open or close the door
and restart the plugin or the opener device.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/READMEfigures/Figure3.png)

The Virtual Garage Door Opener device also includes an onOffState in its states
dictionary. The opener plugin sets the onOffState to on (True) if the door
state is not closed. It is off (False) if the door is closed. The onOffState is
used by the HomeKit Bridge plugin to determine the closed/open state for the
HomeKit/Siri garage door accessory. The polarity must be inverted, however,
when the HomeKit accessory is configured.

In addition to managing the opener device's states, the Virtual Garage Door
plugin executes all plugin actions. These include the custom plugin actions,
device actions, and universal action listed in Figure 2. Open and on actions
are ignored if the door is not closed when the action is requested. Similarly,
close and off actions only work if the door is open.



User Guide
----------

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/READMEfigures/Figure4.png)

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/READMEfigures/Figure5.png)