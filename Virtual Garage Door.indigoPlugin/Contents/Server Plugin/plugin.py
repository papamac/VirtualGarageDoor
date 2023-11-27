# coding=utf-8
"""
###############################################################################
#                                                                             #
#                      Virtual Garage Door Indigo Plugin                      #
#                              MODULE plugin.py                               #
#                                                                             #
###############################################################################

  BUNDLE:  Monitoring and control of conventional garage door openers in Indigo
           (Virtual Garage Door.indigoPlugin)
  MODULE:  plugin.py
   TITLE:  Main Python module in the Virtual Garage Door.indigoPlugin bundle
FUNCTION:  plugin.py defines the Plugin class, with standard methods that
           interface to the Indigo server and manage Indigo device objects.
   USAGE:  plugin.py is included in the Virtual Garage Door.indigoPlugin bundle
           and its methods are called by the Indigo server.
  AUTHOR:  papamac
 VERSION:  1.2.4
    DATE:  November 27, 2023

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

VIRTUAL GARAGE DOOR PLUGIN BUNDLE DESCRIPTION:

The Virtual Garage Door (VGD) plugin monitors one or more Indigo devices to
track the garage door as it moves through its operational cycles. It saves the
door states in the states dictionary of a VGD opener device. The states are
displayed in the Indigo Home window and are available for use by scripts,
action groups, control pages, triggers, and other plugins. The VGD plugin also
provides actions to open, close and toggle the garage door.

The VGD plugin bundle has two primary Python modules/classes: this module,
plugin.py, encapsulates the Indigo device behavior in the Plugin class, and
virtualGarageDoor.py encapsulates detailed door behavior in the
VirtualGarageDoor class.  A VirtualGarageDoor instance is created for each VGD
device defined by plugin.py.  The plugin bundle also includes several xml
files that define Indigo GUIs and actions.

MODULE plugin.py DESCRIPTION:

plugin.py defines the Plugin class whose methods provide entry points into the
plugin from the Indigo Plugin Host.  These methods, with access to the Indigo
server's object database, manage the definition, validation, instantiation, and
concurrent execution of VGD device objects.  Plugin methods instantiate a
VirtualGarageDoor object for each VGD device and invoke the VirtualGarageDoor
update method to perform detailed device functions.

DEPENDENCIES/LIMITATIONS:

The VGD plugin will work only with conventional garage door openers that auto-
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
                    the state transition diagram.  Also, log warning messages
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
v0.9.5   7/10/2022  Add debug logging of monitored device event event sequences
                    and state updates.  Optionally log all monitored device
                    events, even if they don't result in state changes.
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
v1.1.1   1/22/2023  (1) Update the wiki to document the changes introduced in
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
v1.1.2   1/29/2023  Fix "key not found in dictionary" initialization error.
v1.1.3   3/19/2023  Change the logger global name from "LOG" to "L".
v1.1.4   7/26/2023  Add the pseudoRelay device type id to the
                    genericSensorTypeIds.  This will allow Indigo virtual
                    devices to be used as VGD sensor devices.
v1.1.5   8/21/2023  (1) Ignore multiple consecutive reports for the same
                    monitored device event within a 1 second time interval.
                    (2) Eliminate the logMonitoredDeviceEvents
                    checkbox in the pluginPrefs ConfigUi.  These events should
                    always be logged in the debug logging level.
v1.2.0   9/24/2023  (1) Divide the Plugin class into two classes: Plugin which
                    encapsulates the Indigo device behavior and
                    VirtualGarageDoor which encapsulates the detailed door
                    behavior.  The VirtualGarageDoor class has instances for
                    each VGD plugin device.
                    (2) Move startup functions from the startup method into the
                    __init__ method.  Remove the startup method override and
                    use the superclass method.
                    (3) Remove the do nothing __del__ method and use the
                    superclass method.
                    (4) Use monitored device ids to initialize opener devices
                    instead of the monitored device names.  This allows
                    monitored devices to be renamed if desired without
                    reconfiguring.
                    (5) Consolidate multiple ConfigUi callback methods (one for
                    each monitored device type) into a single method
                    (setMDevConfig) that works for all types.
                    (6) Add method docstrings for most methods.
v1.2.1   10/8/2023  Move the thread debug logging setup from the __init__
                    method back to the startup method.  Apparently, pluginPrefs
                    are not copied from the xml file prior to calling __init__,
                    causing a key error when starting the plugin for the first
                    time. This change should fix the error.
v1.2.2  11/10/2023  The bug fix in v1.2.1 doesn't work. It erroneously assumes
                    that the Indigo server initializes the pluginPrefs
                    directly from the PluginConfig.xml file. It does not; it
                    loads pluginPrefs from a different preferences file written
                    by a prior plugin execution. For a true first time
                    execution (with no prior file), the pluginPrefs are still
                    not initialized properly.  The replacement fix in this
                    version assigns a default INFO logging level in pluginPrefs
                    when there is no prior file.  It then sets the logging
                    level with this default value in the __init__ method.
v1.2.3  11/12/2023  Correct a minor omission in v1.2.2 that adds an incorrect
                    note in the PluginConfig GUI.
v1.2.4  11/27/2023  (1) Correct a bug that causes messages from class
                    VirtualGarageDoor to refer to an old opener door name if
                    the name was changed by the user after initilization.
                    (2) Improve the travel timer device management process.
                    Standardize travel timer device names and restore them
                    if they are changed.

###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################
"""
__author__ = 'papamac'
__version__ = '1.2.4'
__date__ = 'November 27, 2023'

