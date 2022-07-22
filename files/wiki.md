![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/doubleDoor.png)

Initial release v1.0.0, July 22, 2022

## 1. Overview ##

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

## 2. Theory of Operation ##

The end-to-end operation of the Virtual Garage Door plugin and its supporting
plugins/devices is illustrated in Figure 1. It shows the data flow between the
various Indigo plugins and z-wave drivers (yellow) and the Indigo device
objects (green) that are needed for the overall Virtual Garage Door operation.
All interaction between the Virtual Garage Door plugin and other plugin/driver
software occurs through the attributes and methods of the Indigo device
objects.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure1.png)

### Virtual Garage Door Plugin and Opener Devices ###

The Virtual Garage Door plugin creates opener devices using GUIs specified in
the Devices.xml. The GUIs allow the user to specify the door travel time and
identify all the devices that are to be used by the plugin to monitor and
control the door. The user can optionally select an activation relay (used as
both a sensor and a control device), a closed sensor, an open sensor, and a
vibration sensor. Each sensor (except the relay) can have a custom on/off state
with optional polarity inversion. The plugin creates a unique travel timer for
each opener device and initializes it with the specified door travel time. Data
for these monitored devices are saved in the plugin properties for the opener
device. During startup, the device id and on/off state name for all selected
devices are saved in a local monitored devices dictionary. 

Once the opener device is started, the plugin uses the Indigo deviceUpdated
callback to continuously monitor on/off state changes for the monitored devices
in the monitored devices dictionary. Selected transition events (e.g., closed
sensor off) are used along with the current door state (from the states
directory) to dynamically update the door state as the door moves through its
operational cycle. The new door state is obtained from a global
DOOR_STATE_TRANSITIONS dictionary in plugin.py. The dictionary is keyed by the
current door state and the monitored device events for that state.

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

### Other Plugins and Monitored Devices ###

For completeness, Figure 1 shows the other plugins and devices that support the
Virtual Garage Door plugin.  Monitored devices are managed by their plugins
and/or z-wave drivers to interface to their respective device hardware. These
devices then interact with the opener plugin through their device states and
actions. Examples of actual device hardware are shown. All the examples
have been tested with the Virtual Garage Door plugin except the Aeotec door/
window sensor and fortrezZ devices.

Finally, the HomeKit Bridge plugin provides the interface between the Virtual
Garage Door opener devices and Apple HomeKit/Siri. Because the HomeKit Bridge 
plugin only uses the opener device's onOffState, the HomeKit accessory
normally displays only the door's open and closed states. If, however, the door
is activated by Indigo, the HomeKit accessory will infer opening and closing
states as well. It's confusing. The HomeKit Bridge plugin should use the
doorStatus in the opener device's states dictionary.

## 3. Physical Door Events, States, and Transitions ##

A conventional garage door/opener is illustrated if Figure 2 along with a
description of the physical events that drive the door's operational cycles.
This door is sometimes referred to as an "auto-reversing" door because it
automatically reverses if an interrupt occurs during closing. This plugin will
not work with a door opener that is not auto-reversing.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure2.png)

A normal opening cycle is initiated by the activation wall button (or an RF
remote). The opener begins to raise the door from the closed position. It stops
when the door becomes fully open, after a time that is approximately the door's
travel time. Normal closing (following a second activation) reverses the
process, closing the door until it becomes fully closed in roughly the same
travel time.

The normal operational cycles may be interrupted if the door is obstructed,
the safety sensors are tripped, or any manual activations occur while the door
is in motion.  During an interrupted opening, the door stops in place. On
re-activation, it reverses into a normal closing cycle. During a closing cycle,
an interrupt immediately auto-reverses the opener drive and the door returns to
open.

Figure 3 summarizes the four operational cycles (1) normal opening, (2) normal
closing, (3) interrupted opening, and (4) interrupted closing in a state
transition diagram.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure3.png)

The _real world events_ described in Figure 2 cause transitions among the five
_physical door states_ (closed, opening, open, closing, and stopped), as the
door moves through an operational cycle. The transitions depend on the event
and the current state of the opener. Note the difference in responding to the
interrupt event when it occurs in the opening and closing states.

## 4. Sensor and Control Devices ##

The functions of the Virtual Garage Door plugin are (1) to track the state of
the physical garage door through all its operational cycles and (2) to control
the activation of the door in Indigo as needed. As described briefly above, the
plugin performs these functions using optional devices that monitor and control
the physical door. It detects on/off state changes (events) from the monitored
devices and tracks the state of the physical door states using the sequence of
monitored device events. Figure 4 shows the physical door with five monitored
devices and a table of candidate device characteristics.

