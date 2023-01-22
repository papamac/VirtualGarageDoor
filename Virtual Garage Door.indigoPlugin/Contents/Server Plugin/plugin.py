# coding=utf-8
###############################################################################
#                                                                             #
#                           VIRTUAL GARAGE DOOR                               #
#                             MODULE plugin.py                                #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Virtual Garage Door - Monitoring and control of conventional garage
           door openers in Indigo
  MODULE:  plugin.py
   TITLE:  primary module in the Virtual Garage Door Indigo plugin bundle
FUNCTION:  Monitors multiple Indigo devices to track garage door motion
           and report the door state in the states dictionary of an opener
           device.  Provides actions to open, close and toggle the garage door.
   USAGE:  plugin.py is included in a standard Indigo plugin bundle.
  AUTHOR:  papamac
 VERSION:  1.1.1
    DATE:  January 12, 2023


UNLICENSE:

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>


DESCRIPTION:

The Virtual Garage Door (VGD) plugin monitors one or more Indigo devices to
track the garage door as it moves through its operational cycles. It saves the
door states in the states dictionary of a VGD opener device. The states are
displayed in the Indigo Home window and are available for use by scripts,
action groups, control pages, triggers, and other plugins. The VGD plugin also
provides actions to open, close and toggle the garage door.

VGD opener devices work with Apple HomeKit by using the HomeKit Bridge (HKB)
plugin or the HomeKitLink Siri (HKLS) plugin. After installation and setup of
either plugin, you can use the Apple Home application to monitor and control
your garage doors.  With any Apple device, you can also monitor and control
your doors verbally using Siri. Say "Hey Siri, check the garage door status" or
"Hey Siri, open the garage main door".

The VGD plugin can monitor a wide variety of optional devices that are already
available in Indigo as supported devices or through existing 3rd party plugins.
These include both z-wave devices and custom/wired devices. Device types
include relays, contact sensors, tilt sensors, and multisensors. Please see the
latest list of supported devices at
<https://github.com/papamac/VirtualGarageDoor/wiki/2.-Supported-Devices>.

The garage door tracking accuracy depends upon which monitored devices are
selected and the door's operational cycle. The wiki Design page (see
<https://github.com/papamac/VirtualGarageDoor/wiki/3.-Design> (Section 3.4)
contains a detailed discussion of the tracking performance under a wide range
of conditions. This allows the user to select the set of monitored devices
to best meet his specific needs.


DEPENDENCIES/LIMITATIONS:

The plugin will work only with conventional garage door openers that auto-
reverse during an obstructed closing cycle.  It will not accurately track door
state transitions in this cycle for a non-auto-reversing door.

If equipped with an activation relay, the plugin is capable of unattended
operation of the door.  Unattended operation of a residential garage door is
permitted only with accompanying audible and visible alarms. See the safety
issue discussion in the wiki Section 5.1 at
<https://github.com/papamac/VirtualGarageDoor/wiki/5.-User-Notes>.


CHANGE LOG:

Major changes to the Virtual Garage Door plugin are described in the CHANGES.md
file in the top level bundle directory.  Changes of lesser importance may be
described in individual module docstrings if appropriate.

v0.5.0  12/27/2020  Initial beta version.
v0.6.0   2/16/2021  Allow the plugin to utilize on/off state names other than
                    the usual "onOffState".  This allows the use of EasyDAQ
                    digital input/output/relay devices that include the channel
                    number in the state name, e.g., "channel01".
v0.7.0   9/ 9/2021  Eliminate the numeric door state and change it to a
                    descriptive door state.  Improve the state display in the
                    primary Indigo display.  Delete the travel timer device in
                    the deviceStopCom method to avoid the accumulation of
                    orphan timers.
v0.7.1   4/13/2022  Perform error checking for travel timer creation.  Abort
                    device startup on timer error.
v0.7.2   4/20/2022  Change the travel timer state name from the text value
                    "timerStatus" to the boolean value "timerStatus.active"
                    for symmetry in device monitoring.
v0.8.0   4/30/2022  Revise the door state transition processing to use a state
                    transition model based on the behavior of auto-reversing
                    garage door openers.  The new state transition diagram is
                    included in the plugin wiki.  The transitions are entered
                    in a DOOR_STATE_TRANSITIONS dictionary that controls a
                    table-driven state tracking algorithm.  The transitions in
                    the dictionary are numbered to cross-reference them to
                    the state transition diagram.  Also, LOG warning messages
                    for monitored device state changes that are inconsistent
                    with the new state transition model.
v0.9.0   5/31/2022  (1) Add a new monitored device called an activation sensor
                    that turns on when the garage door opener is activated.
                    Keep the openerRelay (formally actuatorRelay) only for use
                    in controlling the door.
                    (2) Add opener relay processing for activating an EasyDAQ
                    relay.
                    (3) Update for Python 3.
v0.9.2   6/13/2022  Replace the activation sensor with a new vibration sensor.
                    Change the opener relay to the activation relay and
                    recognize its role as a sensor device as well as an
                    activation control device.  Replace the full sensor names
                    with two character abbreviated names to simplify the state
                    processing code.
v0.9.3   6/30/2022  Modify the deviceStartComm and validateDeviceConfigUi
                    methods to initialize and validate the travel timer in the
                    same way as other monitored devices.  Move the timer device
                    creation from deviceStartComm to validateDeviceConfigUi and
                    use a travel timer device name based on the opener device
                    name.  Add device selection menu callback methods for all
                    monitored device types to facilitate optional device
                    selection in the opener ConfigaUi.
