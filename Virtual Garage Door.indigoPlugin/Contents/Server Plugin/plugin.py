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
 VERSION:  1.4.1
    DATE:  May 3, 2025

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

The VGD plugin will work only with conventional garage door openers that
automatically reverse when obstructed during a closing cycle.  It will not
accurately track door state transitions in this case for a non-auto-reversing
door.

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
v0.9.5   7/10/2022  Add debug logging of monitored device event sequences and
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
v1.0.5   8/16/2022  Add 'zwRelayType' to RELAY_DEVICE_TYPE_IDs to permit Z-Wave
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
                    the REVERSING state to OPENING to reflect the
                    auto-reversing behavior of the physical door.
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
                    monitored device event within a 1-second time interval.
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
                    (3) Encapsulate travel timer initialization functions into
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
v1.3.10  10/5/2024  Add apcpdu as a switch deviceTypeId.
v1.3.11 10/11/2024  Allow switch devices to be selected as lock devices in
                    ConfigUi's.
v1.4.0   4/20/2025  This is a major release with a number of new capabilities
                    and new ConfigUi's.  Consider it the first beta release of
                    a forthcoming v2.0.  It includes the following changes:
                    (1) Recover gracefully from missing or invalid lock, timer,
                    and monitored devices.
                    (2) Remove lock state constraints on lock/unlock actions.
                    (3) Add optional capabilities to unlock before opening a
                    door and lock after closing a door.
                    (4) Set the initial lock device states based on the states
                    of any options power switch or mechanical lock devices.
                    (5) Add an "AUTOMATIC" menu item to automatically create/
                    use lock and timer devices for an opener.  Make both lock
                    and timer devices optional.
                    (6) Change the menu item "None" to "NO SELECTION" to allow
                    the user to deselect a previously selected menu item.
                    Include this item in all menus except the opener device
                    menu in the lock device ConfigUi.  The opener field is
                    mandatory for the lock device and cannot be deselected.
                    (7) Add significant debug logging for debugging ConfigUi
                    menu interactions with the values dictionary.
                    (8) Add the ESPbuttonType to the relayDeviceTypeIds tuple.
v1.4.1    5/3/2025  (1) Add the ESPbinarySensor to the sensorDeviceTypeIds
                    tuple.
                    (2) Add the ESPswitchType to the switchDeviceTypeIds tuple.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '1.4.1'