Note that except for the travel timer, the devices are indeed optional; if none
are specified in the opener device GUI, the plugin doesn't complain, it simply
does nothing. The travel timer is created by the plugin, so it is always
available. Other devices may be specified in any combination. Each will offer
advantages for particular operational cycles, to be discussed in Section 5
below.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure4.png)

Table 1 describes the monitored device events that are used to track the
physical door states. Some events are not used by the tracking logic and are
ignored by the plugin. Some travel timer events have logic conditions that
change the way that they are used in tracking. These are given different event
names to distinguish them. This section will describe the five devices and
their events in detail.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/table1.png)

### activation relay (ar)

The activation relay is a normally open relay that is connected across the two
wires of the activation wall switch. It is used in a momentary contact mode to
activate the garage door opener in response to plugin actions. This device is
optional, but is needed if Indigo/HomeKit are to be used to open and close the
door. The momentary closure time required by most garage doors is 0.5 to 1
second. The plugin is hard coded to use the global AR_CLOSURE_TIME of 1 second.

The activation relay permits unattended operation of the door by the plugin.
Unattended operation of a residential garage door is permitted only with
accompanying audible and visible alarms. See the safety issue discussion in
Section 7.

In addition to serving as an opening/closing control device, the activation
relay serves as an activation monitoring sensor. The ar-on event is the
earliest indication that the opener is activated to open or close the door.
It occurs before any closed/open or vibration sensor events.  If available,
ar-on is the best activation indicator for door state tracking. Unfortunately,
the user may choose to activate the opener using the activation wall switch or
RF remote and there will be no ar-on event. This requires the plugin to monitor
all potential activation sensors to ensure accurate tracking. Note that the
ar-off event is not needed and is ignored.

### closed sensor (cs) ###

The closed sensor is a device whose on/off state is on when the door is stopped
and fully closed, and off otherwise.  It may be a z-wave/wired/custom contact
sensor or a z-wave tilt sensor.

Most wired security systems use a closed contact sensor as a garage door alarm
zone. In some cases, this sensor can be connected to a z-wave/wired digital
input device for use as a closed sensor. If the alarm panel is interfaced
directly to Indigo (e.g., using the AD2USB plugin) the alarm zone device may be
used directly by the plugin as a closed sensor. This device is off (clear) if
the door is closed and becomes on (faulted) when it opens. Thus, the on/off 
state must be inverted when using an alarm zone device for the closed sensor
(see Section 6).

It may be convenient to use a z-wave tilt sensor as the closed sensor. This
sensor is off in the vertical (closed) position and on in the tilted (open)
position. Hence, the on/off state must be inverted in this case also.

When using a tilt sensor as the closed sensor, it should be mounted on the top
segment of the door so that it tilts at the earliest possible time when opening
and at the latest possible time when closing. Even so, the cs-off event will be
delayed and the cs-on event will occur sooner than corresponding events using a
contact sensor. These timing differences can affect state tracking. The test
case worked, but be warned that your experience may differ.

The cs-off event indicates an opening activation. The cs-on event indicates
that the door is closed. This event is useful in re-syncing the tracking state
with the physical door state if tracking fails.

### open sensor (os) ###

The open sensor is a device whose on/off state is on when the door is stopped
and fully open.  Like the closed sensor, it may be a z-wave/wired/custom
contact sensor or a z-wave tilt sensor.

If a normally open magnetic contact sensor is wired to a digital input with a
pull-up resistor, the input will be off when the door is open and on otherwise.
Thus, the open sensor state must be inverted.

When using a tilt sensor as the open sensor, it should be mounted on the bottom
segment of the door so that it tilts at the latest possible time when opening
and at the earliest possible time when closing. Timing considerations are
similar to those described above for the closed sensor.

The os-off event indicates a closing activation. The os-on event indicates
that the door is open. This event, like the cs-on event is useful in
re-syncing the tracking state with the physical door state if tracking fails.
This failure recovery feature makes it highly desirable to have a closed
sensor, an open sensor, or both in your monitored device configuration.

### vibration sensor (vs) ###

The vibration sensor is an alternative activation sensor for use when other
options are unavailable (e.g., no activation relay, the user prefers button/RF
remote activation, or when there is no closed/open sensor). Although other
possibilities may exist, this plugin uses the tamper sensor element of the
Aeotec Multisensor 6 as its vibration sensor. This z-wave sensor turns on if
the multisensor is tampered with and stays on until reset with a device turn
off command.

To fulfill its garage door activation function, the multisensor is mounted on
the actuator arm that is connected to the door (see Figure 4). Activation of
the door for either opening or closing gives the multisensor a good shake and
the tamper sensor turns on (vs-on). The plugin sends a turnOff command to the
tamper sensor when the door reaches a stationary state (closed, open, or
stopped). It is then ready to turn on at the next door activation. The vs-off
event resulting from the turnOff command is ignored.