v0.9.4    7/2/2022  Change monitored device event names to be compatible with
                    the new wiki figures.
v0.9.5   7/10/2022  Add debug logging of monitored event sequences and
                    state updates.  Optionally log all monitored device events,
                    even if they don't result in state changes.
v0.9.6   7/20/2022  Use sleep for VS_TURNOFF instead of Indigo device delayed
                    action which is less precise.  Update README.md and the
                    wiki.
v0.9.7   7/20/2022  Update comments in plugin.py.
v1.0.0   7/22/2022  Initial GitHub release.
v1.0.1   7/23/2022  Add a user-specified vsResetDelay time to delay the
                    vibration sensor reset after the door stops. This prevents
                    false vibration sensor activations from residual shaking.
                    Permit travel time to be a floating point number.
v1.0.3   7/27/2022  Increase the maximum value of the vsResetDelay time from 2
                    to 5 seconds.
v1.0.5   8/16/2022  Add 'zwRelayType' to RELAY_DEVICE_TYPE_IDs to permit z-wave
                    relays to be used with the plugin.  Separate EasyDAQ
                    deviceTypeIds into combo, relay, and sensor groups for
                    more accurate dynamic list creation in relay and sensor
                    device selection.
v1.0.5a  8/27/2022  Improve debug reporting of the monitored device
                    configuration and the door state transition sequence.
v1.0.6    9/8/2022  Add deviceTypeIds for several new devices/plugins to make
                    them available in device selection.  Fix a bug in state
                    tracking that incorrectly equated a timer inactive event
                    (tt-off) with an expired timer.  The fix definitively
                    detects a new timer expired event (tt-exp) to simplify
                    tracking.  The old tt-off event is ignored.
v1.1.0   12/18/2022 (1) Add an integer doorState to the device states
                    dictionary to support full integration with Apple HomeKit.
                    Re-structure plugin.py around the integer doorState
                    instead of the text doorStatus.  The states are defined by:
                    OPEN, CLOSED, OPENING, CLOSING, STOPPED, REVERSING = range(6).
                    (2) Add state tracking logic for the new REVERSING
                    doorState (and "reversing" doorStatus) to detect and report
                    interrupted (obstructed) door closing.  Update the
                    transitions in the DOOR_STATE_TRANSITIONS tuple to
                    implement the new REVERSING state.  Immediately transition
                    the REVERSING state to OPENING to reflect the auto-
                    reversing behavior of the physical door.
                    (3) Improve error detection and reporting during ConfigUi
                    validation, device startup, and runtime.
                    (4) Allow the openGarageDoor action (and indigo.device.
                    turnOff) regardless of the opener onOffState.  This enables
                    recovery from obstructed door conditions using the Apple
                    HomeKit application.
v1.1.1   1/12/2023  (1) Update the wiki to document the changes introduced in
                    version v1.1.0.
                    (2) Add the DoorStateTrack class to capture and log
                    sequences of door transition sequences (tracks).
                    (3) Optionally log door state tracks in the info log per a
                    pluginPrefs checkbox.
                    (4) Restore the restriction on the openGarageDoor action
                    that was removed in v1.1.0 (4).  Restoring this restriction
                    requires that the door be closed before the open action is
                    performed.  The removal of the same restriction on the
                    device turnOff command remains to allow the HomeKit Home
                    application (via the HKB of HKLS plugin) to close the door
                    from a stopped state.
                    (5) Log warning messages if the door opening/closing
                    restrictions are violated.
                    (6) Change the validation of the vibration sensor reset
                    delay time to check for an integer between 0 and 4 seconds.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '1.1.1'
__date__ = 'January 12, 2023'

from datetime import datetime
from logging import getLogger, NOTSET
from time import sleep

import indigo

# Globals:

LOG = getLogger('Plugin')  # Standard logger.
TIMER_PLUGIN_ID = 'com.perceptiveautomation.indigoplugin.timersandpesters'
TIMER = indigo.server.getPlugin(TIMER_PLUGIN_ID)

# Monitored device types used in deviceStartComm and validateDeviceConfigUi
# methods.

MONITORED_DEVICE_TYPES = (

    'ar',  # activation relay
    'cs',  # closed sensor
    'os',  # open sensor
    'vs',  # vibration sensor
    'tt')  # travel timer

# Activation relay momentary closure time (seconds).

AR_CLOSURE_TIME = 1

# Door state enumeration, stationary state group, and door status.

# The first five door states are the same as those defined in the
# HMCharacteristicValueDoorState enumeration in the Apple developer HomeKit website:
# (https://developer.apple.com/documentation/homekit/hmcharacteristicvaluedoorstate).

OPEN, CLOSED, OPENING, CLOSING, STOPPED, REVERSING = range(6)
STATIONARY_STATES = (OPEN, CLOSED, STOPPED)
DOOR_STATUS = ('open', 'closed', 'opening', 'closing', 'stopped', 'reversing')

# Valid door state transitions tuple used by the deviceUpdated method to select
# a new door state after the occurrence of a monitored device event.  These
# transitions define the door state tracking logic for the plugin.

# newDoorState = DOOR_STATE_TRANSITIONS[doorState][mDevEvent]