import indigo

from logging import getLogger, NOTSET
from time import sleep

from virtualGarageDoor import VirtualGarageDoor

L = getLogger('Plugin')  # Standard Plugin logger.


###############################################################################
#                                                                             #
#                               CLASS Plugin                                  #
#                                                                             #
###############################################################################

class Plugin(indigo.PluginBase):
    """
    The Plugin class is a collection of standard Indigo plugin methods that are
    needed to manage and run multiple door opener devices.  It is segmented
    into four parts for readability:

    I   STANDARD INDIGO INITIALIZATION, STARTUP, AND RUN/STOP METHODS,
    II  CONFIG UI VALIDATION METHODS,
    III CONFIG UI CALLBACK METHODS, and
    IV  ACTION CALLBACK METHODS
    """

    # Class constants:

    AR_CLOSURE_TIME = 1  # Activation relay momentary closure time (seconds).
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

    # Sensor and relay device type id tuples used by the dynamic list callback
    # methods in Plugin Part III.

    easyDaqComboTypeIds = ('easyDaq4r4io', 'easyDaq16r8io',
                           'easyDaq8ii4io4r')
    easyDaqRelayTypeIds = ('easyDaq8r', 'easyDaq24r',
                           'easyDaqDo24Stack', 'easyDaqOutputRelay')
    easyDaqSensorTypeIds = ('easyDaq24io',)

    shellyDirectRelayTypeIds = ('shelly1', 'shelly1l',
                                'shelly1pm', 'shelly4pro,'
                                             'shellyem', 'shellyem3')
    shellyMQTTRelayTypeIds = ('shelly-1', 'shelly-1pm',
                              'shelly-2-5-relay', 'shelly-2-5-roller',
                              'shelly-4-pro', 'shelly-em-relay',
                              'shelly-uni-relay')

    genericRelayTypeIds = ('digitalOutput', 'pseudoRelay',
                           'zwDimmerType', 'zwRelayType')
    genericSensorTypeIds = ('alarmZone', 'contactSensor',
                            'digitalInput', 'masqSensor',
                            'pseudoRelay', 'zwOnOffSensorType')

    RELAY_DEVICE_TYPE_IDs = (easyDaqComboTypeIds + easyDaqRelayTypeIds
                             + shellyDirectRelayTypeIds + shellyMQTTRelayTypeIds
                             + genericRelayTypeIds)

    SENSOR_DEVICE_TYPE_IDs = (easyDaqComboTypeIds + easyDaqSensorTypeIds
                              + genericSensorTypeIds)

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
    #  def didDeviceCommPropertyChange(oldDev, newDev)                        #
    #  def deviceStartComm(self, dev)                                         #
    #  def deviceStopComm(self, dev)                                          #
    #  def deviceUpdated(self, oldDev, newDev)                                #
    #                                                                         #
    ###########################################################################

    def __init__(self, pluginId, pluginDisplayName,
                 pluginVersion, pluginPrefs):
        """
        Define the two local dictionaries needed by plugin methods: the
        monitored devices dictionary and the door state tracks dictionary.
        Set these to empty dictionaries to be initialized later by the
        deviceStartComm method.  Set the logging level and subscribe to device
        changes.
        """
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        # The monitored devices dictionary is a compound dictionary that stores
        # the device id's and properties of devices that are monitored by the
        # plugin.  It has the following structure:
        #
        # self._monitoredDevices = {devId: {mDevId: {mDevState: mDevType}}}
        # where:
        #   devId     is the device id of the opener device.
        #   mDevId    is the device id of a timer, sensor, or relay device to
        #             be monitored by the opener plugin to track the garage
        #             door state.  All monitored devices must have an on/off
        #             bool state defined in the devices xml by
        #             <ValueType boolType="OnOff">Boolean</ValueType>.
        #   mDevState is the on/off state name to be monitored by the plugin.
        #             For most sensor devices it is typically "onOffState".
        #             For EasyDAQ devices it is "channelnn" where nn is the
        #             numeric channel number.  For timers the state name is
        #             "timerStatus.active".
        #   mDevType  is the type of the monitored device that allows the
        #             plugin to interpret state changes. Types are "ar"
        #             (activation relay), "cs" (closed sensor), "os"
        #             (open sensor), "vs" (vibration sensor), and "tt"
        #             (travel timer).

        self._monitoredDevices = {}

        # The virtual garage doors dictionary saves a VirtualGarageDoor
        #             instance object for each plugin opener device.  It has
        #             the following structure:
        #
        # self._virtualGarageDoors = {devId: vgd}
        # where:
        #   devId    is the device id of the opener device.
        #   vgd      is an instance object of the VirtualGarageDoor class in
        #            the virtualGarageDoor module.

        self._virtualGarageDoors = {}

        # Set logging level and subscribe to device state changes.

        self.indigo_log_handler.setLevel(NOTSET)  # Eliminate handler level.
        level = pluginPrefs.get('loggingLevel', 'INFO')
        L.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        L.threaddebug('__init__ called')
        L.debug(pluginPrefs)
        indigo.devices.subscribeToChanges()

    @staticmethod
    def didDeviceCommPropertyChange(oldDev, newDev):
        """
        By default, changing a device's plugin properties causes the Indigo
        server to stop the device and then restart it.  This method forces a
        stop/restart when either the pluginProps or the device name changes.
        Stopping/restarting on a name change avoids complications in the
        virtualGarageDoor VirtualGarageDoor class which uses the device name at
        the time of initialization.
        """
        devChanged = (oldDev.pluginProps != newDev.pluginProps
                      or oldDev.name != newDev.name)
        return devChanged

    def deviceStartComm(self, dev):
        """
        Initialize door opener devices.  For each opener device, create a new
        monitored devices dictionary entry and a new virtual garage door
        instance.
        """
        L.threaddebug('deviceStartComm called "%s"', dev.name)

        # Create a new monitored devices dictionary entry for this opener
        # device.

        devId = dev.id
        self._monitoredDevices[devId] = {}

        # Add all monitored devices that are selected in the opener device
        # ConfigUi to the monitored devices dictionary.  Save the initial
        # states of the devices for use in setting the initial device opener
        # state.

        errors = False
        mDevStates = {}  # Initial states of monitored devices by device type.
        for mDevType in self.MONITORED_DEVICE_TYPES:
            mDevId = dev.pluginProps[mDevType + 'DevId']
            if mDevId:  # Monitored device is selected in the ConfigUi.
                mDevId = int(mDevId)

                # Check the device and state names.

                mDev = indigo.devices.get(mDevId)
                if not mDev:
                    L.error('"%s" mDevId %s is not in devices dictionary',
                            dev.name, mDevId)
                    errors = True
                    continue
                mDevStateName = dev.pluginProps[mDevType + 'State']
                if mDevStateName not in mDev.states:
                    L.error('"%s" "%s" state %s is not in states dictionary',
                            dev.name, mDev.name, mDevStateName)
                    errors = True
                    continue

                # Add a new entry in the monitored devices dictionary.

                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevStateName] = mDevType

                # Get the normalized state of the monitored device.

                invert = dev.pluginProps.get(mDevType + 'Invert', False)
                mDevStates[mDevType] = mDev.states[mDevStateName] ^ invert

        L.debug(self._monitoredDevices[devId])
        L.debug(mDevStates)

        if errors:  # Abort deviceStartComm if there were errors.
            self.deviceStopComm(dev)
            L.error('"%s" init error(s): check/run ConfigUi', dev.name)
            dev.setErrorStateOnServer('init err')  # Set error state.

        else:  # No errors.

            # Instantiate a VirtualGarageDoor object for the device and clear
            # the error state on the server, if any.

            vgd = VirtualGarageDoor(self, dev, mDevStates)
            self._virtualGarageDoors[devId] = vgd
            dev.setErrorStateOnServer(None)

    def deviceStopComm(self, dev):
        """ Retire door opener devices. """
        L.threaddebug('deviceStopComm called "%s"', dev.name)

        # Delete the entries in the monitored devices dictionary and the
        # virtual garage doors dictionary, if present.

        if dev.id in self._monitoredDevices:
            del self._monitoredDevices[dev.id]
        if dev.id in self._virtualGarageDoors:
            del self._virtualGarageDoors[dev.id]

    def deviceUpdated(self, oldDev, newDev):
        """
        Detect monitored device state changes (events) and update the virtual
        garage door using the events.
        """
        indigo.PluginBase.deviceUpdated(self, oldDev, newDev)
        for devId in self._monitoredDevices:
            if oldDev.id in self._monitoredDevices[devId]:
                dev = indigo.devices[devId]
                mDevId = oldDev.id
                for mDevState in self._monitoredDevices[devId][mDevId]:

                    # Get the onOffStates for both the old (unchanged) device
                    # object and the new (updated) device object.  Invert the
                    # states if specified in the pluginProps.  Ignore the
                    # device object update if the mdevState is unchanged.

                    mDevType = (self._monitoredDevices
                                [devId][mDevId][mDevState])
                    invert = dev.pluginProps.get(mDevType + 'Invert', False)
                    oldState = oldDev.states[mDevState] ^ invert
                    newState = newDev.states[mDevState] ^ invert
                    if oldState == newState:
                        continue  # No change, ignore it.

                    # Create a monitored device event name and log it for
                    # debug.

                    mDevEvent = mDevType + ('-off', '-on')[newState]
                    L.debug('"%s" %s', dev.name, mDevEvent)

                    # Check for expired timer.

                    if mDevEvent == 'tt-off':  # Timer is inactive.
                        if newDev.states['timeLeftSeconds'] == '0':
                            mDevEvent = 'tt-exp'  # Timer has expired.

                    # Update the virtual garage door in response to the new
                    # monitored device event.

                    self._virtualGarageDoors[devId].update(mDevEvent)

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
        Set the logging level if the user requests a change after startup.
        """
        L.threaddebug('validatePrefsConfigUi called')
        level = valuesDict['loggingLevel']
        L.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        return True

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        """
        Validate the ConfigUi travel time.  Create a standard travel timer
        device name based on the opener device name. Configure an existing or
        new timer device using the ConfigUi travel time and the standard device
        name.

        Validate monitored device ConfigUi entries and create the monitored
        device dictionary.
        """
        dev = indigo.devices[devId]
        L.threaddebug('validateDeviceConfigUi called "%s"', dev.name)
        L.debug(valuesDict)
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

        # Derive a standard travel timer device name (tt) from the opener
        # device name (dev.name):

        #    Opener Device Name          Standard Travel Timer Device Name

        #  new device x (default)   devIdnnnnnnnnnnn-travelTimer (nnnnnnnnnn = dev id)
        #  device-opener            device-travelTimer
        #  arbitraryDeviceName      arbitraryDeviceName-travelTimer

        if dev.name.startswith('new device'):
            tt = 'devId%s' % devId
        elif dev.name.endswith('-opener'):
            tt = dev.name[:-7]
        else:
            tt = dev.name
        tt += '-travelTimer'
        valuesDict['tt'] = tt
        L.debug('"%s" standard travel timer device name is "%s"', dev.name, tt)

        # Select and configure the tt device.

        props = dict(amount=tTime, amountType='seconds')
        description = 'Automatically generated timer for "%s"' % dev.name
        try:
            # Use an existing tt device if available; create a new device if
            # not.

            ttDev = indigo.devices.get(tt)  # Search for standard device name.
            if ttDev:  # tt device exists with the standard name; use it.
                L.debug('"%s" using existing travel timer device "%s"',
                        dev.name, ttDev.name)
                self.TIMER.executeAction('setTimerStartValue',
                                         deviceId=ttDev.id, props=props)
            else:  # No device with the standard name.
                ttDevId = valuesDict['ttDevId']  # Search for the tt device id.
                ttDevId = int(ttDevId) if ttDevId else ttDevId
                ttDev = indigo.devices.get(ttDevId)
                if ttDev:  # tt device exists; use it and rename it.
                    L.debug('"%s" using existing travel timer device "%s"',
                            dev.name, ttDev.name)
                    self.TIMER.executeAction('setTimerStartValue',
                                             deviceId=ttDev.id, props=props)
                    L.debug('"%s" renaming travel timer from "%s" to "%s"',
                            dev.name, ttDev.name, tt)
                    ttDev.name = tt
                    ttDev.description = description
                    ttDev.replaceOnServer()
                else:  # No existing tt device; create a new one.
                    L.debug('"%s" creating new travel timer device "%s"',
                            dev.name, tt)
                    indigo.device.create(
                        protocol=indigo.kProtocol.Plugin,
                        name=tt,
                        description=description,
                        pluginId=self.TIMER_PLUGIN_ID,
                        deviceTypeId='timer',
                        props=props,
                        folder='doors')

        except Exception as errorMessage:
            error = '"%s" travel timer init failed: %s' % (tt, errorMessage)
            errors['tTime'] = error
            return False, valuesDict, errors

        # Clear self._monitoredDevices for this opener to prevent previous
        # device configurations from generating ConfigUi errors.

        self._monitoredDevices[devId] = {}

        # Validate all monitored devices that are selected in the opener device
        # ConfigUi.  Ensure that selected device name/state pairs are unique
        # for all monitored device types in all opener devices.  Set the device
        # id fields in the values dictionary.

        mDevConfig = ''
        for mDevType in self.MONITORED_DEVICE_TYPES:
            valuesDict[mDevType + 'DevId'] = ''
            mDevName = valuesDict[mDevType]
            if mDevName:  # Monitored device is selected in the ConfigUi.

                # Validate the device name.

                mDev = indigo.devices.get(mDevName)
                if not mDev:
                    error = '%s not in the devices dictionary' % mDevName
                    errors[mDevType] = error
                    continue

                # Validate the state name.

                mDevStateKey = mDevType + 'State'
                mDevStateName = valuesDict[mDevStateKey]
                if mDevStateName not in mDev.states:
                    error = '%s not in device states dictionary'\
                            % mDevStateName
                    errors[mDevStateKey] = error
                    continue

                # Check to ensure that no device/state pairs are reused by this
                # opener device or others.

                mDevId = mDev.id
                for devId_ in self._monitoredDevices:
                    for mDevId_ in self._monitoredDevices[devId_]:
                        for mDevStateName_ in self._monitoredDevices[devId_][mDevId_]:
                            if mDevId == mDevId_ and mDevStateName == mDevStateName_:
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
                valuesDict['mDevConfig'] = mDevConfig

                # Add keys/values to self._monitoredDevices to mark this
                # device/state combination as used.  Note that these additions
                # are overwritten (with the same data) when the opener device
                # is initialized by the deviceStartComm method.

                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevStateName] = mDevType
                L.debug(self._monitoredDevices[devId])

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
    #  def getRelayDeviceList(self, *args)                                    #
    #  def getSensorDeviceList(self, *args)                                   #
    #  def setMDevConfig(self, valuesDict, *args)                             #
    #                                                                         #
    ###########################################################################

    def getRelayDeviceList(self, *args):
        """
        Return a list of relay device names for the ar device selection menu
        in the opener device ConfigUi.

        List all indigo devices with a deviceTypeIds in RELAY_DEVICE_TYPE_IDs.
        Also include a "none" element to enable the removal of an existing
        selection.
        """
        L.threaddebug('getRelayDeviceList called')
        relays = []
        for dev in indigo.devices:
            if dev.deviceTypeId in self.RELAY_DEVICE_TYPE_IDs:
                relays.append(dev.name)
        return ['None'] + sorted(relays)

    def getSensorDeviceList(self, *args):
        """
        Return a list of sensor device names for the cs, os, and vs device
        selection menus in the opener device ConfigUi.

        List all indigo devices with a deviceTypeIds in SENSOR_DEVICE_TYPE_IDs.
        Also include a "none" element to enable the removal of an existing
        selection.
        """
        L.threaddebug('getSSensorDeviceList called')
        sensors = []
        for dev in indigo.devices:
            if dev.deviceTypeId in self.SENSOR_DEVICE_TYPE_IDs:
                sensors.append(dev.name)
        return ['None'] + sorted(sensors)

    def setMDevConfig(self, valuesDict, *args):
        """
        Respond to a user selection from any of the monitored device selection
        menus in the opener device ConfigUi.

        For each monitored device type menu item in the ConfigUi:

        (1) If no device name is selected in the menu (the name is the null
        string), do nothing.  This device type is not in the monitored device
        configuration.  The device Config checkbox will retain its default
        value of false.
        (2) If None is selected in the menu (the name is None), this device
        type was previously selected, but is now being de-selected.  Set the
        monitored device name to the null string to indicate that the device is
        not in the configuration.  Set the monitored device Config checkbox to
        false to supress the display of additional fields in the ConfigUi.
        (3) If a valid name is selected (not the null string and not None),
        then set the monitored device Config checkbox to true to allow the
        configuration of the additional the fields in the ConfigUi.
        """
        L.threaddebug('setMDevConfig called')

        for mDevType in self.MONITORED_DEVICE_TYPES:
            mDevName = valuesDict[mDevType]  # The selected mDevType dev name.
            mDevConfig = mDevType + 'Config'
            if mDevName:
                if mDevName == 'None':
                    valuesDict[mDevType] = ''
                    valuesDict[mDevConfig] = 'false'
                else:
                    valuesDict[mDevConfig] = 'true'
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
    # def _toggleActivationRelay(self, dev)                                   #
    # def closeGarageDoor(self, pluginAction)                                 #
    # def openGarageDoor(self, pluginAction)                                  #
    # def toggleGarageDoor(self, pluginAction)                                #
    # def actionControlDevice(self, action, dev)                              #
    # def actionControlUniversal(action, dev)                                 #
    #                                                                         #
    ###########################################################################

    def _toggleActivationRelay(self, dev):
        """
        Turn on the activation relay for a period equal to the global
        AR_CLOSURE_TIME.  Use special plugin actions for EasyDAQ relay devices;
        otherwise use the standard Indigo device turnOn method.
        """
        L.threaddebug('_toggleActivationRelay called "%s"', dev.name)
        arDevId = dev.pluginProps.get('arDevId')
        if arDevId:
            arDevId = int(arDevId)
            arDev = indigo.devices[arDevId]
            if arDev.deviceTypeId.startswith('easyDaq'):  # EasyDAQ relay.
                plugin = indigo.server.getPlugin(arDev.pluginId)
                props = dict(channelSel=int(dev.pluginProps['arState'][8:9]))
                plugin.executeAction('turnOnOutput', deviceId=arDevId,
                                     props=props)
                sleep(self.AR_CLOSURE_TIME)
                plugin.executeAction('turnOffOutput', deviceId=arDevId,
                                     props=props)
            else:  # Standalone relay device.
                indigo.device.turnOn(arDevId, duration=self.AR_CLOSURE_TIME)
        else:
            error = 'no activation relay specified; door action ignored.'
            L.warning('"%s" %s', dev.name, error)

    def closeGarageDoor(self, pluginAction):
        """
        Toggle the activation relay to close the garage door if it is not
        already closed.  This prevents the inadvertent opening of the door with
        a close command.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('closeGarageDoor called "%s"', dev.name)
        if not dev.states['onOffState']:
            self._toggleActivationRelay(dev)
        else:
            error = ('attempt to toggle the garage door closed when it is '
                     'already closed; door action ignored.')
            L.warning('"%s" %s', dev.name, error)

    def openGarageDoor(self, pluginAction):
        """
        Toggle the activation relay to open the garage door if it is closed.
        This prevents the inadvertent closing of the door with an open command.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('openGarageDoor called "%s"', dev.name)
        if dev.states['onOffState']:
            self._toggleActivationRelay(dev)
        else:
            error = ('attempt to toggle the garage door open when it is '
                     'not closed; door action ignored.')
            L.warning('"%s" %s', dev.name, error)

    def toggleGarageDoor(self, pluginAction):
        """
        Toggle the activation relay with no state conditions.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('toggleGarageDoor called "%s"', dev.name)
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
        L.threaddebug('actionControlDevice called "%s"', dev.name)
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            if not dev.states['onOffState']:  # Close if not already closed.
                self._toggleActivationRelay(dev)
            else:
                error = ('attempt to toggle the garage door open when it is '
                         'not closed; door action ignored.')
                L.warning('"%s" %s', dev.name, error)
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            self._toggleActivationRelay(dev)  # Allow opening anytime.
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            self._toggleActivationRelay(dev)

    def actionControlUniversal(self, action, dev):
        """
        Implement the requestStatus command by logging the current door state.
        """
        L.threaddebug('actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            L.info('"%s" is %s', dev.name, dev.states['doorStatus'].upper())