It is conceivable that a false vs-on event could occur when the door has not
been activated. This, however, has not happened during extensive testing.

### travel timer (tt) ###

The travel timer is an Indigo Timers and Pesters plugin device. A unique timer
device is created by the Virtual Garage Door plugin for each door opener device
and initialized with a time that is slightly longer than the actual travel time
for that door. The travel timer is restarted (tt-on) whenever the door is
activated. Timeout events (tt-off) occur when the travel time has expired and
the door has had sufficient time to reach its open/closed/stopped state. tt-on
events are ignored. 

tt-off events are used in two different ways depending on the sensor
configuration. If a closed and/or open sensor is in the monitored device
configuration and there are no cs-on or os-on events, then a tt-off event
indicates a physical door interrupt. The door did not complete its opening/
closing in the allotted travel time.

If there is no closed and/or open sensor there will be no cs-on or os-on event.
In this case, a tt-off event is interpreted as completion of the motion. For
example, during opening, if there is no open sensor, a tt-off event will
cause a transition to open. Similarly, during closing, if there is no closed
sensor, a tt-off event will cause a door state transition to closed. Door
interrupts will not be detected in these cases.

These conditional events are distinguished from a normal tt-off event using
unique event names (see Table 1). tt-off&!cs means tt-off and no closed sensor.
tt-off&!os means tt-off and no open sensor.

# 5. Door State Tracking ##

This section describes the details of how the plugin tracks physical door
states using a sequence of monitored device events. It also describes eight use
cases that describe different ways that the user can operate the garage door.
It predicts tracking accuracy as a function of the monitored device
configuration and the use cases. Finally, this section uses the performance
predictions to guide the user in selecting the best monitored devices for his
situation.

### Virtual Door State Transitions ###

In Section 3, Figure 3 showed how _physical door states_ transition from one to
another in response to _real world events_. In this section, Figure 5 shows how
_virtual door states_ transition from one to another in response to _monitored
device events_. The Virtual Garage Door state transition diagram is structured
so that the _virtual door states_ will match the _physical door states_ as the
door moves through its operational cycles. Tracking accuracy is a measure of
how well the _virtual states_ and the _physical states_ match given a
particular configuration of monitored devices and operational cycles/use cases.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure5.png)

The plugin tracks states by using the global DOOR_STATE_TRANSITIONS dictionary
which codifies the state transitions in Figure 5. The dictionary provides a new
door state keyed by the current door state and the monitored device event. For
example, if the current state is closed and an ar-on event occurs then the
dictionary provides a new door state of opening. The plugin then continues
tracking with the current state equal to opening. Note that each transition
reference number in Figure 5 corresponds to an entry in the
DOOR_STATE_TRANSITIONS dictionary.

Figure 5 has transitions for all possible monitored device events that can
occur from a particular state, including some that may be redundant. Suppose,
for example, that the monitored device configuration includes an ar, a cs, and
a vs. Activation with the ar from the closed state will cause an ar-on event, a
cs-off event, and a vs-on event. The ar-on event (1) will occur first and the
state will transition to opening. In the opening state, the cs-off (10) and
vs-on (11) will cause a null transition to opening. So, tracking wil continue
in the opening state, awaiting additional events.

Figure 5 also includes some out of sequence transitions that are designed to
recover the virtual state if it gets out of sync with the physical state. In
general, anytime a cs-on event occurs, from any state, the new state will
transition to closed (transitions 12, 17, and 20). Similarly, an os-on event
will always transition to open (transitions 5, 24, and 29). This logic is based
on the premise that the cs-on and os-on are reliable events that end in the
closed/open state regardless of whatever happened previously.

### Use Cases ###

A major decision in deploying the Virtual Garage Door plugin is whether to
include an activation relay. Including it has the advantage of being able to
open and close the door using Indigo and HomeKit/Siri. It also has the
advantage of generating ar-on events which are valuable contributors to virtual
state tracking.

If an activation relay is included, the user must decide if he will use it
exclusively for all door activations, or if he will allow mixed activations
using the wall button/RF remote along with the activation relay. Tracking
performance is enhanced by the use of ar-on event, but you can't count on it
if mixed activation is permitted. The situation is the same, of course, if the
user decides not to include an activation relay.

To assess tracking performance two classes of use cases are needed: (1) non-ar
activation (using a wall button/RF remote), and (2) ar activation (using the
activation relay). The use cases within each of these classes are the four
operational door cycles introduced in Section 3: (1) normal opening, (2) normal
closing, (3) interrupted opening, and (4) interrupted closing. Thus, there are
a total of eight use cases for tracking performance assessment: non-ar normal
opening, non-ar normal closing, and so on.

