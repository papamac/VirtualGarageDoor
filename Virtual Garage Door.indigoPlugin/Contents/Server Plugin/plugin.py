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
 VERSION:  1.3.9
    DATE:  September 15, 2024

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
action groups, control pages, triggers, and other plugins.

The plugin also creates a VGD lock device for each VGD opener device.  Engaging
the lock device locks the garage door by disabling open/close actions and
optionally powering down the physical opener and/or engaging a physical lock.
The plugin provides actions to open, close, lock and unlock the garage door.

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
update method to perform detailed device functions.  Also, action callback
methods implement the open, close, lock, and unlock plugin actions.

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
                    the name was changed by the user after initialization.
                    (2) Improve the travel timer device management process.
                    Standardize travel timer device names and restore them
                    if they are changed.
v1.3.0   5/23/2024  Add optional actions and/or delays prior to toggling the
                    activation relay for closing and opening.
v1.3.1   6/21/2024  (1) Remove the toggleGarageDoor action because it is
                    normally not necessary and is an unattended operation
                    safety risk.
                    (2) Add lockGarageDoor and unlockGarageDoor actions as part
                    of a larger VGD security update.
                    (3) Encapsulate travel timer initilization functions into
                    a new internal method _initTravelTimerDevice(self, dev) in
                    preparation for introducing a new lock device.
v1.3.2   7/12/2024  Add a new lock device to the plugin.
v1.3.3   7/17/2024  (1) Fix a bug in the _initializeLockDevice method.
                    (2) Add validation code for lock devices in
                    validateDeviceConfigUi.
v1.3.4   8/18/2024  (1) Add a deviceTypeId check when looking for existing lock
                    and travel timer devices.
                    (2) Eliminate the LOCKED state from the door state
                    enumeration.
                    (3) Update action callback methods to use the lock device
                    state for locked/unlocked decisions.
v1.3.6    9/4/2024  Update comments and wiki figures/tables.
v1.3.7   9/13/2024  Update comments and wiki figures/tables.
v1.3.8   9/14/2024  (1) Change the _lockGarageDoor and _unlockGarageDoor
                    methods to update the lock device states after successful
                    execution of the optional actions.  If any exception
                    occurs, log a warning message and return without updating
                    the states.
                    (2) Update comments and table3.
v1.3.9   9/15/2024  (1) Change the _lockGarageDoor and _unlockGarageDoor
                    methods to check the lock device state before proceeding.
                    Ignore action if there will be no change in the lock state.
                    (2) Update comments and table3.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '1.3.9'