DOOR_STATE_TRANSITIONS = (

    # Transitions from the OPEN state (doorState == 0):

    {'ar-on':       CLOSING,      # 12     normal closing
     'os-off':      CLOSING,      # 13     normal closing
     'vs-on':       CLOSING,      # 14     normal closing
     'cs-on':       CLOSED},      # 15     out-of-sync recovery

    # Transitions from the CLOSED state (doorState == 1):

    {'ar-on':       OPENING,      # 1      normal opening
     'cs-off':      OPENING,      # 2      normal opening
     'vs-on':       OPENING,      # 3      normal opening
     'os-on':       OPEN},        # 4      out-of-sync recovery

    # Transitions from the OPENING state (doorState == 2):

    {'os-on':       OPEN,         # 5      normal open
     'tt-exp&!os':  OPEN,         # 6      normal open if no os
     'ar-on':       STOPPED,      # 7      interrupted opening
     'tt-exp':      STOPPED,      # 8      interrupted opening
     'cs-off':      OPENING,      # 9      redundant event
     'vs-on':       OPENING,      # 10     redundant event
     'cs-on':       CLOSED},      # 11     out-of-sync recovery

    # Transitions from the CLOSING state (doorState == 3):

    {'cs-on':       CLOSED,       # 16     normal closed
     'tt-exp&!cs':  CLOSED,       # 17     normal closed if no cs
     'ar-on':       REVERSING,    # 18     interrupted closing
     'tt-exp':      REVERSING,    # 19     interrupted closing
     'os-off':      CLOSING,      # 20     redundant event
     'vs-on':       CLOSING,      # 21     redundant event
     'os-on':       OPEN},        # 22     out-of-sync recovery

    # Transitions from the STOPPED state (doorState == 4):

    {'ar-on':       CLOSING,      # 23     normal closing from stop
     'vs-on':       CLOSING,      # 24     normal closing from stop
     'cs-on':       CLOSED,       # 25     out-of-sync recovery
     'os-on':       OPEN}         # 26     out-of-sync recovery

    # Transitions from the REVERSING state (doorState == 5):

    # There are no event driven transitions from the REVERSING state.
    # REVERSING is an instantaneous state that is used to detect and report
    # interrupted (obstructed) door closing.  It is reported and then
    # immediately transitioned to OPENING to reflect the auto-reversing
    # behavior of the physical door.
)

# Sensor and relay device type id tuples used by the dynamic list callback
# methods in Plugin Part III.

easyDaqComboTypeIds =      ('easyDaq4r4io',      'easyDaq16r8io',
                            'easyDaq8ii4io4r')
easyDaqRelayTypeIds =      ('easyDaq8r',         'easyDaq24r',
                            'easyDaqDo24Stack',  'easyDaqOutputRelay')
easyDaqSensorTypeIds =     ('easyDaq24io',)

shellyDirectRelayTypeIds = ('shelly1',           'shelly1l',
                            'shelly1pm',         'shelly4pro,'
                            'shellyem',          'shellyem3')
shellyMQTTRelayTypeIds =   ('shelly-1',          'shelly-1pm',
                            'shelly-2-5-relay',  'shelly-2-5-roller',
                            'shelly-4-pro',      'shelly-em-relay',
                            'shelly-uni-relay')

genericRelayTypeIds =      ('digitalOutput',    'pseudoRelay',
                            'zwDimmerType',     'zwRelayType')
genericSensorTypeIds =     ('alarmZone',        'contactSensor',
                            'digitalInput',     'masqSensor',
                            'zwOnOffSensorType')

RELAY_DEVICE_TYPE_IDs =    (easyDaqComboTypeIds + easyDaqRelayTypeIds
                            + shellyDirectRelayTypeIds + shellyMQTTRelayTypeIds
                            + genericRelayTypeIds)

SENSOR_DEVICE_TYPE_IDs =   (easyDaqComboTypeIds + easyDaqSensorTypeIds
                            + genericSensorTypeIds)

###############################################################################
#                                                                             #
#                            CLASS DoorStateTrack                             #
#                                                                             #
###############################################################################

class DoorStateTrack:
    """
    A (virtual) door state track is a time sequence of transitions from state
    to state as the door moves through its operational cycle.  A monitored
    device event (mDevEvent) initiates a transition from the current door state
    to a new door state as determined by the global DOOR_STATE_TRANSITIONS
    tuple.  Each transition is a string of the form:

    [timeSinceLastEvent mDevEvent newDoorState], and tracks look like:
    initialState [transition 1] [transition2]...

    Each track begins in a stationary state (see globals tuple
    STATIONARY_STATES) and continues until the start of the next stationary
    state.  When a stationary state occurs, the current track is optionally
    logged and a new track started.  Optional logging is controlled by the
    logDoorStateTracks checkbox in the plugin preferences.

    Virtual state tracks are used offline to facilitate door state tracking
    analysis.  Virtual state tracks are compared with the actual physical state
    tracks to identify missing or added virtual state transitions.

    This class provides methods to initialize, update, and log door state
    tracks.  These methods are called by the deviceStartComm and deviceUpdated
    plugin methods.
    """
    def __init__(self, plugin, dev, currentDoorState):
        """
        Initialize local attributes.
        """

        self._plugin = plugin
        self._dev = dev
        self._lastEventTime = datetime.now()
        self._doorStateTrack = DOOR_STATUS[currentDoorState].upper()
        self._lastState = currentDoorState

    def update(self, mDevEvent, newDoorState):
        """
        Add the current door state transitions to an existing track.
        """

        # Compute the time since the last event.

        eventTime = datetime.now()
        dt = eventTime - self._lastEventTime
        timeSinceLastEvent = dt.total_seconds()
        if timeSinceLastEvent > 99:  # Max it out at 99 seconds.
            timeSinceLastEvent = 99
        self._lastEventTime = eventTime

        # Format a transition string in the form of [time event state] and
        # append it to the track.

        transition = ' [%.2f %s %s]' % (timeSinceLastEvent, mDevEvent,
                                        DOOR_STATUS[newDoorState].upper())
        self._doorStateTrack += transition
        self._lastState = newDoorState

    def log(self):
        """
        LOG the track if requested and initialize a new track with the last
        door state.
        """
        if self._plugin.pluginPrefs['logDoorStateTracks']:
            LOG.info('"%s" config: %s| track: %s', self._dev.name,
                     self._dev.pluginProps['mDevConfig'],
                     self._doorStateTrack)

        self._doorStateTrack = DOOR_STATUS[self._lastState].upper()