### Door State Tracking Performance ###

The door state tracking performance is a measure of how well the _virtual state
track_ determined from the sequence of monitored device events matches the
actual _physical state track_ from the operational cycle. It depends on the
monitored devices that are available for tracking and also on the use case.
Table 2 defines four color-coded levels of tracking performance, and shows the
assessed performance for eight configurations of monitored devices each
tracking through the eight use cases.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/table2.png)

The ar and tt are included in all the monitored device configurations. The tt
is defined by the plugin and is always available. The ar is shown only because
it is needed in the ar activation use cases. If it is not included in the
monitored devices configuration, then only the non-ar activation use cases are
applicable. Thus, the eight configurations of monitored devices correspond to
the eight combinations of cs, os, and vs devices along with the optional ar and
the tt.

The general performance trends shown in Table 2 are as expected: (1) ar
activation performance is better than that for non-ar activation and (2)
performance improves as more sensors are included in the monitored devices
configuration. The performance with only one of the three sensors (cs, os, and
vs) is generally poor. Performance is improved with any of the two-sensor
combinations, but only the (cs, os, vs) combination provides accurate
performance for all use cases.

### Monitored Device Selection ###

Selection of the monitored device configuration is an individual decision. A
general rule is to use the sensors that you already have and use Table 2 to
see if the performance with those sensors is acceptable. For example, if you
already have a cs from a security alarm zone, and you plan to use ar activation
exclusively, then the (ar, cs, tt) configuration may work for you. It fails in
the interrupted opening cycle, but that is not a common cycle, and you may not
care.

If you require accurate tracking over all operational cycles and plan to use
ar activation exclusively, then the (ar, cs, os, tt) configuration will work
fine. Even if you want to allow non-ar activation or no activation relay, the
(cs, os) combination has merits. It has only a minor failure in the interrupted
opening cycle.

If you want it all, then the (cs, os, vs, tt) is your configuration with or
without an ar. This configuration provides accurate tracking for all
operational cycles and (with the ar) all use cases.

The bottom line is: choose what works best for you in terms of sensors and
desired performance. The Virtual Garage Door plugin is designed to flexibly
accommodate your needs.

# 6. User Notes ##

### Travel Timer Event Timing ###

It is essential that the open/close travel time is slightly longer (~0.1-0.2
sec) than the actual time required for the door to complete a cycle. This
allows open/close events (os-on, cs-on) to occur before the timer expires
(tt-off). Premature timer expiration will cause the tracking logic to fail.
On the other side, if the travel time is too long, state changes caused
by a tt-off event will be delayed.

Interrupted cycles may cause tt-off state changes to be delayed because the
timer is restarted mid-cycle. The normal travel time is too long for the
partial movement of the door. If you find yourself waiting for an expiration
driven state change, just be patient. It will happen in a couple of seconds.

### Plugin and Opener Device Configuration ###

The Virtual Garage Door plugin is easy to configure. Notes in the configuration
user interfaces should provide all the guidance that you will need. The
following figure shows the plugin configuration GUI. It is used to select the
plugin logging level and a debug logging option.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure6.png)

The following figure shows a Virtual Garage Door opener device configuration
GUI immediately after device creation. There are no monitored devices selected.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure7.png)

This figure shows the opener device configuration GUI after all four monitored
devices have been selected.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure8.png)

This figure shows the HomeKit Accessory Server device configuration GUI with
the Virtual Garage Door opener device configured.

![](https://raw.githubusercontent.com/papamac/VirtualGarageDoor/master/files/figure9.png)

## 7. Safety Issue - Unattended Operation ##
**Unattended operation is defined as activation of the garage door opener when
the person (or software) causing the activation has no line of sight to the
door. There is an obvious physical injury or entrapment issue for any person
that may be in the garage or near/under the door during unattended
opening/closing. The US Consumer Product Safety Commission has specified a
number of requirements for unattended operation of residential garage doors.
These include flashing lights and audio alarm signals for five seconds before
the unattended activation. Details are available online at
<https://ecfr.io/Title-16/Section-1211.14>.**

**When using the Virtual Garage Door plugin with an activation relay there
is nothing to prohibit unattended operation. It is up to the user (you) to do
the right thing. YOU MAY NOT USE THIS VIRTUAL GARAGE DOOR PLUGIN FOR UNATTENDED
OPERATION AS DEFINED ABOVE. IF YOU REALLY REQUIRE UNATTENDED OPERATION YOU
SHOULD INVEST IN A NEWER DOOR OPENER THAT IS ACTIVATED VIA MOBILE PHONE AND
HAS THE REQUIRED SAFETY FEATURES BUILT IN.**