__date__ = 'May 3, 2025'

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
    The Plugin class is a collection of standard Indigo plugin and supporting
    methods that are needed to manage/operate multiple door lock/opener
    devices.  It is segmented into six major parts for readability:

    I   CLASS CONSTANTS,
    II  UTILITY METHODS,
    III STANDARD INDIGO INITIALIZATION, STARTUP, AND RUN/STOP METHODS,
    IV  CONFIG UI VALIDATION METHODS,
    V   CONFIG UI CALLBACK METHODS, and
    VI  ACTION CALLBACK METHODS

    A word on class Plugin device references...

    dev generally refers to an opener device, but may in some cases be an
    opener or a lock device (to be determined).
    When more specificity is needed, lkDev and opDev refer to lock and opener
    devices respectively.
    ltDev is used to refer to a device that is either a lock device or a timer
    device.
    devId, lkDevId, opDevId, and ltDevId refer to the various device id's.
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
    #                             CLASS CONSTANTS                             #
    #                                                                         #
    ###########################################################################

    # Miscellaneous:

    AR_CLOSURE_TIME = 0.8  # Activation relay momentary closure time (seconds).
    ON, OFF = (True, False)

    # Door state enumeration, stationary state group, door status, and text
    # door states.

    # The first five door states are the same as those defined in the
    # HMCharacteristicValueDoorState enumeration in the Apple developer HomeKit website:
    # https://developer.apple.com/documentation/homekit/hmcharacteristicvaluedoorstate

    OPEN, CLOSED, OPENING, CLOSING, STOPPED, REVERSING = range(6)
    STATIONARY_STATES = (OPEN, CLOSED, STOPPED)
    DOOR_STATUS = ('open', 'closed', 'opening', 'closing', 'stopped',
                   'reversing')
    DOOR_STATES = [status.upper() for status in DOOR_STATUS]

    # Lock state enumeration, lock status, and text lock states.

    UNLOCKED, LOCKED = (False, True)
    LOCK_STATUS = ('unlocked', 'locked')
    LOCK_STATES = [status.upper() for status in LOCK_STATUS]

    # Lock and timer constants.

    LOCK_PLUGIN_ID = 'net.papamac.indigoplugin.virtualgaragedoor'
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

    # Menu types keyed by field id (Devices.xml).

    MENU_TYPES = {
        'lk': 'lock',             # lock device
        'ar': 'relay',            # activation relay
        'cs': 'sensor',           # closed sensor
        'os': 'sensor',           # open sensor
        'vs': 'sensor',           # vibration sensor
        'tt': 'timer',            # travel timer
        'op': 'opener',           # opener device
        'ps': 'switch',           # physical power switch device
        'ml': 'lock',             # mechanical lock device
        'openingAG': 'action',    # opening action group
        'closingAG': 'action',    # closing action group
        'lockingAG': 'action',    # locking action group
        'unlockingAG': 'action'}  # unlocking action group

    # Relay, sensor, and switch device type id tuples used to generate device
    # selection menus in the getMenuList method (Part V).

    # EasyDAQ devices:

    easyDaqComboTypeIds = ('easyDaq4r4io', 'easyDaq16r8io',
                           'easyDaq8ii4io4r')
    easyDaqRelayTypeIds = ('easyDaq8r', 'easyDaq24r',
                           'easyDaqDo24Stack', 'easyDaqOutputRelay')
    easyDaqSensorTypeIds = ('easyDaq24io',)

    # ESPHome devices:

    espHomeRelayTypeIds = ('ESPbuttonType',)
    espHomeSensorTypeIds = ('ESPbinarySensor',)
    espHomeSwitchTypeIds = ('ESPswitchType',)

    shellyDirectRelayTypeIds = ('shelly1', 'shelly1l',
                                'shelly1pm', 'shelly4pro,'
                                'shellyem', 'shellyem3')
    shellyMQTTRelayTypeIds = ('shelly-1', 'shelly-1pm',
                              'shelly-2-5-relay', 'shelly-2-5-roller',
                              'shelly-4-pro', 'shelly-em-relay',
                              'shelly-uni-relay')

    # Generic devices:

    genericRelayTypeIds = ('digitalOutput', 'pseudoRelay',
                           'zwDimmerType', 'zwRelayType')
    genericSensorTypeIds = ('alarmZone', 'contactSensor',
                            'digitalInput', 'masqSensor',
                            'pseudoRelay', 'zwOnOffSensorType')
    genericSwitchTypeIds = ('apcpdu', 'pseudoRelay', 'relay', 'zwRelayType')

    # Relay, sensor, and switch devices:

    relayDeviceTypeIds = (easyDaqComboTypeIds + easyDaqRelayTypeIds
                          + espHomeRelayTypeIds
                          + shellyDirectRelayTypeIds + shellyMQTTRelayTypeIds
                          + genericRelayTypeIds)
    sensorDeviceTypeIds = (easyDaqComboTypeIds + easyDaqSensorTypeIds
                           + espHomeSensorTypeIds + genericSensorTypeIds)
    switchDeviceTypeIds = espHomeSwitchTypeIds + genericSwitchTypeIds

    # Device type id selection dictionary keyed by VGD field type:

    DEVICE_TYPE_IDs = {'opener': ('opener',),
                       'lock':   ('lock',) + switchDeviceTypeIds,
                       'relay':  relayDeviceTypeIds,
                       'sensor': sensorDeviceTypeIds,
                       'switch': switchDeviceTypeIds,
                       'timer':  ('timer',)}

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
    #                             UTILITY METHODS                             #
    #                                                                         #
    #  def _getOpenerDevice(lkDev)                                            #
    #  def _getLockDevice(opDev)                                              #
    #  def getLockState(self, opDev)                                          #
    #  def _updateLockStatesOnServer(self, lkDev, lockState)                  #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def _getOpenerDevice(lkDev):
        """
        Return the opener device object associated with a lock device.  Use
        the opener device id link in the lock device pluginProps to find the
        opener device in the devices dictionary.  If the opener device id is
        missing or null, or a valid opener device id is not in the devices
        dictionary, return None.
        """
        L.threaddebug(' _getOpenerDevice called "%s"', lkDev.name)

        opDevId = lkDev.pluginProps.get('opDevId')  # Get link to opener dev.
        opDevId = int(opDevId) if opDevId else ''  # Integer device id or ''.
        return indigo.devices.get(opDevId)  # Valid opener device or None.

    @staticmethod
    def _getLockDevice(opDev):
        """
        Return the lock device object associated with an opener device.  Use
        the lock device id link in the opener device pluginProps to find the
        lock device in the devices dictionary.  If the lock device id is
        missing or null, or a valid lock device id is not in the devices
        dictionary, return None.
        """
        L.threaddebug(' _getLockDevice called "%s"', opDev.name)

        lkDevId = opDev.pluginProps.get('lkDevId')  # Get link to lock device.
        lkDevId = int(lkDevId) if lkDevId else ''  # Integer device id or ''.
        return indigo.devices.get(lkDevId)  # Valid lock device or None.

    def getLockState(self, opDev):
        """
        Return the lock state for the lock device associated with an opener
        device.  Use the _getLockDevice method to get the lock device object
        and then return the device onState.  If there is no lock device, then
        return UNLOCKED.
        """
        L.threaddebug('getLockState called "%s"', opDev.name)

        lkDev = self._getLockDevice(opDev)
        return lkDev.onState if lkDev else self.UNLOCKED

    def _updateLockStatesOnServer(self, lkDev, lockState):
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
        L.threaddebug('_updateLockStatesOnServer called "%s"', lkDev.name)

        # Compute and update lock states.

        lockStatus = self.LOCK_STATUS[lockState]
        lkDev.updateStateOnServer('onOffState', lockState, uiValue=lockStatus)
        lkDev.updateStateOnServer('lockStatus', lockStatus)
        L.info('"%s" update to %s', lkDev.name, self.LOCK_STATES[lockState])

        # Compute and update state image.

        image = (indigo.kStateImageSel.Locked if lockState
                 else indigo.kStateImageSel.Unlocked)
        lkDev.updateStateImageOnServer(image)

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
    #      STANDARD INDIGO INITIALIZATION, STARTUP, AND RUN/STOP METHODS      #
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
        monitored devices dictionary and the virtual garage doors dictionary.
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
        #             <ValueType boolType="OnOff">Boolean</ValueType>,
        #   mDevState is the on/off state name to be monitored by the plugin.
        #             For most sensor devices it is typically "onOffState".
        #             For EasyDAQ devices it is "channelnn" where nn is the
        #             numeric channel number.  For timers the state name is
        #             "timerStatus.active", and
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
        #   devId    is the device id of the opener device, and
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
        virtualGarageDoor.py VirtualGarageDoor class which uses the device name
        at the time of initialization.
        """
        devChanged = (oldDev.pluginProps != newDev.pluginProps
                      or oldDev.name != newDev.name)
        return devChanged

    def deviceStartComm(self, dev):
        """
        Start door opener and lock devices.  For each opener device, create a
        new monitored devices dictionary entry and a new virtual garage door
        instance.  Set the initial opener device states based on the initial
        monitored device states.  Check for inconsistency between the initial
        monitored device states and the lock state.

        For each lock device, set the initial lock states based on the states
        of any optional power switch or mechanical lock devices.
        """
        L.threaddebug('deviceStartComm called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':  # Start opener device.

            # Create a new monitored devices dictionary entry for the opener.

            devId = dev.id
            self._monitoredDevices[devId] = {}

            # Add all monitored devices that are selected in the opener device
            # ConfigUi to the monitored devices dictionary.  Save the initial
            # states of the devices for use in setting the initial opener
            # device state.

            mDevStates = {}  # Initial states of monitored devices.
            for mDevType in self.MONITORED_DEVICE_TYPES:
                mDevId = dev.pluginProps[mDevType + 'DevId']
                if mDevId:  # Monitored device is selected in the ConfigUi.
                    mDevId = int(mDevId)

                    # Check the monitored device id and state name.  If there
                    # are any errors, log a warning message and exclude the
                    # monitored device from the monitored devices dictionary.

                    mDev = indigo.devices.get(mDevId)
                    if not mDev:
                        L.warning('"%s" mDevId %s is not in the devices dict; '
                                  '%s device will not be monitored',
                                  dev.name, mDevId, mDevType)
                        continue

                    if not mDev.enabled:
                        L.warning('"%s" monitored device "%s" is not enabled; '
                                  '%s device will not be monitored',
                                  dev.name, mDev.name, mDevType)
                        continue

                    mDevStateName = dev.pluginProps[mDevType + 'State']
                    if mDevStateName not in mDev.states:
                        L.warning('"%s" "%s" state %s is not in the states '
                                  'dict; %s device will not be monitored',
                                  dev.name, mDev.name, mDevStateName, mDevType)
                        continue

                    # Add a new entry in the monitored devices dictionary.

                    if not self._monitoredDevices[devId].get(mDevId):
                        self._monitoredDevices[devId][mDevId] = {}
                    self._monitoredDevices[devId][mDevId][mDevStateName] = mDevType

                    # Get the normalized state of the monitored device.

                    invert = dev.pluginProps.get(mDevType + 'Invert', False)
                    mDevStates[mDevType] = mDev.states.get(mDevStateName) ^ invert

            L.debug(self._monitoredDevices[devId])
            L.debug(mDevStates)

            # Guess the starting door state.  Assume that door is not in motion
            # and that it is closed unless the closed sensor is off and open
            # sensor is on.  Update the door states on the server.

            csState = mDevStates.get('cs')
            osState = mDevStates.get('os')
            doorState = self.OPEN if not csState and osState else self.CLOSED

            # Check for inconsistency between the door and lock states.

            if doorState is self.OPEN and self.getLockState(dev) is self.LOCKED:
                L.warning('"%s" initial state is open and locked; close the '
                          'door manually, or unlock it')

            # Instantiate a VirtualGarageDoor object for the device and save
            # the object in the virtual garage doors dictionary.

            vgd = VirtualGarageDoor(self, dev, doorState)
            self._virtualGarageDoors[devId] = vgd

        elif dev.deviceTypeId == 'lock':  # Start lock device.

            # Get optional power switch state (defaults to ON).

            ps = dev.pluginProps.get('ps')
            psDev = indigo.devices.get(ps)
            psState = (psDev.states.get('onOffState', self.ON) if psDev
                       else self.ON)

            # Get optional mechanical lock state (defaults to OFF).

            ml = dev.pluginProps.get('ml')
            mlDev = indigo.devices.get(ml)
            mlState = mlDev.states.get('onOffState') if mlDev else self.OFF

            # Set lock state to ON if the power switch is OFF or the mechanical
            # lock is ON.

            lockState = not psState or mlState
            self._updateLockStatesOnServer(dev, lockState)

    def deviceStopComm(self, dev):
        """
        Retire door opener devices by deleting the entries in the monitored
        devices dictionary and the virtual garage doors dictionary, if present.
        Lock devices do not require any special action.
        """
        L.threaddebug('deviceStopComm called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':
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
    #                             III   III     III                           #
    #                              I     I       I                            #
    #                              I      I     I                             #
    #                              I       I   I                              #
    #                              I        I I                               #
    #                             III       III                               #
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
        Validate opener and lock device ConfigUi's.  Complete device
        configuration by creating new devices and updating valuesDict/
        pluginProps values as needed.

        For an opener device, initialize the optional lock device and travel
        timer device if they are selected in the ConfigUi.  In both cases,
        create a new device with a standard name if "New" is specified as the
        device name.  Link the lock device bidirectionally with the opener
        device and validate the locking/unlocking delay times.

        Validate all manual (non-menu) entries in the ConfigUi.  For each
        monitored device that is selected in the ConfigUi, check the device and
        its on/off state name to ensure that the device exists and its on/off
        state name is in the device's states dictionary. Also check to ensure
        that a particular device name/state name combination is not reused in
        any other monitored device ConfigUi for all opener devices.  Add
        configuration flags, monitored device id's, and initial monitored
        device states to the values dictionary for use by other methods.
        Validate the opening and closing delay times.

        For a lock device, if an opener device is selected, link the lock
        device bidirectionally with the opener device.  If no opener device is
        selected, the lock device will not constrain opener device operation
        until it is subsequently linked by activating either an opener or lock
        device ConfigUi.  In either case, validate the locking/unlocking delay
        times.

        Throughout the method, when errors are found, add an error message to
        the errors dictionary in keeping with the standard Indigo validation
        protocol.  Return the values dictionary and the errors dictionary.
        """

        # Debug functions.

        def _null(text):
            return 'Null' if text == '' else text

        def _logProps(lt='lk'):
            """
            Debug log device names, config flags and device id's for lock and
            timer devices.  Log values from both the values dictionary and the
            device plugin props.
            """
            ltName = _null(valuesDict.get(lt))
            ltConfig = _null(valuesDict.get(lt + 'Config'))
            ltDevId = _null(valuesDict.get(lt + 'DevId'))
            L.debug('"%s" valuesDict %s "%s" %s %s',
                    dev.name, lt, ltName, ltConfig, ltDevId)
            ltName = _null(dev.pluginProps.get(lt))
            ltConfig = _null(dev.pluginProps.get(lt + 'Config'))
            ltDevId = _null(dev.pluginProps.get(lt + 'DevId'))
            L.debug('"%s" pluginProps %s "%s" %s %s',
                    dev.name, lt, ltName, ltConfig, ltDevId)

        # Local support functions:

        def _getProps():
            """
            Get lock device plugin props from the opener or lock device values
            dictionary.  Also include the device name and device id fields used
            to link the opener device to the lock device and vice versa.  If
            the typeId is opener include the opener device name and device id.
            If the typeId is lock include the lock device name and device id.
            """
            fieldId = 'op' if typeId == 'opener' else 'lk'

            return {fieldId:           dev.name,
                    fieldId + 'DevId': str(devId),
                    'ps':              valuesDict.get('ps', ''),
                    'ml':              valuesDict.get('ml', ''),
                    'lockingAG':       valuesDict.get('lockingAG', ''),
                    'lockingDT':       valuesDict.get('lockingDT', '0.0'),
                    'unlockingAG':     valuesDict.get('unlockingAG', ''),
                    'unlockingDT':     valuesDict.get('unlockingDT', '0.0')}

        def _validateActionDT(action, maxDT=10.0):
            """
            Validate the delay time value associated with a VGD action.  Add an
            error message to the errors dictionary if the delay time is less
            than 0.0 or greater than maxDelay.  The action must be opening,
            closing, locking, or unlocking.
            """
            delayFieldId = action + 'DT'
            delayTime = -1  # Force an error if the try fails.
            try:
                delayTime = float(valuesDict[delayFieldId])
            except ValueError:
                pass
            if not 0 <= delayTime <= maxDT:
                err = ('%s delay time must be a number between 0.0 and %.1f '
                       'seconds' % (action.capitalize(), maxDT))
                errorsDict[delayFieldId] = err

        # validateDeviceConfigUi initial debug.

        dev = indigo.devices[devId]
        L.threaddebug('validateDeviceConfigUi called "%s"', dev.name)
        L.debug(valuesDict)
        _logProps('lk')
        _logProps('tt')
        errorsDict = indigo.Dict()

        # Begin configuration and validation for opener and lock devices.

        if typeId == 'opener':  # Configure and validate an opener device.

            # Optionally configure a lock device using the opener device plugin
            # props.

            valuesDict['lkDevId'] = ''  # Set default to no lock device.
            lk = valuesDict['lk']
            if lk:  # Existing lock device or automatic device.
                props = _getProps()

                lkDev = indigo.devices.get(lk)
                if lkDev:  # Existing device; replace plugin props on server.
                    lkProps = lkDev.pluginProps
                    for prop in props:
                        lkProps[prop] = props[prop]
                    lkDev.replacePluginPropsOnServer(lkProps)

                else:  # No device in dictionary; create a new one.
                    description = ('Automatically generated lock device for '
                                   '"%s"' % dev.name)
                    lkDev = indigo.device.create(
                                protocol=indigo.kProtocol.Plugin,
                                name=lk,
                                description=description,
                                pluginId=self.LOCK_PLUGIN_ID,
                                deviceTypeId='lock',
                                props=props,
                                folder='doors')

                if lkDev.enabled:  # Lock device successfully configured.
                    valuesDict['lkDevId'] = lkDev.id  # Add lk link to opener.
                else:  # Lock device configuration error.
                    errorsDict['lk'] = 'Lock configuration error.'

            # Optionally configure a travel timer (tt) device.

            valuesDict['ttDevId'] = ''  # Set default to no timer device.
            tt = valuesDict['tt']
            if tt:  # Existing timer device or automatic device.
                ttDev = indigo.devices.get(tt)
                if not ttDev:  # No existing device; create new auto device.
                    description = ('Automatically generated timer device for '
                                   '"%s"' % dev.name)
                    props = dict(amount=1.0, amountType='seconds')
                    indigo.device.create(
                        protocol=indigo.kProtocol.Plugin,
                        name=tt,
                        description=description,
                        pluginId=self.TIMER_PLUGIN_ID,
                        deviceTypeId='timer',
                        props=props,
                        folder='doors')

            # Optional configuration of lock and timer devices is complete;
            # begin validation of monitored devices.

            # Clear self._monitoredDevices for this opener to prevent previous
            # device configurations from generating ConfigUi errors.

            self._monitoredDevices[devId] = {}

            # For each monitored device that is selected in the opener device
            # ConfigUi:

            # (1) Validate the device name.
            # (2) Ensure that the device is configured (enabled)
            # (3) Validate the state name.
            # (4) Ensure that selected device name/state pair is unique among
            #     all monitored device types for all opener devices.
            # (5) Validate unique fields for vs and tt devices.
            # (6) Set the device id field in the values dictionary.

            mDevConfig = ''
            for mDevType in self.MONITORED_DEVICE_TYPES:
                valuesDict[mDevType + 'DevId'] = ''
                mDevName = valuesDict[mDevType]
                if mDevName:  # Monitored device is selected in the ConfigUi.

                    # Validate the device name.

                    mDev = indigo.devices.get(mDevName)
                    if not mDev:
                        error = '"%s" not in the devices dictionary' % mDevName
                        errorsDict[mDevType] = error
                        continue

                    if not mDev.enabled:
                        error = '"%s" configuration error' % mDevName
                        errorsDict[mDevType] = error
                        continue

                    # Validate the state name.

                    mDevStateKey = mDevType + 'State'
                    mDevStateName = valuesDict[mDevStateKey]
                    if mDevStateName not in mDev.states:
                        error = ('%s not in device states dictionary'
                                 % mDevStateName)
                        errorsDict[mDevStateKey] = error
                        continue

                    # Check to ensure that no device/state pairs are reused by
                    # this opener device or others.

                    mDevId = mDev.id
                    for devId_ in self._monitoredDevices:
                        for mDevId_ in self._monitoredDevices[devId_]:
                            for mDevStateName_ in self._monitoredDevices[devId_][mDevId_]:
                                if mDevId == mDevId_ and mDevStateName == mDevStateName_:
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
                            error = ('Reset delay time must be an integer '
                                     'between 0 and 4 seconds')
                            errorsDict['vsResetDelay'] = error
                            continue

                    # Validate the travel time entry and update the timer start
                    # value.

                    if mDevType == 'tt':
                        tTime = 0  # Force an error if try fails.
                        try:
                            tTime = float(valuesDict['tTime'])
                        except ValueError:
                            pass
                        if not 8 <= tTime <= 20:  # Invalid entry; set error.
                            error = ('Travel time must be a number between 8 '
                                     'and 20 seconds')
                            errorsDict['tTime'] = error
                            continue
                        else:  # Good travel time; set the timer start value.
                            self.TIMER.executeAction('setTimerStartValue',
                                deviceId=mDevId,
                                props=dict(amount=tTime, amountType='seconds'))

                    # No error for this monitored device/state.  Set the
                    # monitored device id in the values dictionary and add the
                    # monitored device type to the monitored device
                    # configuration.

                    valuesDict[mDevType + 'DevId'] = str(mDevId)
                    mDevConfig += mDevType + ' '

                    # Add keys/values to self._monitoredDevices to mark this
                    # device/state combination as used.  Note that these
                    # additions are overwritten (with the same data) when the
                    # opener device is started.

                    if not self._monitoredDevices[devId].get(mDevId):
                        self._monitoredDevices[devId][mDevId] = {}
                    self._monitoredDevices[devId][mDevId][mDevStateName] = mDevType
                    L.debug(self._monitoredDevices[devId])

            # All mDevTypes validated. Set the monitored device configuration
            # in the values dictionary.

            valuesDict['mDevConfig'] = mDevConfig

            # Validate action delay times.

            for action_ in ('opening', 'closing', 'locking', 'unlocking'):
                _validateActionDT(action_)

        elif typeId == 'lock':  # Configure and validate a lock device.
            op = valuesDict['op']
            if op:  # Opener device was selected.

                # Replace opener device plugin props (including lock device
                # name and device id).

                props = _getProps()
                opDev = indigo.devices[op]
                opProps = opDev.pluginProps
                for prop in props:
                    opProps[prop] = props[prop]
                opDev.replacePluginPropsOnServer(opProps)

            else:  # No opener device selected.
                errorsDict['op'] = 'Opener device is required'

            # Validate locking/unlocking delay times.

            _validateActionDT('locking')
            _validateActionDT('unlocking')

        # validateDeviceConfigUi ending debug.

        L.debug(valuesDict)
        L.debug(errorsDict)
        _logProps('lk')
        _logProps('tt')

        # Return with or without errors.

        return not bool(errorsDict), valuesDict, errorsDict

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                               III     III                               #
    #                                I       I                                #
    #                                 I     I                                 #
    #                                  I   I                                  #
    #                                   I I                                   #
    #                                   III                                   #
    #                                                                         #
    #                       CONFIG UI CALLBACK METHODS                        #
    #                                                                         #
    #  def getMenuList(self, filter_, valuesDict, typeId, devId)              #
    #  def updateDynamicConfigValues(self, valuesDict, typeId, devId)         #
    #                                                                         #
    ###########################################################################

    def getMenuList(self, fieldId, valuesDict, typeId, devId):
        """
        Create and return a menu list for the action group and device selection
        menus in the opener and lock device ConfigUi's.

        Select action group or device names based on the value of the filter_
        argument passed by the ConfigUi list specification.  Valid filter_
        arguments are 'action', 'relay', 'sensor', 'switch', 'timer', 'opener',
        and 'lock'.

        For the 'action' filter, select all action groups from the Indigo
        action groups dictionary.

        For the 'relay', 'sensor', 'switch', 'timer', and 'opener' filters,
        select devices from the Indigo devices dictionary that have a
        device type id in the self.DEVICE_TYPE_IDs[filter_] tuple.

        For the 'lock' filter select devices that have a subType attribute with
        a value of 'Lock' or select switch devices.  Allowing switch devices to
        be selected for the 'lock' filter permits a switch to be used to
        control a powered custom lock device.

        Choose up to two user options to be added at the bottom of the menu
        list following the selected action group or device names.  For the
        opener filter do not include any user options.  For all other filters
        include a 'None' option to let the user de-select a prior action group
        or device selection.  For timer and lock filters, also add a 'New'
        option to let the user create a new device.

        Return a menu list consisting of user options followed by a sorted list
        of action group or device names.
        """
        dev = indigo.devices[devId]
        L.threaddebug('getMenuList called "%s" field id = %s',
                      dev.name, fieldId)

        names = []  # Action group or device names.
        menuType = self.MENU_TYPES[fieldId]

        if menuType == 'action':  # Select action groups.
            for actionGroup in indigo.actionGroups.iter('self'):
                names.append(actionGroup.name)

        else:  # Select devices.
            for dev_ in indigo.devices:
                if dev_.deviceTypeId in self.DEVICE_TYPE_IDs[menuType]:
                    names.append(dev_.name)

        # Generate and return menu list with "AUTOMATIC" and "NO SELECTION"
        # optionS.

        menuList = [(name, name) for name in sorted(names)]

        if fieldId in ('lk', 'tt'):  # "AUTOMATIC" option for lk and tt.

            # Derive an automatic device name from the opener device name and
            # the menu type ('lock' or 'timer').

            if dev.name == 'new device':  # Opener device is new.
                autoDevName = 'new %s device' % menuType
            elif dev.name.endswith('-opener'):
                autoDevName = dev.name[:-7] + '-' + menuType
            else:
                autoDevName = dev.name + '-' + menuType

            # Add "AUTOMATIC" option.

            menuList.append((autoDevName, 'AUTOMATIC'))

        if fieldId != 'op' and valuesDict.get(fieldId):  # "NO SELECTION"
            menuList.append(('None', 'NO SELECTION'))

        return menuList

    def updateDynamicConfigValues(self, valuesDict, typeId, devId):
        """
        Respond to a user selection of any value in a lock or opener ConfigUi
        menu.  These can be either action group or device
        selection menus that are generated by the getMenuList method.  The field id's for the dynamic
        list fields must be included in the self.MENU_TYPES dictionary
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
        not selected, or displayed if it is selected.

        If the initial value of a field is the null string leave the values
        dictionary unchanged.
        """
        dev = indigo.devices[devId]
        L.threaddebug('updateDynamicConfigValues called "%s"', dev.name)

        # Deselect the first field with a value of 'None'.

        for fieldId in self.MENU_TYPES:
            if valuesDict.get(fieldId) == 'None':
                valuesDict[fieldId] = ''
                break

        # For an opener device ConfigUi, update xxConfig fields for monitored
        # devices and the lock device.

        if typeId == 'opener':
            for fieldId in self.MONITORED_DEVICE_TYPES + ('lk',):
                valuesDict[fieldId + 'Config'] = (
                    'true' if valuesDict[fieldId] else 'false')

        return valuesDict

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                           III     III   III                             #
    #                            I       I     I                              #
    #                             I     I      I                              #
    #                              I   I       I                              #
    #                               I I        I                              #
    #                               III       III                             #
    #                                                                         #
    #                         ACTION CALLBACK METHODS                         #
    #                                                                         #
    #                     Internal Action Support Methods                     #
    #                                                                         #
    #  def _toggleActivationRelay(self, opDev)                                #
    #  def _executeOptionalActions(dev, action='opening')                     #
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

        arDevId = opDev.pluginProps['arDevId']
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
    def _executeOptionalActions(dev, action='opening'):
        """
        dev can be an opener or lock device.  action must be opening, closing,
        locking, or unlocking.

        Optionally execute an action group and delay based on opener or lock
        device pluginProps entries.  Do nothing if the action group or delay
        keys are not in the pluginProps dictionary.  This ensures backward
        compatibility with opener or lock devices created by older plugin
        versions.
        """
        L.threaddebug('_executeOptionalActions called "%s"', dev.name)

        actionGroup = dev.pluginProps.get(action + 'AG')
        if actionGroup:
            indigo.actionGroup.execute(actionGroup)

        delayTime = dev.pluginProps.get(action + 'DT')
        if delayTime:
            sleep(float(delayTime))

    def _openGarageDoor(self, opDev):
        """
        Execute optional opening actions and open the door if it is unlocked
        and currently closed.  Unlock the door before opening if requested.
        """
        L.threaddebug('_openGarageDoor called "%s"', opDev.name)

        # Unlock before opening if requested.

        if opDev.pluginProps.get('unlockBeforeOpening'):  # Unlock requested.
            lkDev = self._getLockDevice(opDev)
            if lkDev:  # Valid lock device; unlock it.
                self._unlockGarageDoor(lkDev)

                # Delay at least 5 seconds for the lock to unlock.  If an
                # opening delay is specified, additional delay is needed only
                # if the opening delay is less than 1 second.

                openingDT = opDev.pluginProps.get('openingDT')
                openingDT = float(openingDT) if openingDT else 0.0
                if openingDT < 5.0:
                    sleep(5.0 - openingDT)

            else:  # No lock device linked to opener.
                L.warning('"%s" no lock device linked to opener; unlock '
                          'before opening ignored', opDev.name)

        # Check the lock state.

        if self.getLockState(opDev):  # Abort if locked.
            L.warning('"%s" attempt to open the garage door when it is '
                      'locked; action ignored', opDev.name)
            return

        # Check the door state.

        doorState = opDev.states['doorState']
        if doorState != self.CLOSED:  # Abort if not closed.
            L.warning('"%s" attempt to open the garage door when it is '
                      'not closed; action ignored', opDev.name)

        else:  # Execute optional opening actions and toggle the door open.
            self._executeOptionalActions(opDev)
            self._toggleActivationRelay(opDev)

    def _closeGarageDoor(self, opDev):
        """
        Close the door and execute optional closing actions if it is unlocked
        and currently open or stopped.  Lock the door after closing if
        requested.
        """
        L.threaddebug('_closeGarageDoor called "%s"', opDev.name)

        doorState = opDev.states['doorState']

        # Check the lock state.

        if self.getLockState(opDev):  # Abort if locked.
            L.warning('"%s" attempt to close the garage door when it is '
                      'locked; action ignored', opDev.name)

        # Check the door state.

        elif doorState == self.CLOSED:  # Abort if already closed.
            L.warning('"%s" attempt to close the garage door when it is '
                      'already closed; door action ignored', opDev.name)

        elif doorState not in self.STATIONARY_STATES:  # Abort if moving.
            L.warning('"%s" attempt to close the garage door when it is '
                      'moving; door action ignored', opDev.name)

        else:  # Execute optional closing actions and toggle the door closed.
            self._executeOptionalActions(opDev, action='closing')
            self._toggleActivationRelay(opDev)

    def _lockGarageDoor(self, lkDev):
        """
        Lock the garage door if it is closed.  If there is no link to an opener
        device or, the door is not closed, log a warning message and return.

        Optionally execute locking actions to (1) turn off the garage door
        opener power, (2) turn on (lock) a garage door mechanical lock, and
        (3) execute a user-specified locking action group.  Log a warning
        message and return if any of the optional actions fails to execute.

        If there are no exceptions, set the lock device states on the server to
        locked.
        """
        L.threaddebug('_lockGarageDoor called "%s"', lkDev.name)

        opDev = self._getOpenerDevice(lkDev)
        if not opDev:  # Abort if no opener device.
            L.warning('"%s" lock device is not linked to an opener device; '
                      'action ignored', lkDev.name)
            return

        if opDev.states['doorState'] != self.CLOSED:  # Abort if not closed.
            L.warning('"%s" attempt to lock the garage door when it is not '
                      'closed; action ignored', lkDev.name)
            return

        # Execute optional locking actions in order (1) power switch off,
        # (2) mechanical lock on, and (3) locking action group and delay.

        try:
            ps = lkDev.pluginProps.get('ps')
            if ps:
                indigo.device.turnOff(ps)

            ml = lkDev.pluginProps.get('ml')
            if ml:
                indigo.device.turnOn(ml)

            self._executeOptionalActions(lkDev, action='locking')

        except Exception as warningMessage:
            L.warning('"%s" optional locking action failed: %s',
                      lkDev.name, warningMessage)

        else:  # Update lock device states.
            self._updateLockStatesOnServer(lkDev, self.LOCKED)

    def _unlockGarageDoor(self, lkDev):
        """
        Unlock the garage door if it is closed.  If there is no link to an
        opener device or, the door is not closed, log a warning message and
        return.

        Optionally execute unlocking actions to (1) execute a user-specified
        unlocking actin group, (2) turn off (unlock) a garage door mechanical
        lock, and (3) turn on the garage door opener power.  Log a warning
        message and return if any of the optional actions fails to execute.

        If there are no exceptions, set the lock device states on the server to
        unlocked.
        """
        L.threaddebug('unlockGarageDoor called "%s"', lkDev.name)

        opDev = self._getOpenerDevice(lkDev)
        if not opDev:  # Abort if no opener device.
            L.warning('"%s" lock device is not linked to an opener device;'
                      'unlock action ignored', lkDev.name)
            return

        if opDev.states['doorState'] != self.CLOSED:  # Abort if not closed.
            L.warning('"%s" attempt to unlock the garage door when it is not '
                      'closed; action ignored', lkDev.name)
            return

        # Execute optional unlocking actions in order (1) mechanical lock off,
        # (2) power switch on, and (3) unlocking action group and delay.

        try:
            ml = lkDev.pluginProps.get('ml')
            if ml:
                indigo.device.turnOff(ml)

            ps = lkDev.pluginProps.get('ps')
            if ps:
                indigo.device.turnOn(ps)

            self._executeOptionalActions(lkDev, action='unlocking')

        except Exception as warningMessage:
            L.warning('"%s" optional unlocking action failed: %s',
                      lkDev.name, warningMessage)

        else:  # Update lock device states.
            self._updateLockStatesOnServer(lkDev, self.UNLOCKED)

    def openGarageDoor(self, pluginAction):
        """
        Get the device from the pluginAction argument and call the internal
        open method.  Log a warning message if the pluginAction device is not
        an opener.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('openGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':  # dev is an opener device; open it.
            self._openGarageDoor(dev)
        else:  # Abort if not an opener.
            L.warning('"%s" open action requested for a non-opener device; '
                      'action ignored', dev.name)

    def closeGarageDoor(self, pluginAction):
        """
        Get the device from the pluginAction argument and call the internal
        close method.  Log a warning message if the pluginAction device is not
        an opener.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('closeGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':  # dev is an opener device; close it.
            self._closeGarageDoor(dev)
        else:  # Abort if not an opener.
            L.warning('"%s" close action requested for a non-opener device; '
                      'action ignored', dev.name)

    def lockGarageDoor(self, pluginAction):
        """
        Lock a garage door given either a lock device or an opener device.
        If a lock device is provided in the pluginAction argument, use the
        lock device from the argument.  If an opener device is provided, use
        the lock device obtained from the _getLockDevice method.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('lockGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'lock':  # dev is a lock device; lock it.
            self._lockGarageDoor(dev)

        elif dev.deviceTypeId == 'opener':  # dev is an opener device.
            lkDev = self._getLockDevice(dev)
            if lkDev:  # Valid lock device, lock it.
                self._lockGarageDoor(lkDev)
            else:  # Abort if no lock.
                L.warning('"%s" no available lock device; action ignored',
                          dev.name)

    def unlockGarageDoor(self, pluginAction):
        """
        Unlock a garage door given either a lock device or an opener device.
        If a lock device is provided in the pluginAction argument, use the
        lock device from the argument.  If an opener device is provided, use
        the lock device obtained from the _getLockDevice method.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('unlockGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'lock':  # dev is a lock device; unlock it.
            self._unlockGarageDoor(dev)

        elif dev.deviceTypeId == 'opener':  # dev is an opener device.
            lkDev = self._getLockDevice(dev)
            if lkDev:  # Valid lock device, unlock it.
                self._unlockGarageDoor(lkDev)
            else:  # Abort if no lock.
                L.warning('"%s" no available lock device; action ignored',
                          dev.name)

    def actionControlDevice(self, action, dev):
        """
        Implement the device turnOn (close) and turnOff (open) using the
        internal _closeGarageDoor and _openGarageDoor methods.  Log a warning
        message if the device toggle action is selected.  Remote toggling of
        the garage door is not allowed for safety reasons.
        """
        L.threaddebug('actionControlDevice called "%s"', dev.name)

        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            if dev.deviceTypeId == 'opener':  # dev is opener device; close it.
                self._closeGarageDoor(dev)
            elif dev.deviceTypeId == 'lock':  # dev is a lock device; lock it.
                self._lockGarageDoor(dev)

        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            if dev.deviceTypeId == 'opener':  # dev is opener device; open it.
                self._openGarageDoor(dev)
            elif dev.deviceTypeId == 'lock':  # dev is lock device; unlock it.
                self._unlockGarageDoor(dev)

        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            L.warning('"%s" toggling not allowed for opener or lock devices; '
                      'action ignored', dev.name)

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