###############################################################################
#                                                                             #
#                               CLASS Plugin                                  #
#                                                                             #
###############################################################################

class Plugin(indigo.PluginBase):
    """
    The Plugin class is a collection of standard Indigo plugin methods that are
    needed to manage multiple door opener devices.  It is segmented into four
    parts for readability:

    I   STANDARD INDIGO INITILIZATION, STARTUP, AND RUN/STOP METHODS,
    II  CONFIG UI VALIDATION METHODS,
    III CONFIG UI CALLBACK METHODS, and
    IV  ACTION CALLBACK METHODS
    """

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                                   III                                   #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                   III                                   #
    #                                                                         #
    #      STANDARD INDIGO INITILIZATION, STARTUP, AND RUN/STOP METHODS       #
    #                                                                         #
    #  def __init__(self, pluginId, pluginDisplayName,                        #
    #               pluginVersion, pluginPrefs)                               #
    #  def __del__(self)                                                      #
    #  def startup(self)                                                      #
    #  def deviceStartComm(self, dev)                                         #
    #  def deviceStopComm(self, dev)                                          #
    #  def deviceUpdated(self, oldDev, newDev)                                #
    #                                                                         #
    #                           SUPPORTING METHOD                             #
    #                                                                         #
    #  def _updateDoorStates(dev, mDevEvent, doorState)                       #
    #                                                                         #
    ###########################################################################

    def __init__(self, pluginId, pluginDisplayName,
                 pluginVersion, pluginPrefs):
        """
        Define the two local dictionaries needed by plugin methods: the
        monitored devices dictionary and the door state tracks dictionary.
        Set these to empty dictionaries to be initialized later by the
        deviceStartComm method.

        The monitored devices dictionary is a compound dictionary that stores
        the device id's and properties of devices that are monitored by the
        plugin.  It has the following structure:

        self._monitoredDevices = {devId: {mDevId: {mDevState: mDevType}}}
        where:
           devId     is the device id of the opener device.
           mDevId    is the device id of a timer, sensor, or relay device to be
                     monitored by the opener plugin to track the garage
                     door state.  All monitored devices must have an on/off
                     bool state defined in the devices xml by
                     <ValueType boolType="OnOff">Boolean</ValueType>.
           mDevState is the on/off state name to be monitored by the plugin.
                     For most sensor devices it is typically "onOffState".  For
                     EasyDAQ devices it is "channelnn" where nn is the
                     numeric channel number.  For timers the state name is
                     "timerStatus.active".
           mDevType  is the type of the monitored device that allows the
                     plugin to interpret state changes. Types are "ar"
                     (activation relay), "cs" (closed sensor), "os" (open
                     sensor), "vs" (vibration sensor), and "tt" (travel timer).

        The door state tracks dictionary stores a single DoorStateTrack
        instance object for each plugin opener device.  It has the following
        structure:

        self._doorStateTracks = {devId: track}
        where:
            devId   is the device id of the opener device.
            track   is an instance object of the DoorStateTrack class
                    (see above).
        """
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        self._monitoredDevices = {}  # Monitored device properties by devId.
        self._doorStateTracks = {}   # Door state track objects by devId.

    def __del__(self):
        """
        Delete the Plugin instance object.
        """
        LOG.threaddebug('Plugin.__del__ called')
        indigo.PluginBase.__del__(self)

    @staticmethod
    def _updateDoorStates(dev, doorState):
        """
        Update the door states on the Indigo server for use by the Home window,
        scripts, action groups, control pages, triggers, and other plugins.

        The door states include the doorState, doorStatus and the onOffState.
        The doorState can be OPEN, CLOSED, OPENING, CLOSING, STOPPED, and
        REVERSING (see enumeration in globals).  The doorStatus is a lower case
        string representation of the doorState, and the onOffState is on if the
        doorState is CLOSED and off otherwise.

        Also, set state image on the Indigo Home window based on the value of
        the onOffState.  Select a green dot if the onOffState is on (doorState
        is CLOSED) and a red dot if it is off.
        """
        onOffState = doorState is CLOSED
        doorStatus = DOOR_STATUS[doorState]
        dev.updateStateOnServer('onOffState', onOffState, uiValue=doorStatus)
        image = (indigo.kStateImageSel.SensorOn if onOffState
                 else indigo.kStateImageSel.SensorTripped)
        dev.updateStateImageOnServer(image)
        dev.updateStateOnServer('doorStatus', doorStatus)
        dev.updateStateOnServer('doorState', doorState)
        LOG.info('"%s" update to %s', dev.name, doorStatus.upper())

    def startup(self):
        """
        Setup THREADDEBUG logging and subscribe to device state changes.
        """
        self.indigo_log_handler.setLevel(NOTSET)
        level = self.pluginPrefs['loggingLevel']
        LOG.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        LOG.threaddebug('Plugin.startup called')
        LOG.debug(self.pluginPrefs)
        indigo.devices.subscribeToChanges()

    def deviceStartComm(self, dev):
        """
        Initialize door opener devices.
        """
        LOG.threaddebug('Plugin.deviceStartComm called "%s"', dev.name)

        # Create a new monitored devices dictionary entry for this opener
        # device.

        devId = dev.id
        self._monitoredDevices[devId] = {}

        # Add all monitored devices that are selected in the opener device
        # ConfigUi to the monitored devices dictionary.  Save the initial
        # states of the devices for use in setting the initial device opener
        # state.

        errors = False
        states = {}
        for mDevType in MONITORED_DEVICE_TYPES:
            mDevName = dev.pluginProps.get(mDevType)
            if mDevName:  # Monitored device is selected in the ConfigUi.

                # Check the device and state names.

                mDev = indigo.devices.get(mDevName)
                if not mDev:
                    LOG.error('"%s" not in devices dictionary', mDevName)
                    errors = True
                    continue
                mDevStateKey = mDevType + 'State'
                mDevState = dev.pluginProps[mDevStateKey]
                if mDevState not in mDev.states:
                    LOG.error('"%s" state %s not in states dictionary',
                              mDevName, mDevState)
                    errors = True
                    continue

                # Add a new entry in the monitored devices dictionary.

                mDevId = mDev.id
                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevState] = mDevType

                # Get the normalized state of the device.

                invert = dev.pluginProps.get(mDevType + 'Invert', False)
                states[mDevType] = mDev.states[mDevState] ^ invert

        LOG.debug(self._monitoredDevices[devId])
        LOG.debug(states)

        if errors:  # Abort deviceStartComm if there were errors.
            self.deviceStopComm(dev)
            LOG.error('"%s" init error(s): check/run ConfigUi', dev.name)
            dev.setErrorStateOnServer('init err')  # Set error state.
            return

        # Initialize the opener device state and door state track.  Assume that
        # door is not in motion and that it is closed unless the closedSensor
        # is off and openSensor is on.

        csState = states.get('cs')
        osState = states.get('os')
        doorState = OPEN if not csState and osState else CLOSED
        self._doorStateTracks[devId] = DoorStateTrack(self, dev, doorState)
        if doorState != dev.states.get('doorState'):
            self._updateDoorStates(dev, doorState)

        # Clear error state, if any.

        dev.setErrorStateOnServer(None)

    def deviceStopComm(self, dev):
        """
        Retire door opener devices.
        """
        LOG.threaddebug('Plugin.deviceStopComm called "%s"', dev.name)

        # Delete the entry in the monitored devices dictionary, if present.

        if dev.id in self._monitoredDevices:
            del self._monitoredDevices[dev.id]

    def deviceUpdated(self, oldDev, newDev):
        """
        Monitor device state changes (events) and update the opener device
        states in response.
        """
        indigo.PluginBase.deviceUpdated(self, oldDev, newDev)
        errorDevices = []
        for devId in self._monitoredDevices:
            if oldDev.id in self._monitoredDevices[devId]:
                dev = indigo.devices[devId]
                mDevId = oldDev.id
                for mDevState in self._monitoredDevices[devId][mDevId]:

                    # Get the onOffStates for both the old (unchanged) device
                    # object and the new (updated) device object.  Invert the
                    # states if specified in the pluginProps.  Ignore the
                    # device object update if the onOffState is unchanged.

                    mDevType = (self._monitoredDevices
                                [devId][mDevId][mDevState])
                    invert = dev.pluginProps.get(mDevType + 'Invert', False)
                    oldState = oldDev.states[mDevState] ^ invert
                    newState = newDev.states[mDevState] ^ invert
                    if oldState == newState:
                        continue

                    doorState = dev.states['doorState']

                    # Create monitored device event name and optionally log it.

                    mDevEvent = mDevType + ('-off', '-on')[newState]
                    if self.pluginPrefs['logMonitoredDeviceEvents']:
                        LOG.debug('"%s" %s', dev.name, mDevEvent)

                    # Check for expired timer.

                    if mDevEvent == 'tt-off':  # Timer is inactive.
                        if newDev.states['timeLeftSeconds'] == '0':
                            mDevEvent = 'tt-exp'  # Timer has expired.

                            # Add qualifiers for travel timer expired events
                            # that have different meanings during opening and
                            # closing.

                            if doorState is OPENING:
                                os = dev.pluginProps.get('os')
                                mDevEvent += '&!os' if not os else ''
                            elif doorState is CLOSING:
                                cs = dev.pluginProps.get('cs')
                                mDevEvent += '&!cs' if not cs else ''

                            # Optionally log timer expired events.

                            if self.pluginPrefs['logMonitoredDeviceEvents']:
                                LOG.debug('"%s" %s', dev.name, mDevEvent)

                    # Ignore events that can't affect the door state.

                    if mDevEvent in ('ar-off', 'vs-off', 'tt-on', 'tt-off'):
                        continue

                    # Get the new door state from the DOOR_STATE_TRANSITIONS
                    # dictionary as a function of the current door state and
                    # the monitored device event.

                    try:
                        newDoorState = (DOOR_STATE_TRANSITIONS
                                        [doorState][mDevEvent])
                    except KeyError:  # Ignore event if no legal transition.
                        LOG.warning('"%s" mDevEvent %s is inconsistent '
                                    'with door state %s', dev.name, mDevEvent,
                                    DOOR_STATUS[doorState].upper())
                        continue

                    self._doorStateTracks[devId].update(mDevEvent,
                                                        newDoorState)

                    if newDoorState != doorState:  # Door state has changed.

                        self._updateDoorStates(dev, newDoorState)

                        # If the new door state is REVERSING, immediately
                        # transition to OPENING and update the door states
                        # and tracks again.

                        if newDoorState is REVERSING:
                            newDoorState = OPENING
                            self._doorStateTracks[devId].update('null',
                                                                newDoorState)
                            self._updateDoorStates(dev, newDoorState)

                        # Perform new state actions.

                        try:
                            ttDevId = int(dev.pluginProps['ttDevId'])
                            if newDoorState in STATIONARY_STATES:

                                # Log/reset the existing state track, stop
                                # the timer, and reset the vibration sensor.

                                self._doorStateTracks[devId].log()

                                TIMER.executeAction('stopTimer',
                                                    deviceId=ttDevId)

                                vsDevIdStr = dev.pluginProps['vsDevId']
                                if vsDevIdStr:
                                    vsDevId = int(vsDevIdStr)
                                    vsResetDelay = int(round(float(
                                        dev.pluginProps['vsResetDelay'])))
                                    indigo.device.turnOff(vsDevId,
                                                          delay=vsResetDelay)

                            else:  # Door is moving; restart the timer.
                                TIMER.executeAction('restartTimer',
                                                    deviceId=ttDevId)

                        except Exception as errorMessage:  # tt or vs error.
                            LOG.error('"%s" run error: %s; check/run ConfigUi',
                                      dev.name, errorMessage)
                            dev.setErrorStateOnServer('run err')  # Set error.
                            errorDevices.append(dev)  # Update error devices.
                            break  # Break from inner mDevState loop.

        # Stop devices with run errors.

        map(self.deviceStopComm, errorDevices)

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                                III   III                                #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                III   III                                #
    #                                                                         #
    #                      CONFIG UI VALIDATION METHODS                       #
    #                                                                         #
    #  def validatePrefsConfigUi(valuesDict)                                  #
    #  def validateDeviceConfigUi(self, valuesDict, typeId, devId)            #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def validatePrefsConfigUi(valuesDict):
        """
        Set the THREADDEBUG logging level if the user changes the pluginPrefs
        after startup.
        """
        LOG.threaddebug('Plugin.validatePrefsConfigUi called')
        level = valuesDict['loggingLevel']
        LOG.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        return True

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        """
        Validate the GUI travel time.  If a timer device already exists for the
        opener device, then configure the timer.  If not, create a new timer.

        Validate monitored device GUI entries and create the monitored device
        dictionary.

        Set the initial opener device state based on the states
        of the open and closed sensors.
        """
        dev = indigo.devices[devId]
        devName = 'devId%s' % devId if dev.name == 'new device' else dev.name
        LOG.threaddebug('Plugin.validateDeviceConfigUi called "%s"', devName)
        LOG.debug(valuesDict)
        errors = indigo.Dict()

        # Validate open/close travel time entry.

        tTime = 0  # Force an error if try fails.
        try:
            tTime = float(valuesDict['tTime'])
        except ValueError:
            pass
        if not 8 <= tTime <= 20:
            error = 'Travel time must be a number between 8 and 20 seconds'
            errors['tTime'] = error
            return False, valuesDict, errors

        # Configure the timer.

        props = dict(amount=tTime, amountType='seconds')
        name = devName[:-7] if devName.endswith('-opener') else devName
        tt = name + '-travelTimer'
        valuesDict['tt'] = tt
        ttDev = indigo.devices.get(tt)

        try:
            if ttDev:  # Device exists, set the travel time.
                ttDevId = ttDev.id
                TIMER.executeAction('setTimerStartValue', deviceId=ttDevId,
                                    props=props)
            else:  # Create a new timer device.
                description = 'Automatically generated timer for "%s"' % devName
                indigo.device.create(protocol=indigo.kProtocol.Plugin,
                                     name=tt,
                                     description=description,
                                     pluginId=TIMER_PLUGIN_ID,
                                     deviceTypeId='timer',
                                     props=props,
                                     folder='doors')
                LOG.info('"%s" new timer device created', tt)
        except Exception as errorMessage:
            error = '"%s" travel timer init failed: %s' % (tt, errorMessage)
            valuesDict['tTime'] = error
            return False, valuesDict, errors

        # Clear self._monitoredDevices for this opener to prevent previous
        # device configurations from generating ConfigUi errors.

        self._monitoredDevices[devId] = {}

        # Validate all monitored devices that are selected in the opener device
        # ConfigUi.  Ensure that selected device name/state pairs are unique
        # for all monitored device types in all opener devices.  Set the device
        # id fields in the values dictionary.

        mDevConfig = ''
        for mDevType in MONITORED_DEVICE_TYPES:
            valuesDict[mDevType + 'DevId'] = ''
            mDevName = valuesDict.get(mDevType)
            if mDevName:  # Monitored device is selected in the ConfigUi.

                # Validate the device name.

                mDev = indigo.devices.get(mDevName)
                if not mDev:
                    error = '%s not in the devices dictionary' % mDevName
                    errors[mDevType] = error
                    continue

                # Validate the state name.

                mDevStateKey = mDevType + 'State'
                mDevState = valuesDict[mDevStateKey]
                if mDevState not in mDev.states:
                    error = '%s not in device states dictionary' % mDevState
                    errors[mDevStateKey] = error
                    continue

                # Check to ensure that no device/state pairs are reused by this
                # opener device or others.

                mDevId = mDev.id
                for devId_ in self._monitoredDevices:
                    for mDevId_ in self._monitoredDevices[devId_]:
                        for mDevState_ in (self._monitoredDevices[devId_]
                                           [mDevId_]):
                            if mDevId == mDevId_ and mDevState == mDevState_:
                                error = 'Device/state name already in use'
                                errors[mDevType] = error
                                errors[mDevStateKey] = error
                                continue

                # Validate the vs reset delay time.

                if mDevType == 'vs':
                    vsResetDelay = -1  # Force an error if the try fails.
                    try:
                        vsResetDelay = int(valuesDict['vsResetDelay'])
                    except ValueError:
                        pass
                    if not 0 <= vsResetDelay <= 4:
                        error = ('Reset delay time must be an integer between '
                                 '0 and 4 seconds')
                        errors['vsResetDelay'] = error
                        continue

                # No error for this monitored device/state; update derived
                # values in the values dictionary.

                valuesDict[mDevType + 'DevId'] = mDevId
                mDevConfig += mDevType + ' '
                valuesDict['mDevConfig'] = mDevConfig

                # Add keys/values to self._monitoredDevices to mark this
                # device/state combination as used.  Note that these additions
                # are overwritten (with the same data) when the opener device
                # is initialized by the deviceStartComm method.

                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevState] = mDevType
                LOG.debug(self._monitoredDevices[devId])

        # Return with or without errors.

        return not bool(errors), valuesDict, errors

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III   III                             #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                             III   III   III                             #
    #                                                                         #
    #                      CONFIG UI CALLBACK METHODS                         #
    #                                                                         #
    #  def getSensorDeviceList(*args)                                         #
    #  def getRelayDeviceList(*args)                                          #
    #  def setCsConfig(valuesDict, typeId, devId)                             #
    #  def setOsConfig(valuesDict, typeId, devId)                             #
    #  def setVsConfig(valuesDict, typeId, devId)                             #
    #  def setArConfig(valuesDict, typeId, devId)                             #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def getSensorDeviceList(*args):
        """
        Return a list of sensor device names for the cs, os, and vs device
        selection menus in the opener device ConfigUi.

        List all indigo devices with a deviceTypeIds in SENSOR_DEVICE_TYPE_IDs.
        Also include a "none" element to enable the removal of an existing
        selection.
        """
        LOG.threaddebug('Plugin.getSSensorDeviceList called')
        sensors = []
        for dev in indigo.devices:
            if dev.deviceTypeId in SENSOR_DEVICE_TYPE_IDs:
                sensors.append(dev.name)
        return ['none'] + sorted(sensors)

    @staticmethod
    def getRelayDeviceList(*args):
        """
        Return a list of relay device names for the ar device selection menu
        in the opener device ConfigUi.

        List all indigo devices with a deviceTypeIds in RELAY_DEVICE_TYPE_IDs.
        Also include a "none" element to enable the removal of an existing
        selection.
        """
        LOG.threaddebug('Plugin.getRelayDeviceList called')
        relays = []
        for dev in indigo.devices:
            if dev.deviceTypeId in RELAY_DEVICE_TYPE_IDs:
                relays.append(dev.name)
        return ['none'] + sorted(relays)

    @staticmethod
    def setCsConfig(valuesDict, typeId, devId):
        """
        Respond to a user selection from the closed sensor (cs) device
        selection menu in the opener device ConfigUi.

        Set the cs device name to the null string if no device was selected.
        Set the csConfig hidden checkbox to control the visibility of the
        remaining cs fields based on the device name selection.
        """
        LOG.threaddebug('Plugin.setCsConfig called')
        cs = '' if valuesDict['cs'] == 'none' else valuesDict['cs']
        valuesDict['cs'] = cs
        valuesDict['csConfig'] = 'true' if cs else 'false'
        return valuesDict

    @staticmethod
    def setOsConfig(valuesDict, typeId, devId):
        """
        Respond to a user selection from the open sensor (os) device selection
        menu in the opener device ConfigUi.

        Set the os device name to the null string if no device was selected.
        Set the osConfig hidden checkbox to control the visibility of the
        remaining os fields based on the device name selection.
        """
        LOG.threaddebug('Plugin.setOsConfig called')
        os = '' if valuesDict['os'] == 'none' else valuesDict['os']
        valuesDict['os'] = os
        valuesDict['osConfig'] = 'true' if os else 'false'
        return valuesDict

    @staticmethod
    def setVsConfig(valuesDict, typeId, devId):
        """
        Respond to a user selection from the vibration sensor (vs) device
        selection menu in the opener device ConfigUi.

        Set the vs device name to the null string if no device was selected.
        Set the vsConfig hidden checkbox to control the visibility of the
        remaining vs fields based on the device name selection.
        """
        LOG.threaddebug('Plugin.setVsConfig called')
        vs = '' if valuesDict['vs'] == 'none' else valuesDict['vs']
        valuesDict['vs'] = vs
        valuesDict['vsConfig'] = 'true' if vs else 'false'
        return valuesDict

    @staticmethod
    def setArConfig(valuesDict, typeId, devId):
        """
        Respond to a user selection from the activation relay (ar) device
        selection menu in the opener device ConfigUi.

        Set the ar device name to the null string if no device was selected.
        Set the arConfig hidden checkbox to control the visibility of the
        remaining ar fields based on the device name selection.
        """
        LOG.threaddebug('Plugin.setArConfig called')
        ar = '' if valuesDict['ar'] == 'none' else valuesDict['ar']
        valuesDict['ar'] = ar
        valuesDict['arConfig'] = 'true' if ar else 'false'
        return valuesDict

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III      III                          #
    #                              I     I       I                            #
    #                              I      I     I                             #
    #                              I       I   I                              #
    #                              I        I I                               #
    #                             III       III                               #
    #                                                                         #
    #                         ACTION CALLBACK METHODS                         #
    #                                                                         #
    # def _toggleActivationRelay(dev)                                         #
    # def closeGarageDoor(self, pluginAction)                                 #
    # def openGarageDoor(self, pluginAction)                                  #
    # def toggleGarageDoor(self, pluginAction)                                #
    # def actionControlDevice(self, action, dev)                              #
    # def actionControlUniversal(action, dev)                                 #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def _toggleActivationRelay(dev):
        """
        Turn on the activation relay for a period equal to the global
        AR_CLOSURE_TIME.  Use special plugin actions for EasyDAQ relay devices;
        otherwise use the standard Indigo device turnOn method.
        """
        LOG.threaddebug('Plugin._toggleActivationRelay called "%s"', dev.name)
        ar = dev.pluginProps.get('ar')
        if ar:
            arDev = indigo.devices[ar]
            if arDev.deviceTypeId.startswith('easyDaq'):  # EasyDAQ relay.
                plugin = indigo.server.getPlugin(arDev.pluginId)
                props = dict(channelSel=int(dev.pluginProps['arState'][8:9]))
                plugin.executeAction('turnOnOutput', deviceId=arDev.id,
                                     props=props)
                sleep(AR_CLOSURE_TIME)
                plugin.executeAction('turnOffOutput', deviceId=arDev.id,
                                     props=props)
            else:  # Standalone relay device.
                indigo.device.turnOn(ar, duration=AR_CLOSURE_TIME)
        else:
            error = 'no activation relay specified; door action ignored.'
            LOG.warning('"%s" %s', dev.name, error)

    def closeGarageDoor(self, pluginAction):
        """
        Toggle the activation relay to close the garage door if it is not
        already closed.  This prevents the inadvertent opening of the door with
        a close command.
        """
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug('Plugin.closeGarageDoor called "%s"', dev.name)
        if not dev.states['onOffState']:
            self._toggleActivationRelay(dev)
        else:
            error = ('attempt to toggle the garage door closed when it is '
                     'already closed; door action ignored.')
            LOG.warning('"%s" %s', dev.name, error)

    def openGarageDoor(self, pluginAction):
        """
        Toggle the activation relay to open the garage door if it is closed.
        This prevents the inadvertent closing of the door with an open command.
        """
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug('Plugin.openGarageDoor called "%s"', dev.name)
        if dev.states['onOffState']:
            self._toggleActivationRelay(dev)
        else:
            error = ('attempt to toggle the garage door open when it is '
                     'not closed; door action ignored.')
            LOG.warning('"%s" %s', dev.name, error)

    def toggleGarageDoor(self, pluginAction):
        """
        Toggle the activation relay with no state conditions.
        """
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug('Plugin.toggleGarageDoor called "%s"', dev.name)
        self._toggleActivationRelay(dev)

    def actionControlDevice(self, action, dev):
        """
        Implement the device turnOn (close), turnOff (open) and toggle commands
        by selectively toggling the activation relay.  Allow the turnOn (close)
        activation only if the door is not already closed. This prevents the
        inadvertent opening of the door with a close command.  Do not restrict
        activation for the turnOn (close) or toggle commands.  The previous
        turnOn restriction was removed to allow the HomeKit Home application
        (via the HKB of HKLS plugin) to close the door from a stopped state.
        """
        LOG.threaddebug('Plugin.actionControlDevice called "%s"', dev.name)
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            if not dev.states['onOffState']:  # Close if not already closed.
                self._toggleActivationRelay(dev)
            else:
                error = ('attempt to toggle the garage door open when it is '
                         'not closed; door action ignored.')
                LOG.warning('"%s" %s', dev.name, error)
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            self._toggleActivationRelay(dev)  # Allow opening anytime.
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            self._toggleActivationRelay(dev)

    def actionControlUniversal(self, action, dev):
        """
        Implement the requestStatus command by logging the current door state.
        """
        LOG.threaddebug('Plugin.actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            LOG.info('"%s" is %s', dev.name, dev.states['doorStatus'].upper())