__date__ = 'September 15, 2024'

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

    AR_CLOSURE_TIME = 0.8  # Activation relay momentary closure time (seconds).
    LOCK_PLUGIN_ID = 'net.papamac.indigoplugin.virtualgaragedoor'
    TIMER_PLUGIN_ID = 'com.perceptiveautomation.indigoplugin.timersandpesters'
    TIMER = indigo.server.getPlugin(TIMER_PLUGIN_ID)

    # Lock state enumeration and lock status.

    UNLOCKED, LOCKED = (False, True)
    LOCK_STATUS = ('unlocked', 'locked')
    LOCK_STATES = [status.upper() for status in LOCK_STATUS]

    # Door state enumeration and stationary states.

    OPEN, CLOSED, OPENING, CLOSING, STOPPED, REVERSING = range(6)
    STATIONARY_STATES = (OPEN, CLOSED, STOPPED)

    # Monitored device types used in deviceStartComm and validateDeviceConfigUi
    # methods.

    MONITORED_DEVICE_TYPES = (

        'ar',  # activation relay
        'cs',  # closed sensor
        'os',  # open sensor
        'vs',  # vibration sensor
        'tt')  # travel timer

    # Configuration fields to be dynamically updated during ConfigUi execution:

    DYNAMIC_CONFIG_FIELD_IDs = ((

        'openingActionGroup',          # Action group executed before opening
        'closingActionGroup',          # Action group executed before closing
        'powerSwitch',                 # Opener physical power switch device
        'mechanicalLock',              # Garage door mechanical lock device
        'lockingActionGroup',          # Action group executed before locking
        'unlockingActionGroup')        # Action group executed before unlocking
        + MONITORED_DEVICE_TYPES[:4])  # Monitored devices sans tt

    # Relay, sensor, and switch device type id tuples used by the dynamic
    # device list callback method in Plugin Part III.

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

    relayDeviceTypeIds = (easyDaqComboTypeIds + easyDaqRelayTypeIds
                          + shellyDirectRelayTypeIds + shellyMQTTRelayTypeIds
                          + genericRelayTypeIds)

    sensorDeviceTypeIds = (easyDaqComboTypeIds + easyDaqSensorTypeIds
                           + genericSensorTypeIds)

    switchDeviceTypeIds = ('pseudoRelay', 'relay', 'zwRelayType')

    # Device id selection dictionary keyed by device type:

    DEVICE_TYPE_IDs = {'relay':  relayDeviceTypeIds,
                       'sensor': sensorDeviceTypeIds,
                       'switch': switchDeviceTypeIds}

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
    #  def _updateLockStatesOnServer(self)                                    #
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

    def _updateLockStatesOnServer(self, dev, lockState):
        """
        Update the lock states on the Indigo server for use by the Home window,
        scripts, action groups, control pages, triggers, and other plugins.

        The lock states include the onOffState and the lockStatus.  The
        onOffState is the lockState with values UNLOCKED (off) and LOCKED (on).
        The lockStatus is a lower case string representation of the lockState
        enumeration (locked or unlocked).

        Also, set the state image on the Indigo Home window based on the value
        of the lockState (onOffState).  Select a green lock image if the
        lockState is LOCKED (on) and a red lock image if it is UNLOCKED (off).
        """

        # Compute lock status and update states on server.

        lockStatus = self.LOCK_STATUS[lockState]
        dev.updateStateOnServer('onOffState', lockState, uiValue=lockStatus)
        dev.updateStateOnServer('lockStatus', lockStatus)
        L.info('"%s" update to %s', dev.name, self.LOCK_STATES[lockState])

        # Select and update state image.

        image = (indigo.kStateImageSel.Locked if lockState
                 else indigo.kStateImageSel.Unlocked)
        dev.updateStateImageOnServer(image)

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
        Initialize lock and door opener devices.  For each lock device, set
        the initial lock state to UNLOCKED.  For each opener device, create a
        new monitored devices dictionary entry and a new virtual garage door
        instance.
        """
        L.threaddebug('deviceStartComm called "%s"', dev.name)

        # Initialize lock device:

        if dev.deviceTypeId == 'lock':
            self._updateLockStatesOnServer(dev, self.UNLOCKED)
            return

        # Initialize opener device:

        # Create a new monitored devices dictionary entry for the opener.

        devId = dev.id
        self._monitoredDevices[devId] = {}

        # Add all monitored devices that are selected in the opener device
        # ConfigUi to the monitored devices dictionary.  Save the initial
        # states of the devices for use in setting the initial device opener
        # state.

        error = False
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
                    error = True
                    continue
                mDevStateName = dev.pluginProps[mDevType + 'State']
                if mDevStateName not in mDev.states:
                    L.error('"%s" "%s" state %s is not in states dictionary',
                            dev.name, mDev.name, mDevStateName)
                    error = True
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

        if error:  # Abort deviceStartComm if there was an error.
            self.deviceStopComm(dev)
            L.error('"%s" init error(s): check/run ConfigUi', dev.name)
            dev.setErrorStateOnServer('init err')  # Set error state.

        else:  # No error.

            # Instantiate a VirtualGarageDoor object for the device and clear
            # the error state on the server, if any.

            vgd = VirtualGarageDoor(self, dev, mDevStates)
            self._virtualGarageDoors[devId] = vgd
            dev.setErrorStateOnServer(None)

    def deviceStopComm(self, dev):
        """ Retire door opener devices. """
        L.threaddebug('deviceStopComm called "%s"', dev.name)
        if dev.deviceTypeId == 'lock':  # Lock device requires no closeout.
            return

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
                    L.debug('"%s" event %s', dev.name, mDevEvent)

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
    #                        Internal Support Methods                         #
    #                                                                         #
    #  def _initializeLockDevice(self, dev, valuesDict, errorsDict)           #
    #  def _initializeTravelTimer(self, dev, valuesDict, errorsDict)          #
    #                                                                         #
    #                        Core Validation Methods                          #
    #                                                                         #
    #  def validatePrefsConfigUi(valuesDict)                                  #
    #  def validateDeviceConfigUi(self, valuesDict, typeId, devId)            #
    #                                                                         #
    ###########################################################################

    def _initializeLockDevice(self, dev, valuesDict):
        """
        Validate the ConfigUi open/close travel time entry.  Create a standard
        travel timer device name derived from the opener device name and add it
        to the values dictionary with the key tt.

        If there is an existing device with the standard name, configure it
        with the validated travel time and use it.  If not, check for an
        existing timer device using a prior timer device id.  If there is an
        existing timer, configure it and rename it with the standard device
        name.  If no existing timer devices are available, create a new device
        using the validated travel time and the standard timer device name.

        If there is an error, add it to the errors dictionary with the key
        tTime and return.
        """
        L.threaddebug(' _initializeLockDevice called "%s"', dev.name)

        # Derive a standard lock device name (tt) from the opener device name
        # (dev.name):

        #   Opener Device Name            Standard Lock Device Name

        #  new device (default)   devIdnnnnnnnnnnn-lock (nnnnnnnnnn = dev id)
        #  device-opener          device-lock
        #  arbitraryDeviceName    arbitraryDeviceName-lock

        devId = str(dev.id)
        if dev.name.startswith('new device'):
            lk = 'devId%s' % devId
        elif dev.name.endswith('-opener'):
            lk = dev.name[:-7]
        else:
            lk = dev.name
        lk += '-lock'
        L.debug('"%s" standard lock device name is "%s"', dev.name, lk)

        # Select and configure the tt device with the validated travel time.

        description = 'Automatically generated lock for "%s"' % dev.name
        try:
            # Use an existing lk device if available; create a new device
            # if not.

            lkDev = indigo.devices.get(lk)  # Get dev for standard name.
            if lkDev and lkDev.deviceTypeId == 'lock':  # lock device exists.
                L.debug('"%s" using existing lock device "%s"',
                        dev.name, lk)

                # Update the pluginProps link to the opener device if needed.

                if lkDev.pluginProps['opDevId'] != devId:
                    props = lkDev.pluginProps
                    props['opDevId'] = devId
                    lkDev.replacePluginPropsOnServer(props)
            else:  # No device with the standard name.
                lkDevId = valuesDict['lkDevId']  # Check prior device id.
                lkDevId = int(lkDevId) if lkDevId else lkDevId
                lkDev = indigo.devices.get(lkDevId)
                if lkDev:  # lk device exists; use it and rename it.
                    L.debug('"%s" using existing lock device "%s"',
                            dev.name, lkDev.name)
                    L.debug('"%s" renaming lock device from "%s" to "%s"',
                            dev.name, lkDev.name, lk)
                    lkDev.name = lk
                    lkDev.description = description
                    lkDev.replaceOnServer()
                else:  # No existing lk device; create a new one.
                    L.debug('"%s" creating new lock device "%s"', dev.name, lk)
                    indigo.device.create(
                        protocol=indigo.kProtocol.Plugin,
                        name=lk,
                        description=description,
                        pluginId=self.LOCK_PLUGIN_ID,
                        deviceTypeId='lock',
                        props=dict(opDevId=devId,  # Lock dev link to opener.
                                   powerSwitch='',
                                   mechanicalLock='',
                                   lockingActionGroup='',
                                   unlockingActionGroup=''),
                        folder='doors')
                    lkDev = indigo.devices.get(lk)

            valuesDict['lkDevId'] = str(lkDev.id)  # Opener dev link to lock.

        except Exception as errorMessage:
            L.error('"%s" lock device init failed: %s', lk, errorMessage)

        return valuesDict  # Return with or without errors.

    def _initializeTravelTimer(self, dev, valuesDict, errorsDict):
        """
        Validate the ConfigUi open/close travel time entry.  Create a standard
        travel timer device name derived from the opener device name and add it
        to the values dictionary with the key tt.

        If there is an existing device with the standard name, configure it
        with the validated travel time and use it.  If not, check for an
        existing timer device using a prior timer device id.  If there is an
        existing timer, configure it and rename it with the standard device
        name.  If no existing timer devices are available, create a new device
        using the validated travel time and the standard timer device name.

        If there is an error, add it to the errors dictionary with the key
        tTime and return.
        """
        L.threaddebug('_initializeTravelTimer called "%s"', dev.name)

        # Validate the open/close travel time entry.

        tTime = 0  # Force an error if try fails.
        try:
            tTime = float(valuesDict['tTime'])
        except ValueError:
            pass
        if not 8 <= tTime <= 20:
            error = 'Travel time must be a number between 8 and 20 seconds'
            errorsDict['tTime'] = error
            return valuesDict, errorsDict  # Return with error.

        # Derive a standard travel timer device name (tt) from the opener
        # device name (dev.name):

        #   Opener Device Name         Standard Travel Timer Device Name

        #  new device (default)   devIdnnnnnnnnnnn-travelTimer (nnnnnnnnnn = dev id)
        #  device-opener          device-travelTimer
        #  arbitraryDeviceName    arbitraryDeviceName-travelTimer

        if dev.name.startswith('new device'):
            tt = 'devId%s' % dev.id
        elif dev.name.endswith('-opener'):
            tt = dev.name[:-7]
        else:
            tt = dev.name
        tt += '-travelTimer'
        L.debug('"%s" standard travel timer device name is "%s"',
                dev.name, tt)

        # Add the timer device name to the values dictionary.

        valuesDict['tt'] = tt

        # Select and configure the tt device with the validated travel time.

        props = dict(amount=tTime, amountType='seconds')
        description = 'Automatically generated timer for "%s"' % dev.name
        try:
            # Use an existing tt device if available; create a new device
            # if not.

            ttDev = indigo.devices.get(tt)  # Get dev for standard name.
            if ttDev and ttDev.deviceTypeId == 'timer':  # tt device exists.
                L.debug('"%s" using existing travel timer device "%s"',
                        dev.name, tt)
                self.TIMER.executeAction('setTimerStartValue',
                                         deviceId=ttDev.id, props=props)
            else:  # No device with the standard name.
                ttDevId = valuesDict['ttDevId']  # Check prior device id.
                ttDevId = int(ttDevId) if ttDevId else ttDevId
                ttDev = indigo.devices.get(ttDevId)
                if ttDev:  # tt device exists; use it and rename it.
                    L.debug('"%s" using existing travel timer device "%s"',
                            dev.name, ttDev.name)
                    self.TIMER.executeAction('setTimerStartValue',
                                             deviceId=ttDev.id,
                                             props=props)
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
            error = '"%s" Travel timer init failed: %s' % (tt, errorMessage)
            errorsDict['tTime'] = error

        return valuesDict, errorsDict  # Return with or without errors.

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
        Validate both lock and opener device ConfigUi's:

        For a lock device ensure that the hidden textfield 'opDevId' is linked
        to a valid opener device.  This link is inserted when the lock device
        is created by executing the opener ConfigUi.  It is not set if the lock
        device is created using the "New..." button in the Indigo Home window.
        A VGD lock device is automatically created with a valid link when the
        opener device is configured.  Lock options can then be selected using
        the lock ConfigUi.

        For an opener device, initialize the lock device and the travel timer.
        In both cases, use existing devices if available or create new ones if
        not.  Validate all manual entries in the ConfigUi.  Check monitored
        devices and their onOffState names to ensure that the onOffState name
        is in the device's states dictionary.  Also check to ensure that a
        particular device/state combination is not reused in multiple monitored
        devices for all opener devices.  Add configuration flags, monitored
        device id's, and initial monitored device states to the values
        dictionary for use by other methods.  Finally, validate the closing
        and opening delay times.  In all cases where errors are found, add
        an error message to the errors dictionary and return the errors
        dictionary
        """
        dev = indigo.devices[devId]
        L.threaddebug('validateDeviceConfigUi called "%s"', dev.name)
        L.debug(valuesDict)

        # Validate VGD lock device:

        if typeId == 'lock':
            opDevId = dev.pluginProps.get('opDevId')  # Opener device id.
            if opDevId:  # Lock device is linked to sn opener device.
                opDev = indigo.devices.get(int(opDevId))  # Opener device.
                if opDev and opDev.deviceTypeId == 'opener':
                    return True
            L.warning('"%s" lock device is not linked to an valid opener '
                      'device; create and initialize lock devices only with '
                      'the opener device ConfigUi')
            return False

        # Validate VGD opener device:

        errorsDict = indigo.Dict()

        # Initialize the lock device and travel timer.

        valuesDict = self._initializeLockDevice(dev, valuesDict)
        valuesDict, errorsDict = self._initializeTravelTimer(dev, valuesDict,
                                                             errorsDict)

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
                    errorsDict[mDevType] = error
                    continue

                # Validate the state name.

                mDevStateKey = mDevType + 'State'
                mDevStateName = valuesDict[mDevStateKey]
                if mDevStateName not in mDev.states:
                    error = '%s not in device states dictionary'\
                            % mDevStateName
                    errorsDict[mDevStateKey] = error
                    continue

                # Check to ensure that no device/state pairs are reused by this
                # opener device or others.  Bypass this test for the travel
                # timer because the timer devices and state name are generated
                # automatically.

                mDevId = mDev.id
                for devId_ in self._monitoredDevices:
                    for mDevId_ in self._monitoredDevices[devId_]:
                        for mDevStateName_ in self._monitoredDevices[devId_][mDevId_]:
                            if mDevId == mDevId_ and mDevStateName == mDevStateName_:
                                if mDevType == 'tt':
                                    error = ('Timer device/state name already '
                                             'in use')
                                    errorsDict['tTime'] = error
                                else:
                                    error = 'Device/state name already in use'
                                    errorsDict[mDevType] = error
                                    errorsDict[mDevStateKey] = error
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
                        errorsDict['vsResetDelay'] = error
                        continue

                # No error for this monitored device/state; update derived
                # values in the values dictionary.

                valuesDict[mDevType + 'DevId'] = str(mDevId)
                mDevConfig += mDevType + ' '

                # Add keys/values to self._monitoredDevices to mark this
                # device/state combination as used.  Note that these additions
                # are overwritten (with the same data) when the opener device
                # is initialized by the deviceStartComm method.

                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevStateName] = mDevType
                L.debug(self._monitoredDevices[devId])

        # All mDevTypes validated. Update the monitored device configuration.

        valuesDict['mDevConfig'] = mDevConfig

        # Validate the closing delay time.

        closingDelayTime = -1  # Force an error if the try fails.
        try:
            closingDelayTime = float(valuesDict['closingDelayTime'])
        except ValueError:
            pass
        if not 0 <= closingDelayTime <= 10:
            error = ('Closing delay time must be a number between 0 and 10 '
                    'seconds')
            errorsDict['closingDelayTime'] = error

        # Validate the opening delay time.

        openingDelayTime = -1  # Force an error if the try fails.
        try:
            openingDelayTime = float(valuesDict['openingDelayTime'])
        except ValueError:
            pass
        if not 0 <= openingDelayTime <= 10:
            error = ('Opening delay time must be a number between 0 and 10 '
                    'seconds')
            errorsDict['openingDelayTime'] = error

        # Return with or without errors.

        L.debug(valuesDict)
        L.debug(errorsDict)
        return not bool(errorsDict), valuesDict, errorsDict

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
    #                       CONFIG UI CALLBACK METHODS                        #
    #                                                                         #
    #  def getActionGroupList(filter_, valuesDict, typeId, devId)             #
    #  def getDeviceList(self, filter_, valuesDict, typeId, devId)            #
    #  def updateDynamicConfigValues(self, valuesDict, typeId, devId)         #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def getActionGroupList(filter_, valuesDict, typeId, devId):
        """
        Create a list of action group names for the action group selection
        menus in the lock and opener device ConfigUi's.

        Return a sorted list of action groups along with a 'None' option
        to enable the removal of an existing selection by the
        updateDynamicConfigValues method.
        """
        dev = indigo.devices[devId]
        L.threaddebug('getActionGroupList called "%s"', dev.name)

        actionGroups = []
        for actionGroup in indigo.actionGroups.iter('self'):
            actionGroups.append(actionGroup.name)
        return ['None'] + sorted(actionGroups)

    def getDeviceList(self, filter_, valuesDict, typeId, devId):
        """
        Create a list of device names for the device selection menus in the
        lock and opener device ConfigUi's.

        Select devices for the menu list based on the value of the filter_
        argument which is defined in the ConfigUi list specification.  filter_
        values can be lock, relay, sensor, or switch.  For the lock filter
        select devices that have a subType attribute whose value is 'Lock'. For
        the relay, sensor, and switch filters select devices with a
        deviceTypeId in the self.DEVICE_TYPE_IDs[filter_] tuple.

        Return a sorted list of selected devices along with a 'None' option
        to enable the removal of an existing selection by the
        updateDynamicConfigValues method.
        """
        dev = indigo.devices[devId]
        L.threaddebug('getDeviceList called "%s"', dev.name)

        devices = []
        for dev in indigo.devices:
            if filter_ == 'lock':
                selector = (hasattr(dev, 'subType')
                            and dev.subType == 'Lock'
                            and dev.id != devId)
            else:
                selector = dev.deviceTypeId in self.DEVICE_TYPE_IDs[filter_]
            if selector:
                devices.append(dev.name)
        return ['None'] + sorted(devices)

    def updateDynamicConfigValues(self, valuesDict, typeId, devId):
        """
        Respond to a user selection of any value in a lock or opener ConfigUi
        dynamic menu list.  These can be either action group or device
        selection menus that are generated by the getActionGroupList and the
        getDeviceList callback methods above.  The field id's for the dynamic
        list fields must be included in the self.DYNAMIC_CONFIG_FIELD_IDs
        tuple.  Two types of changes are made to the values dictionary for
        fields associated with dynamic list fields:

        (1) For all field ids in the self.DYNAMIC_CONFIG_FIELD_IDs tuple,
        replace a user-selected value of 'None' with the null string.  This
        allows a user to de-select a previously selected menu option by
        selecting the 'None' option.

        (2) For field ids that specify monitored devices (those in the
        self.MONITORED_DEVICE_TYPES tuple) set the value of the 'xxConfig'
        hidden checkbox field.  The value is set to 'true' if the xx field id
        is selected, and 'false' otherwise.  This permits related field id's
        to be dynamically hidden in the ConfigUi if the xx field id is
        nat selected, or displayed if it is selected.

        If the initial value of a field is the null string leave the values
        dictionary unchanged.
        """
        dev = indigo.devices[devId]
        L.threaddebug('updateDynamicConfigValues called "%s"', dev.name)

        for fieldId in self.DYNAMIC_CONFIG_FIELD_IDs:
            if valuesDict.get(fieldId):
                if valuesDict[fieldId] == 'None':
                    valuesDict[fieldId] = ''
                if fieldId in self.MONITORED_DEVICE_TYPES:
                    valuesDict[fieldId+'Config'] = (
                        'true' if valuesDict[fieldId] else 'false')
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
    #                     Internal Action Support Methods                     #
    #                                                                         #
    #  def _toggleActivationRelay(self, opDev)                                #
    #  def _executeOptionalActions(opDev, action='opening')                   #
    #  def _openGarageDoor(self, opDev)                                       #
    #  def _closeGarageDoor(self, opDev)                                      #
    #  def _lockGarageDoor(self, lkDev)                                       #
    #  def _unlockGarageDoor(self, lkDev)                                     #
    #                                                                         #
    #                         Plugin Callback Methods                         #
    #                                                                         #
    #  def openGarageDoor(self, pluginAction)                                 #
    #  def closeGarageDoor(self, pluginAction)                                #
    #  def lockGarageDoor(self, pluginAction)                                 #
    #  def unlockGarageDoor(self, pluginAction)                               #
    #                                                                         #
    #                  Device and Universal Callback Methods                  #
    #                                                                         #
    #  def actionControlDevice(self, action, dev)                             #
    #  def actionControlUniversal(self, action, dev)                          #
    #                                                                         #
    ###########################################################################

    def _toggleActivationRelay(self, opDev):
        """
        Turn on the activation relay for a period equal to the global
        AR_CLOSURE_TIME.  Use special plugin actions for EasyDAQ relay devices;
        otherwise use the standard Indigo device turnOn method.
        """
        L.threaddebug('_toggleActivationRelay called "%s"', opDev.name)

        arDevId = opDev.pluginProps.get('arDevId')
        if arDevId:
            arDevId = int(arDevId)
            arDev = indigo.devices[arDevId]
            if arDev.deviceTypeId.startswith('easyDaq'):  # EasyDAQ relay.
                plugin = indigo.server.getPlugin(arDev.pluginId)
                props = dict(channelSel=int(opDev.pluginProps['arState'][8:9]))
                plugin.executeAction('turnOnOutput', deviceId=arDevId,
                                     props=props)
                sleep(self.AR_CLOSURE_TIME)
                plugin.executeAction('turnOffOutput', deviceId=arDevId,
                                     props=props)
            else:  # Indigo relay device.
                indigo.device.turnOn(arDevId)
                sleep(self.AR_CLOSURE_TIME)
                indigo.device.turnOff(arDevId)
        else:
            L.warning('"%s" no activation relay specified; door action '
                      'ignored', opDev.name)

    @staticmethod
    def _executeOptionalActions(opDev, action='opening'):
        """
        Optionally execute closing or opening action group and closing/opening
        delay based on pluginProps entries.  Do nothing if the action group
        or delay keys are not in the pluginProps dictionary.  This ensures
        backward compatibility with opener devices created by older plugin
        versions.
        """
        L.threaddebug('_executeOptionalActions called "%s"', opDev.name)

        actionGroup = opDev.pluginProps[action + 'ActionGroup']
        if actionGroup:
            indigo.actionGroup.execute(actionGroup)

        delayTime = opDev.pluginProps[action + 'DelayTime']
        if delayTime:
            sleep(float(delayTime))

    def _openGarageDoor(self, opDev):
        """
        If the garage door is locked, log a warning message and return.  No
        opening/closing actions are allowed when the door is locked.

        If the door is not closed, also log a warning message and return.  This
        prevents inadvertently toggling the door when it is already open or
        is stopped (obstructed).

        If the door is moving (not in a stationary state), log a warning
        message and return.  Remote door actions are not allowed when the door
        is in motion.

        Otherwise (door is not locked and closed), execute optional user
        actions and then toggle the activation relay to open the garage door.
        """
        L.threaddebug('_openGarageDoor called "%s"', opDev.name)
        lkDevId = int(opDev.pluginProps['lkDevId'])  # Get lock device id.
        lkDev = indigo.devices[lkDevId]  # Get lock device object.
        doorState = opDev.states['doorState']

        if lkDev.onState:  # Door is locked.
            L.warning('"%s" attempt to open the garage door when it is '
                      'locked; door action ignored', opDev.name)

        elif doorState != self.CLOSED:  # Door is not closed.
            L.warning('"%s" attempt to open the garage door when it is '
                      'not closed; door action ignored', opDev.name)

        elif doorState not in self.STATIONARY_STATES:  # Door is moving.
            L.warning('"%s" attempt to open the garage door when it is '
                      'moving; door action ignored', opDev.name)

        else:  # Execute user actions and toggle the door open.
            self._executeOptionalActions(opDev)
            self._toggleActivationRelay(opDev)

    def _closeGarageDoor(self, opDev):
        """
        If the garage door is locked, log a warning message and return.  No
        opening/closing actions are allowed when the door is locked.

        If the door is already closed, also log a warning message and return.
        This prevents inadvertently toggling the door to open with a close
        action.

        If the door is moving (not in a stationary state), log a warning
        message and return.  Remote door actions are not allowed when the door
        is in motion.

        Otherwise (door is not locked, closed, or moving), execute optional
        user actions and then toggle the activation relay to close the garage
        door.
        """
        L.threaddebug('_closeGarageDoor called "%s"', opDev.name)
        lkDevId = int(opDev.pluginProps['lkDevId'])  # Get lock device id.
        lkDev = indigo.devices[lkDevId]  # Get lock device object.
        doorState = opDev.states['doorState']

        if lkDev.onState:  # Door is locked.
            L.warning('"%s" attempt to close the garage door when it is '
                      'locked; door action ignored', opDev.name)

        elif doorState == self.CLOSED:  # Door is closed.
            L.warning('"%s" attempt to close the garage door when it is '
                      'already closed; door action ignored', opDev.name)

        elif doorState not in self.STATIONARY_STATES:  # Door is moving.
            L.warning('"%s" attempt to close the garage door when it is '
                      'moving; door action ignored', opDev.name)

        else:  # Execute user actions and toggle the door closed.
            self._executeOptionalActions(opDev, action='closing')
            self._toggleActivationRelay(opDev)

    def _lockGarageDoor(self, lkDev):
        """
        If the lock state is LOCKED or door state is not CLOSED, log a warning
        message and return.  The garage door can only be locked when it is
        currently unlocked and closed.

        Optionally execute locking actions to (1) turn off the garage door
        opener power, (2) turn on (lock) a garage door mechanical lock, and
        (3) execute a user-specified locking action group.  Log a warning
        message and return if any of the optional actions fails to execute.

        If there are no exceptions, set the lock device states on the server to
        locked.
        """
        L.threaddebug('_lockGarageDoor called "%s"', lkDev.name)
        opDevId = int(lkDev.pluginProps['opDevId'])  # Get opener device id.
        opDev = indigo.devices[opDevId]  # Get opener device object.

        # Ensure that the lock state is UNLOCKED and the door state is CLOSED.

        if lkDev.onState:  # Door is locked.
            L.warning('"%s" attempt to lock the garage door when it is '
                      'already locked; door action ignored', lkDev.name)
            return

        if opDev.states['doorState'] != self.CLOSED:  # Door is not closed.
            L.warning('"%s" attempt to lock the garage door when it is not '
                      'closed; door action ignored', lkDev.name)
            return

        # Execute optional locking actions in order (1) power switch off,
        # (2) mechanical lock on, and (3) locking action group.

        try:
            powerSwitch = lkDev.pluginProps['powerSwitch']
            if powerSwitch:
                indigo.device.turnOff(powerSwitch)

            mechanicalLock = lkDev.pluginProps['mechanicalLock']
            if mechanicalLock:
                indigo.device.turnOn(mechanicalLock)

            lockingActionGroup = lkDev.pluginProps['lockingActionGroup']
            if lockingActionGroup:
                indigo.actionGroup.execute(lockingActionGroup)

        except Exception as warningMessage:
            L.warning('"%s" optional locking action failed: %s',
                      lkDev.name, warningMessage)
            return

        # Update lock device states.

        self._updateLockStatesOnServer(lkDev, self.LOCKED)

    def _unlockGarageDoor(self, lkDev):
        """
        If the lock state is UNLOCKED or the door state is not closed, log a
        warning message and return.  The garage door can only be unlocked when
        it is both locked and closed.

        Optionally execute unlocking actions to (1) execute a user-specified
        unlocking actin group, (2) turn off (unlock) a garage door mechanical
        lock, and (3) turn on the garage door opener power.  Log a warning
        message and return if any of the optional actions fails to execute.

        If there are no exceptions, set the lock device states on the server to
        unlocked.
        """
        L.threaddebug('unlockGarageDoor called "%s"', lkDev.name)
        opDevId = int(lkDev.pluginProps['opDevId'])  # Get opener device id.
        opDev = indigo.devices[opDevId]  # Get opener device object.

        # Ensure that the lock state is LOCKED and the door state is CLOSED.

        if not lkDev.onState:  # Door is not locked.
            L.warning('"%s" attempt to unlock the garage door when it is '
                      'not locked; door action ignored', lkDev.name)
            return

        if opDev.states['doorState'] != self.CLOSED:  # Door is not closed.
            L.warning('"%s" attempt to unlock the garage door when it is not '
                      'closed; door action ignored', lkDev.name)
            return

        # Execute optional unlocking actions in order (1) unlocking action
        # group, (2) mechanical lock off, and (3) power switch on.

        try:
            unlockingActionGroup = lkDev.pluginProps['unlockingActionGroup']
            if unlockingActionGroup:
                indigo.actionGroup.execute(unlockingActionGroup)

            mechanicalLock = lkDev.pluginProps['mechanicalLock']
            if mechanicalLock:
                indigo.device.turnOff(mechanicalLock)

            powerSwitch = lkDev.pluginProps['powerSwitch']
            if powerSwitch:
                indigo.device.turnOn(powerSwitch)

        except Exception as warningMessage:
            L.warning('"%s" optional unlocking action failed: %s',
                      lkDev.name, warningMessage)
            return

        # Update lock device states.

        self._updateLockStatesOnServer(lkDev, self.UNLOCKED)

    def openGarageDoor(self, pluginAction):
        """
        Get the device from the pluginAction argument and call the internal
        open method.  Log a warning message if the pluginAction device is not
        an opener.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('openGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':
            self._openGarageDoor(dev)
        else:
            L.warning('"%s" open action requested for a lock device; '
                      'action ignored', dev.name)

    def closeGarageDoor(self, pluginAction):
        """
        Get the device from the pluginAction argument and call the internal
        close method.  Log a warning message if the pluginAction device is not
        an opener.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('closeGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':
            self._closeGarageDoor(dev)
        else:
            L.warning('"%s" close action requested for a lock device; '
                      'action ignored', dev.name)

    def lockGarageDoor(self, pluginAction):
        """
        Lock a garage door given either a lock device or an opener device.
        If a lock device is referenced in the pluginAction argument, get the
        lock device from the argument.  If an opener device is provided, look
        up the lock device id in the opener's pluginProps and then look up the
        lock device.  Call the internal lock method with the lock device
        obtained either way.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('lockGarageDoor called "%s"', dev.name)

        lkDev = dev  # Assume that dev is a lock device.
        if dev.deviceTypeId == 'opener':  # Not true, dev is an opener device.
            lkDevId = int(dev.pluginProps['lkDevId'])  # Get lock device id.
            lkDev = indigo.devices[lkDevId]  # Get lock device object.
        self._lockGarageDoor(lkDev)

    def unlockGarageDoor(self, pluginAction):
        """
        Unlock a garage door given either a lock device or an opener device.
        If a lock device is referenced in the pluginAction argument, get the
        lock device from the argument.  If an opener device is provided, look
        up the lock device id in the opener's pluginProps and then look up the
        lock device.  Call the internal unlock method with the lock device
        obtained either way.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('unlockGarageDoor called "%s"', dev.name)

        lkDev = dev  # Assume that dev is a lock device.
        if dev.deviceTypeId == 'opener':  # Not true, dev is an opener device.
            lkDevId = int(dev.pluginProps['lkDevId'])  # Get lock device id.
            lkDev = indigo.devices[lkDevId]  # Get lock device object.
        self._unlockGarageDoor(lkDev)

    def actionControlDevice(self, action, dev):
        """
        Implement the device turnOn (close) and turnOff (open) using the
        internal _closeGarageDoor and _openGarageDoor methods.  Log a warning
        message if the device toggle action is selected.  Remote toggling of
        the garage door is not allowed for safety reasons.
        """
        L.threaddebug('actionControlDevice called "%s"', dev.name)
        if action.deviceAction == indigo.kDeviceAction.TurnOn:  # Close/lock.
            if dev.deviceTypeId == 'opener':
                self._closeGarageDoor(dev)
            elif dev.deviceTypeId == 'lock':
                self._lockGarageDoor(dev)

        elif action.deviceAction == indigo.kDeviceAction.TurnOff:  # Open/unlock.
            if dev.deviceTypeId == 'opener':
                self._openGarageDoor(dev)
            elif dev.deviceTypeId == 'lock':
                self._unlockGarageDoor(dev)

        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            warning = ('the toggle action is not allowed for lock or opener '
                       'devices; action ignored')
            L.warning('"%s" %s', dev.name, warning)

    def actionControlUniversal(self, action, dev):
        """
        Implement the requestStatus command by logging the current door or lock
        state.
        """
        L.threaddebug('actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            if dev.deviceTypeId == 'opener':
                L.info('"%s" is %s', dev.name, dev.states['doorStatus'].upper())
            if dev.deviceTypeId == 'lock':
                L.info('"%s" is %s', dev.name, dev.states['lockStatus'].upper())
