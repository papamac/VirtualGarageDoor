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
 VERSION:  1.5.0
    DATE:  August 4, 2025

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
v0.9.3   6/30/2022  Modify the deviceStartComm and validateDeviceConfigUI
                    methods to initialize and validate the travel timer in the
                    same way as other monitored devices.  Move the timer device
                    creation from deviceStartComm to validateDeviceConfigUI and
                    use a travel timer device name based on the opener device
                    name.  Add device selection menu callback methods for all
                    monitored device types to facilitate optional device
                    selection in the opener ConfigUI.
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
                    (3) Improve error detection and reporting during ConfigUI
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
                    requires that the door be CLOSED before the open action is
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
                    checkbox in the pluginPrefs ConfigUI.  These events should
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
                    (5) Consolidate multiple ConfigUI callback methods (one for
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
                    validateDeviceConfigUI.
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
                    ConfigUIs.
v1.4.0   4/20/2025  This is a major release with a number of new capabilities
                    and new ConfigUIs.  Consider it the first beta release of
                    a forthcoming v2.0.  It includes the following changes:
                    (1) Recover gracefully from missing or invalid lock, timer,
                    and monitored devices.
                    (2) Remove lock state constraints on lock/unlock actions.
                    (3) Add optional capabilities to unlock before opening a
                    door and lock after closing a door.
                    (4) Set the startup lock device states based on the states
                    of any options power switch or mechanical lock devices.
                    (5) Add an 'AUTOMATIC' menu item to automatically create/
                    use lock and timer devices for an opener.  Make both lock
                    and timer devices optional.
                    (6) Change the menu item 'None' to 'NO SELECTION' to allow
                    the user to deselect a previously selected menu item.
                    Include this item in all menus except the opener device
                    menu in the lock device ConfigUI.  The opener field is
                    mandatory for the lock device and cannot be deselected.
                    (7) Add significant debug logging for debugging ConfigUI
                    menu interactions with the values dictionary.
                    (8) Add the ESPbuttonType to the relayDeviceTypeIds tuple.
v1.4.1    5/3/2025  (1) Add the ESPbinarySensor to the sensorDeviceTypeIds
                    tuple.
                    (2) Add the ESPswitchType to the switchDeviceTypeIds tuple.
v1.5.0    8/4/2025  (1) Replace the opener device STOPPED and REVERSING states
                    with a new OBSTRUCTED state.
                    (2) Change the nomenclature for the VGD lock device to the
                    virtual lock device.  Change lock references from lk,
                    lkDevId, and lkDev to vl, vlDevId, and vlDev.
                    (3) Add the virtual lock (vl), latch sensor (ls), power
                    switch (ps), and mechanical lock to the monitored device
                    types tuple, the menu types dictionary, and the monitored
                    devices dictionary.
                    (4) During opener device startup in the deviceStartComm
                    method, log the monitored devices that were configured
                    along with their startup states.
                    (5) Add ls and lsConfig to the _getVirtualLockProps method.
                    (6) Add an ignored events tuple used to bypass the updating
                    of the door state for those events that do not trigger door
                    state transitions.
                    (7) Update the startup door status and lock state logic
                    id the deviceStartComm method.
                    (8) Add the IsLockSubType property to the plugin props when
                    a lock device is created.
                    (9) Implement the lock and unlock device actions for the
                    lock device.
                    (10) Deselect all physical lock devices (ls, ps, and ml)
                    if the virtual lock device (vl) is deselected.
                    (11) Replace the common updateDynamicConfigValues method
                    with 13 simpler xxSelected methods, one for each ConfigUI
                    field group id sans the opener group which has no callback
                    method (see Devices.xml).
                    (12) Optionally log lock state changes based on a new
                    checkbox field in the lock device ConfigUI.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '1.5.0'
__date__ = 'August 4, 2025'

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
    When more specificity is needed, vlDev and opDev refer to virtual lock and
    opener devices respectively.
    ltDev is used to refer to a device that is either a virtual lock device or
    a timer device.
    devId, vlDevId, opDevId, and ltDevId refer to the various device id's.
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

    # Door state/status definitions:

    # The opener device doorState is an integer state variable with values
    # defined by the following enumeration:

    OPEN, CLOSED, OPENING, CLOSING, OBSTRUCTED = range(5)

    # The doorState is used by the HomiKitLink Siri plugin (HKLS) as the
    # preferred device state variable to track the door operation in Apple
    # HomeKit.  The first four door states are the same as those defined in the
    # HMCharacteristicValueDoorState enumeration in the Apple developer HomeKit website:
    # https://developer.apple.com/documentation/homekit/hmcharacteristicvaluedoorstate

    # The fifth state, OBSTRUCTED, includes the Apple STOPPED state.  It is,
    # however, broader in scope to include both the stopping/reversing actions
    # of the physical door opener and various types of locking device actions
    # when the door is not CLOSED.  In the OBSTRUCTED state the physical door
    # can in any position.  It can be stationary, or it can be moving toward a
    # stationary state.  Once in the OBSTRUCTED state, normal door operation
    # can only be restored by automatically/manually moving the door to the
    # CLOSED position and sometimes only by reloading the VGD plugin.

    # The opener device door status is a lower case text state variable with
    # values of 'open', 'closed', 'opening', 'closing', 'obstructed', and
    # 'closed-lk'.  It is used as the uiValue for the State in the device list
    # of the Indigo home window.  It is also used to key the
    # DOOR_STATE_TRANSITIONS data structure in the VirtualGarageDoor class and
    # to provide the door state in logged messages.  The following tuple is
    # used to set the startup door status using the startup door state.

    DOOR_STATUS = ('open', 'closed', 'opening', 'closing', 'obstructed')

    # Virtual lock state enumeration and lock status definition:

    UNLOCKED, LOCKED = (False, True)
    LOCK_STATUS = ('unlocked', 'locked')

    # Timer and virtual lock constants.

    TIMER_PLUGIN_ID = 'com.perceptiveautomation.indigoplugin.timersandpesters'
    TIMER = indigo.server.getPlugin(TIMER_PLUGIN_ID)
    VIRTUAL_LOCK_PLUGIN_ID = 'net.papamac.indigoplugin.virtualgaragedoor'

    # Monitored device types ids used in deviceStartComm and
    # validateDeviceConfigUi methods.

    MONITORED_DEVICE_TYPE_IDs = (
        'ar',  # 1. activation relay
        'cs',  # 2. closed sensor
        'os',  # 3. open sensor
        'vs',  # 4. vibration sensor
        'tt',  # 5. travel timer
        'vl',  # 6. virtual lock
        'ls',  # 7. latch sensor
        'ps',  # 8. power switch
        'ml')  # 9. mechanical lock

    # Relay, sensor, and switch device type id tuples used to generate device
    # selection menus in the getMenuList method (Part V).

    # EasyDAQ devices:

    easyDaqComboTypeIds = ('easyDaq4r4io', 'easyDaq16r8io', 'easyDaq8ii4io4r')
    easyDaqRelayTypeIds = ('easyDaq8r', 'easyDaq24r', 'easyDaqDo24Stack',
                           'easyDaqOutputRelay')
    easyDaqSensorTypeIds = ('easyDaq24io',)

    # ESPHome devices:

    espHomeRelayTypeIds = ('ESPbuttonType',)
    espHomeSensorTypeIds = ('ESPbinarySensor',)
    espHomeSwitchTypeIds = ('ESPswitchType',)

    # Shelly devices:

    shellyDirectRelayTypeIds = ('shelly1', 'shelly1l', 'shelly1pm',
                                'shelly4pro', 'shellyem', 'shellyem3')
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

    # Device type id selection dictionary keyed by menu type:

    DEVICE_TYPE_IDs = {'relay':       relayDeviceTypeIds,
                       'sensor':      sensorDeviceTypeIds,
                       'timer':       ('timer',),
                       'virtualLock': ('lock',),
                       'switch':      switchDeviceTypeIds,
                       'lock':        ('lock',) + switchDeviceTypeIds,
                       'opener':      ('opener',)}

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
    #  def _getOpenerDevice(vlDev)                                            #
    #  def _getVirtualLockDevice(opDev)                                       #
    #  def _getLatchSensorState(self, opDev)                                  #
    #  def _getVirtualLockState(self, opDev)                                  #
    #  def _updateVirtualLockStatesOnServer(self, vlDev, newLockState)        #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def _getOpenerDevice(vlDev):
        """
        Return the opener device object associated with a lock device.  Use
        the opener device id link in the lock device pluginProps to find the
        opener device in the devices dictionary.  If the opener device id is
        null, or a valid opener device id is not in the devices dictionary,
        return None.
        """
        L.threaddebug(' _getOpenerDevice called "%s"', vlDev.name)

        opDevId = vlDev.pluginProps['opDevId']  # Get link to opener dev.
        return indigo.devices.get(int(opDevId)) if opDevId else None

    @staticmethod
    def _getVirtualLockDevice(opDev):
        """
        Return the virtual lock (vl) device object associated with an opener
        device.  Use the vl device id link in the opener device pluginProps to
        find the vl device in the devices dictionary.  If the vl device id is
        null, or a valid vl device id is not in the devices dictionary, return
        None.
        """
        L.threaddebug('_getVirtualLockDevice called "%s"', opDev.name)

        vlDevId = opDev.pluginProps['vlDevId']  # Get link to vl device.
        return indigo.devices.get(int(vlDevId)) if vlDevId else None

    def _getLatchSensorState(self, dev):
        """
        Return the on/off state for a latch sensor (ls) device, if any,
        associated with a linked lock device.  If there is no ls device,
        return the normal operating state (ON) by default.
        """
        L.threaddebug('_getLatchSensorState called "%s"', dev.name)

        lsDevId = dev.pluginProps['lsDevId']
        lsDev = indigo.devices.get(int(lsDevId)) if lsDevId else None
        lsState = self.ON  # Default to ON if there is no ls.
        if lsDev:  # ls exists; get the normalized state.
            lsStateName = dev.pluginProps['lsStateName']
            lsInvert = dev.pluginProps['lsInvert']
            lsState = lsDev.states[lsStateName] ^ lsInvert
        return lsState

    def _getVirtualLockState(self, opDev):
        """
        Return the lock state for the virtual lock (vl) device associated with
        an opener device.  Use the _getVirtualLockDevice method to get the vl
        device object and then return the device onState.  If there is no vl
        device, then return UNLOCKED.
        """
        L.threaddebug('_getVirtualLockState called "%s"', opDev.name)

        vlDev = self._getVirtualLockDevice(opDev)
        return vlDev.onState if vlDev else self.UNLOCKED

    def _updateVirtualLockStatesOnServer(self, vlDev, newLockState):
        """
        Update and optionally log the virtual lock device states on the Indigo
        server.  The states include the onOffState and the lockStatus.  The
        onOffState is the lock state with values UNLOCKED (off) and LOCKED
        (on).  The lockStatus is a lower case string representation of the lock
        state ('locked' or 'unlocked').

        Also, set the state image on the Indigo Home window based on the value
        of the lock state (onOffState).  Select a green lock image if the
        lock state is LOCKED (on) and a red lock image if it is UNLOCKED (off).
        """
        L.threaddebug('_updateVirtualLockStatesOnServer called "%s"',
                      vlDev.name)

        # Compute, update, and optionally log the new lock device states.

        lockStatus = self.LOCK_STATUS[newLockState]
        vlDev.updateStateOnServer('onOffState', newLockState,
                                  uiValue=lockStatus)
        vlDev.updateStateOnServer('lockStatus', lockStatus)
        if vlDev.pluginProps['logLockStateChanges']:
            L.info('"%s" update to %s', vlDev.name, lockStatus.upper())

        # Compute and update the state image.

        image = (indigo.kStateImageSel.Locked if newLockState
                 else indigo.kStateImageSel.Unlocked)
        vlDev.updateStateImageOnServer(image)

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
        deviceStartComm method.  Define the field type instance attribute to
        facilitate communication between ConfigUI callback methods.  Set the
        logging level and subscribe to device changes.
        """
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        # The monitored devices dictionary is a compound dictionary that stores
        # the device id's and properties of devices that are monitored by the
        # plugin.  It has the following structure:
        #
        # self._monitoredDevices = {devId: {mDevId: {mDevStateName: mDevTypeId}}}
        # where:
        #   devId         is the device id of the opener device.
        #   mDevId        is the device id of a timer, sensor, relay or locking
        #                 device to be monitored by the opener plugin to track
        #                 the door state.  All monitored devices must have an
        #                 on/off bool state defined in the devices xml by
        #                 <ValueType boolType="OnOff">Boolean</ValueType>,
        #   mDevStateName is the on/off state name to be monitored by the
        #                 plugin.  For most devices it is typically
        #                 'onOffState'.  For EasyDAQ devices it is 'channelnn'
        #                 where nn is the numeric channel number.  For timers
        #                 the state name is 'timerStatus.active', and
        #   mDevTypeId    identifies the type of monitored device.  The
        #                 monitored device type ids are listed in the
        #                 self.MONITORED_DEVICE_TYPE_IDs tuple.  They are the
        #                 same as the field group type ids in Devices.xml for
        #                 field groups that define monitored devices.

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
        For each opener device, create a new monitored devices dictionary entry
        and a new virtual garage door instance.  Check the monitored device
        properties and determine their startup states.  Reset the vibration
        sensor, if selected and turned on.  Set the startup opener and virtual
        lock states based on the startup monitored device states.  Check for
        inconsistency between the startup door state and the virtual lock
        state.

        No startup processing is needed for a virtual lock device.  The opener
        device pluginProps dictionary includes all virtual lock props.  The
        virtual lock device startup processing is performed as an integral part
        of the opener device startup.
        """
        L.threaddebug('deviceStartComm called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':  # Start opener/virtual lock devices.

            # Create a new monitored devices dictionary entry for the opener.

            devId = dev.id
            self._monitoredDevices[devId] = {}

            # Add all monitored devices that are selected in the opener device
            # ConfigUI to the monitored devices dictionary.  Save the startup
            # states of the devices for use in setting the startup door and
            # virtual lock device states.

            mDevCount = 0
            mDevSelected = ''
            mDevStates = {}  # Startup states of monitored devices.
            for mDevTypeId in self.MONITORED_DEVICE_TYPE_IDs:
                mDevId = dev.pluginProps[mDevTypeId + 'DevId']
                if mDevId:  # Monitored device is selected in the ConfigUI.
                    mDevId = int(mDevId)

                    # Check the monitored device id and state name.  If there
                    # are any errors, log a warning message and exclude the
                    # monitored device from the monitored devices dictionary.

                    mDev = indigo.devices.get(mDevId)
                    if not mDev:
                        L.warning('"%s" mDevId %s is not in the devices '
                                  'dictionary; %s device will not be '
                                  'monitored', dev.name, mDevId, mDevTypeId)
                        continue

                    if not mDev.enabled:
                        L.warning('"%s" monitored device "%s" is not enabled; '
                                  '%s device will not be monitored',
                                  dev.name, mDev.name, mDevTypeId)
                        continue

                    mDevStateName = dev.pluginProps[mDevTypeId + 'StateName']
                    if mDevStateName not in mDev.states:
                        L.warning('"%s" "%s" state %s is not in the states '
                                  'dict; %s device will not be monitored',
                                  dev.name, mDev.name, mDevStateName,
                                  mDevTypeId)
                        continue

                    # Add a new entry in the monitored devices dictionary.

                    if not self._monitoredDevices[devId].get(mDevId):
                        self._monitoredDevices[devId][mDevId] = {}
                    self._monitoredDevices[devId][mDevId][mDevStateName] = mDevTypeId

                    # Get the normalized state of monitored device and add it
                    # to the startup states dictionary.  Increment the
                    # monitored device count.  Add the device type and state
                    # to the selected devices string.

                    mDevInvert = dev.pluginProps.get(mDevTypeId + 'Invert',
                                                     False)
                    mDevState = mDev.states[mDevStateName] ^ mDevInvert
                    mDevStates[mDevTypeId] = mDevState
                    mDevCount += 1
                    mDevSelected += mDevTypeId + ('-off ', '-on ')[mDevState]

                    # Reset the vibration sensor, if selected.

                    if mDevTypeId == 'vs':
                        if mDevState:  # The vibration sensor is on.
                            indigo.device.turnOff(mDevId)  # Reset it.

            L.info('"%s" %s devices selected: %s',
                   dev.name, mDevCount, mDevSelected)
            L.debug(self._monitoredDevices[devId])

            # Determine the startup door state based on the current closed
            # sensor (cs) and open sensor (os) states (see Table 6 in the
            # Design wiki).  Make prudent assumptions and warn the user when
            # the sensor data does not completely determine the startup state.

            csState = mDevStates.get('cs')                 # None if no cs.
            osState = mDevStates.get('os')                 # None of no os.
            
            startupDoorState = self.CLOSED                 # Default to CLOSED.
            if csState and osState:                        # CLOSED and OPEN.
                L.warning('"%s" closed and open sensors are both on; check '
                          'sensors; assume that the door is CLOSED', dev.name)
            elif csState and not osState:                  # Door is CLOSED.
                pass  # startupDoorState = self.CLOSED
            elif not csState and osState:                  # Door is OPEN.
                startupDoorState = self.OPEN
            elif (csState == self.OFF                      # Door is not CLOSED
                  and osState == self.OFF):                # and not OPEN.
                startupDoorState = self.OBSTRUCTED
            elif csState is None and osState is None:      # No sensors.
                L.warning('"%s" no closed sensor or open sensor; cannot '
                          'determine state; assume that the door is CLOSED',
                          dev.name)
            elif csState is None and osState == self.OFF:  # Door is not OPEN.
                L.warning('"%s" no closed sensor; open sensor reports not-'
                          'OPEN; assume that the door is CLOSED', dev.name)
            elif csState == self.OFF and osState is None:  # Door is not CLOSED
                L.warning('"%s" no open sensor; closed sensor reports not-'
                          'CLOSED; assume that the door is OPEN', dev.name)
                startupDoorState = self.OPEN

            # Update the startup door state, if necessary, based on the states
            # of any associated physical lock devices.  Set the startup door
            # state to OBSTRUCTED if the door is not CLOSED and one or more of
            # the physical lock devices LOCKED.

            # Determine the aggregate state of the physical lock (pl)
            # devices (ls, ps, and ml).

            lsState = mDevStates.get('ls', self.ON)   # latch sensor (ls).
            psState = mDevStates.get('ps', self.ON)   # power switch (ps).
            mlState = mDevStates.get('ml', self.OFF)  # mechanical lock (ml).
            plState = not lsState or not psState or mlState  # aggregate pl.

            if startupDoorState != self.CLOSED and plState == self.LOCKED:
                L.warning('"%s" door is not CLOSED and one or more physical '
                          'lock devices are LOCKED; startup door state set to '
                          'OBSTRUCTED', dev.name)
                startupDoorState = self.OBSTRUCTED

            # Set startup door status from the startup door state and the
            # current lock state if any.

            vlState = mDevStates.get('vl')  # None if no vl.
            startupDoorStatus = self.DOOR_STATUS[startupDoorState]
            if startupDoorState == self.CLOSED and vlState:
                startupDoorStatus += '-lk'

            # Instantiate a VirtualGarageDoor object for the device and save
            # the object in the virtual garage doors dictionary.  This
            # completes the startup processing for the opener device.

            vgd = VirtualGarageDoor(dev, startupDoorStatus)
            self._virtualGarageDoors[devId] = vgd

            # The virtual lock normally retains its current state (the existing
            # database state) at startup. If the virtual lock is UNLOCKED and
            # one or more physical lock devices are LOCKED, however, there is
            # a potential inconsistency among the locking device states.  This
            # inconsistency is allowed only if the startup door state is
            # not CLOSED (see above).  If the startup door state is CLOSED,
            # lock the door to resolve the inconsistency.

            if (vlState == self.UNLOCKED and plState == self.LOCKED
                and startupDoorState == self.CLOSED):
                    vlDevId = dev.pluginProps['vlDevId']
                    indigo.device.lock(int(vlDevId))

            # Warn the user if the startup door and lock states are
            # inconsistent.

            if (startupDoorState != self.CLOSED
                    and self._getVirtualLockState(dev)):  # Door is LOCKED.
                L.warning('"%s" door is LOCKED, but not CLOSED; close the '
                          'door manually, or unlock it')

    def deviceStopComm(self, dev):
        """
        Retire door opener devices by deleting the entries in the monitored
        devices dictionary and the virtual garage doors dictionary, if present.
        Virtual lock devices do not require any special action.
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
                for mDevStateName in self._monitoredDevices[devId][mDevId]:

                    # Get the onOffStates for both the old (unchanged) device
                    # object and the new (updated) device object.  Invert the
                    # states if specified in the pluginProps.  Ignore the
                    # device object update if the mdevState is unchanged.

                    mDevTypeId = (self._monitoredDevices
                                  [devId][mDevId][mDevStateName])
                    invert = dev.pluginProps.get(mDevTypeId + 'Invert', False)
                    oldState = oldDev.states[mDevStateName] ^ invert
                    newState = newDev.states[mDevStateName] ^ invert
                    if oldState == newState: continue  # No change, ignore it.

                    # Create a monitored device event name and log it for
                    # debug.

                    mDevEvent = mDevTypeId + ('-off', '-on')[newState]
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
        Validate opener and virtual lock device ConfigUIs.  Complete device
        configuration by creating new devices and updating valuesDict/
        pluginProps values as needed.

        For an opener device, initialize the optional travel timer and virtual
        lock devices if they are selected in the ConfigUI.  In both cases,
        create a new device if the selected device name is not in the Indigo
        devices dictionary.  This occurs when the user selects 'AUTOMATIC' in
        the ConfigUI and the getMenuList method creates a new device name, but
        does not create the new device.  Link the virtual lock device
        bidirectionally with the opener device and validate the locking/
        unlocking delay times.

        Validate all manual (non-menu) entries in the ConfigUI.  For each
        monitored device that is selected in the ConfigUI, check the device and
        its on/off state name to ensure that the device exists and its on/off
        state name is in the device's states dictionary. Also check to ensure
        that a particular device name/state name combination is not reused in
        any other monitored device ConfigUI for all opener devices.  Add
        monitored device id's to the values dictionary for use by other
        methods.  Validate the opening and closing delay times.

        For a virtual lock device, if an opener device is selected, link the
        virtual lock device bidirectionally with the opener device.  If no
        opener device is selected, the virtual lock device will not constrain
        any opener device until it is subsequently linked by activating either
        an opener or virtual lock device ConfigUI.  In either case, validate
        the locking/unlocking delay times.

        Throughout the method, when errors are found, add an error message to
        the errors dictionary in keeping with the standard Indigo validation
        protocol.  Return the values dictionary and the errors dictionary.
        """

        # Local support functions:

        def _getVirtualLockProps():
            """
            Get virtual lock device plugin props from the opener or lock device
            values dictionary.  Also include the device name and device id
            fields used to link the opener device to the virtual lock device
            and vice versa.  If the typeId is 'opener' include the opener
            device name and device id. If the typeId is 'lock' include the
            virtual lock device name and device id.
            """
            groupId = 'op' if typeId == 'opener' else 'vl'

            return {groupId + 'Name':      dev.name,
                    groupId + 'DevId':     str(devId),
                    'lsName':              valuesDict['lsName'],
                    'lsSelected':          valuesDict['lsSelected'],
                    'lsDevId':             valuesDict['lsDevId'],
                    'lsStateName':         valuesDict['lsStateName'],
                    'lsInvert':            valuesDict['lsInvert'],
                    'psName':              valuesDict['psName'],
                    'psDevId':             valuesDict['psDevId'],
                    'psStateName':         valuesDict['psStateName'],
                    'mlName':              valuesDict['mlName'],
                    'mlDevId':             valuesDict['mlDevId'],
                    'mlStateName':         valuesDict['mlStateName'],
                    'laName':              valuesDict['laName'],
                    'laDelay':             valuesDict['laDelay'],
                    'uaName':              valuesDict['uaName'],
                    'uaDelay':             valuesDict['uaDelay'],
                    'logLockStateChanges': valuesDict['logLockStateChanges']}

        def _validateActionDelayTime(action, maxDT=10.0):
            """
            Validate the delay time value associated with a VGD action.  Add an
            error message to the errors dictionary if the delay time is less
            than 0.0 or greater than maxDelay.  The action must be 'opening',
            'closing', 'locking', or 'unlocking'.
            """
            delayFieldId = action[0] + 'aDelay'
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
        errorsDict = indigo.Dict()

        # Begin configuration and validation for opener and lock devices.

        if typeId == 'opener':  # Configure and validate an opener device.

            # Optionally configure a travel timer (tt) device.

            valuesDict['ttDevId'] = ''  # Set default to no timer device.
            ttName = valuesDict['ttName']
            if ttName:  # Existing timer device or automatic device.
                ttDev = indigo.devices.get(ttName)
                if not ttDev:  # No existing device; create new auto device.
                    description = ('Automatically generated timer device for '
                                   '"%s"' % dev.name)
                    props = dict(amount=1.0, amountType='seconds')
                    indigo.device.create(
                        protocol=indigo.kProtocol.Plugin,
                        name=ttName,
                        description=description,
                        pluginId=self.TIMER_PLUGIN_ID,
                        deviceTypeId='timer',
                        props=props,
                        folder='doors')

            # Optionally configure a virtual lock device using the opener
            # device plugin props.

            valuesDict['vlDevId'] = ''  # Set default to no virtual lock.
            vlName = valuesDict['vlName']
            if vlName:  # Existing virtual lock device or automatic device.
                props = _getVirtualLockProps()
                props['IsLockSubType'] = True

                vlDev = indigo.devices.get(vlName)
                if vlDev:  # Existing device; replace plugin props on server.
                    vlProps = vlDev.pluginProps
                    for prop in props:
                        vlProps[prop] = props[prop]
                    vlDev.replacePluginPropsOnServer(vlProps)

                else:  # No device in dictionary; create a new one.
                    description = ('Automatically generated virtual lock '
                                   'device for "%s"' % dev.name)
                    vlDev = indigo.device.create(
                        protocol=indigo.kProtocol.Plugin,
                        name=vlName,
                        description=description,
                        pluginId=self.VIRTUAL_LOCK_PLUGIN_ID,
                        deviceTypeId='lock',
                        props=props,
                        folder='doors')

                if vlDev.enabled:  # Lock device successfully configured.
                    valuesDict['vlDevId'] = vlDev.id  # Add vl link to opener.
                else:  # Virtual lock configuration error.
                    errorsDict['vlName'] = 'Virtual lock configuration error.'

            # Optional configuration of timer and virtual lock devices is
            # complete; begin validation of monitored devices.

            # Clear self._monitoredDevices for this opener to prevent previous
            # device configurations from generating ConfigUI errors.

            self._monitoredDevices[devId] = {}

            # For each monitored device that is selected in the opener device
            # ConfigUI:

            # (1) Validate the device name.
            # (2) Ensure that the device is configured (enabled)
            # (3) Validate the state name.
            # (4) Ensure that selected device name/state pair is unique among
            #     all monitored device types for all opener devices.
            # (5) Validate unique fields for vs and tt devices.
            # (6) Set the device id field in the values dictionary.

            for mDevTypeId in self.MONITORED_DEVICE_TYPE_IDs:
                valuesDict[mDevTypeId + 'DevId'] = ''
                mDevName = valuesDict[mDevTypeId + 'Name']
                if mDevName:  # Monitored device is selected in the ConfigUI.

                    # Validate the device name.

                    mDev = indigo.devices.get(mDevName)
                    if not mDev:
                        error = '"%s" not in the devices dictionary' % mDevName
                        errorsDict[mDevName] = error
                        continue

                    if not mDev.enabled:
                        error = '"%s" configuration error' % mDevName
                        errorsDict[mDevName] = error
                        continue

                    # Validate the state name.

                    mDevStateName = valuesDict[mDevTypeId + 'StateName']
                    if mDevStateName not in mDev.states:
                        error = ('%s not in device states dictionary'
                                 % mDevStateName)
                        errorsDict[mDevStateName] = error
                        continue

                    # Check to ensure that no device/state pairs are reused by
                    # this opener device or others.

                    mDevId = mDev.id
                    for devId_ in self._monitoredDevices:
                        for mDevId_ in self._monitoredDevices[devId_]:
                            for mDevStateName_ in self._monitoredDevices[devId_][mDevId_]:
                                if mDevId == mDevId_ and mDevStateName == mDevStateName_:
                                    error = 'Device/state name already in use'
                                    errorsDict[mDevTypeId + 'Name'] = error
                                    errorsDict[mDevTypeId + 'StateName'] = error
                                    continue

                    # Validate the vs reset delay time.

                    if mDevTypeId == 'vs':
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

                    if mDevTypeId == 'tt':
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
                    # monitored device id in the values dictionary.

                    valuesDict[mDevTypeId + 'DevId'] = str(mDevId)

                    # Add keys/values to self._monitoredDevices to mark this
                    # device/state combination as used.  Note that these
                    # additions are overwritten (with the same data) when the
                    # opener device is started.

                    if not self._monitoredDevices[devId].get(mDevId):
                        self._monitoredDevices[devId][mDevId] = {}
                    self._monitoredDevices[devId][mDevId][mDevStateName] = mDevTypeId
                    L.debug(self._monitoredDevices[devId])

            # Validate action delay times.

            for action_ in ('opening', 'closing', 'locking', 'unlocking'):
                _validateActionDelayTime(action_)

        elif typeId == 'lock':  # Configure and validate a lock device.
            opName = valuesDict['opName']
            if opName:  # Opener device was selected.

                # Replace opener device plugin props (including lock device
                # name and device id).

                props = _getVirtualLockProps()
                opDev = indigo.devices[opName]
                opProps = opDev.pluginProps
                for prop in props:
                    opProps[prop] = props[prop]
                opDev.replacePluginPropsOnServer(opProps)

            else:  # No opener device selected.
                errorsDict['opName'] = 'Opener device is required'

            # Validate locking/unlocking delay times.

            _validateActionDelayTime('locking')
            _validateActionDelayTime('unlocking')

        # validateDeviceConfigUI ending debug.

        L.debug(valuesDict)
        L.debug(errorsDict)

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
    #  def getMenuList(self, fieldId, valuesDict, typeId, devId)              #
    #  def arSelected(valuesDict, typeId, devId):  # 1.  activation relay (ar)#
    #  def csSelected(valuesDict, typeId, devId):  # 2.  closed sensor (cs)   #
    #  def osSelected(valuesDict, typeId, devId):  # 3.  open sensor (os)     #
    #  def vsSelected(valuesDict, typeId, devId):  # 4.  vibration sensor (vs)#
    #  def ttSelected(valuesDict, typeId, devId):  # 5.  travel timer (tt)    #
    #  def vlSelected(valuesDict, typeId, devId):  # 6.  virtual lock (vl)    #
    #  def lsSelected(valuesDict, typeId, devId):  # 7.  latch sensor (ls)    #
    #  def psSelected(valuesDict, typeId, devId):  # 8.  power switch (ps)    #
    #  def mlSelected(valuesDict, typeId, devId):  # 9.  mechanical lock (ml) #
    #  def oaSelected(valuesDict, typeId, devId):  # 10. opening action (oa)  #
    #  def caSelected(valuesDict, typeId, devId):  # 11. closing action (ca)  #
    #  def laSelected(valuesDict, typeId, devId):  # 12. locking action (la)  #
    #  def uaSelected(valuesDict, typeId, devId):  # 13. unlocking action (ua)#
    #                                                                         #
    ###########################################################################

    def getMenuList(self, filter_, valuesDict, typeId, devId):
        """
        Create and return a menu list for the action group/device selection
        menus in the opener and lock device ConfigUIs.

        The filter_ argument is a text string that contains the ConfigUI field
        group id and the menu type in the form 'xx:menuType'.  The group ids
        and menu types are listed in the Devices.xml file.
        
        After decoding the filter_ argument, create a list of action group/
        device names for the menu list.  For the 'action' menu type, select all
        action groups from the Indigo action groups dictionary.  For all other
        menu types, select devices from the Indigo devices dictionary that 
        have a device type id in the DEVICE_TYPE_IDs[menuType] tuple.

        Choose up to two user options to be added at the bottom of the menu
        list following the selected action group/device names.  For the opener
        group (id 'op'), do not include any user options.  For all other groups
        that have an 'xxName' field with a selected value, include a
        'NO SELECTION' option to let the user deselect the prior selection.
        Also, for the travel timer group (id 'tt') and the virtual lock group
        (id 'vl'), add an 'AUTOMATIC' option to let the user automatically
        create a new device.

        Return a menu list consisting of a sorted list of action group/device
        names followed by any user options.
        """
        dev = indigo.devices[devId]
        L.threaddebug('getMenuList called "%s" filter = %s',
                      dev.name, filter_)

        groupId, menuType = filter_.split(':')  # Decode the filter_ argument.
        names = []  # Action group or device names.

        if menuType == 'action':  # Select action groups.
            for actionGroup in indigo.actionGroups.iter('self'):
                names.append(actionGroup.name)

        else:  # Select devices.
            for dev_ in indigo.devices:
                if dev_.deviceTypeId in self.DEVICE_TYPE_IDs[menuType]:
                    names.append(dev_.name)

        # Generate and return menu list with 'AUTOMATIC' and 'NO SELECTION'
        # options.

        menuList = [(name, name) for name in sorted(names)]

        if groupId in ('tt', 'vl'):  # Add the 'AUTOMATIC' option.

            # Derive an automatic device name from the opener device name and
            # the menu type ('virtualLock' or 'timer').

            if dev.name == 'new device':  # Opener device is new.
                autoDevName = 'new %s device' % menuType
            elif dev.name.endswith('-opener'):
                autoDevName = dev.name[:-7] + '-' + menuType
            else:
                autoDevName = dev.name + '-' + menuType

            menuList.append((autoDevName, 'AUTOMATIC'))

        if (groupId != 'op' and                   # Exclude opener group and
              valuesDict.get(groupId + 'Name')):  # add 'NO SELECTION' option.
            menuList.append(('None', 'NO SELECTION'))

        return menuList

    @staticmethod
    def arSelected(valuesDict, typeId, devId):  # 1.  activation relay (ar)
        """
        Respond to a user selection from the dynamic list menu in the arName
        field of the device ConfigUI.

        This method and the other xxSelected methods below complement the
        getMenuList method.  getMenuList inserts a 'NO SELECTION' item into the
        menu list for fields that already have a value selected.  The
        xxSelected methods deselect the field if the user selects
        'NO SELECTION'.

        The xxSelected methods also set the 'xxSelected' hidden checkbox field.
        This field is used to conditionally display other fields if the
        'xxName' field is selected.
        """
        dev = indigo.devices[devId]
        L.threaddebug('arSelected called "%s"', dev.name)

        if valuesDict['arName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['arName'] = ''           # Deselect arName.
            valuesDict['arSelected'] = 'false'  # Disable conditional display.
        else:                                   # Something else selected.
            valuesDict['arSelected'] = 'true'   # Enable conditional display.
        return valuesDict

    @staticmethod
    def csSelected(valuesDict, typeId, devId):  # 2.  closed sensor (cs)
        """
        Respond to a user selection from the dynamic list menu in the csName
        field of the device ConfigUI.  See the arSelected method for details.
        """
        dev = indigo.devices[devId]
        L.threaddebug('csSelected called "%s"', dev.name)

        if valuesDict['csName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['csName'] = ''           # Deselect csName.
            valuesDict['csSelected'] = 'false'  # Disable conditional display.
        else:  # Something else selected.
            valuesDict['csSelected'] = 'true'   # Enable conditional display.
        return valuesDict

    @staticmethod
    def osSelected(valuesDict, typeId, devId):  # 3.  open sensor (os)
        """
        Respond to a user selection from the dynamic list menu in the osName
        field of the device ConfigUI.  See the arSelected method for details.
        """
        dev = indigo.devices[devId]
        L.threaddebug('osSelected called "%s"', dev.name)

        if valuesDict['osName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['osName'] = ''           # Deselect osName.
            valuesDict['osSelected'] = 'false'  # Disable conditional display.
        else:  # Something else selected.
            valuesDict['osSelected'] = 'true'   # Enable conditional display.
        return valuesDict

    @staticmethod
    def vsSelected(valuesDict, typeId, devId):  # 4.  vibration sensor (vs)
        """
        Respond to a user selection from the dynamic list menu in the vsName
        field of the device ConfigUI.  See the arSelected method for details.
        """
        dev = indigo.devices[devId]
        L.threaddebug('vsSelected called "%s"', dev.name)

        if valuesDict['vsName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['vsName'] = ''           # Deselect vsName.
            valuesDict['vsSelected'] = 'false'  # Disable conditional display.
        else:  # Something else selected.
            valuesDict['vsSelected'] = 'true'   # Enable conditional display.
        return valuesDict

    @staticmethod
    def ttSelected(valuesDict, typeId, devId):  # 5.  travel timer (tt)
        """
        Respond to a user selection from the dynamic list menu in the ttName
        field of the device ConfigUI.  See the arSelected method for details.
        """
        dev = indigo.devices[devId]
        L.threaddebug('ttSelected called "%s"', dev.name)

        if valuesDict['ttName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['ttName'] = ''           # Deselect ttName.
            valuesDict['ttSelected'] = 'false'  # Disable conditional display.
        else:  # Something else selected.
            valuesDict['ttSelected'] = 'true'   # Enable conditional display.
        return valuesDict

    @staticmethod
    def vlSelected(valuesDict, typeId, devId):  # 6.  virtual lock (vl)
        """
        Respond to a user selection from the dynamic list menu in the vlName
        field of the device ConfigUI.  See the arSelected method for details.

        In addition to the normal xxSelected actions, deselect the latch
        sensor, the power switch, and the mechanical lock when the virtual lock
        is deselected.
        """
        dev = indigo.devices[devId]
        L.threaddebug('vlSelected called "%s"', dev.name)

        if valuesDict['vlName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['vlName'] = ''           # Deselect vlName.
            valuesDict['vlSelected'] = 'false'  # Disable conditional display.
            for groupId in ('ls', 'ps', 'ml'):  # Deselect ls, ps, and ml.
                valuesDict[groupId + 'Name'] = ''
                valuesDict[groupId + 'Selected'] = 'false'
        else:  # Something else selected.
            valuesDict['vlSelected'] = 'true'   # Enable conditional display.
        return valuesDict

    @staticmethod
    def lsSelected(valuesDict, typeId, devId):  # 7.  latch sensor (ls)
        """
        Respond to a user selection from the dynamic list menu in the lsName
        field of the device ConfigUI.  See the arSelected method for details.
        """
        dev = indigo.devices[devId]
        L.threaddebug('lsSelected called "%s"', dev.name)

        if valuesDict['lsName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['lsName'] = ''           # Deselect lsName.
            valuesDict['lsSelected'] = 'false'  # Disable conditional display.
        else:  # Something else selected.
            valuesDict['lsSelected'] = 'true'   # Enable conditional display.
        return valuesDict

    @staticmethod
    def psSelected(valuesDict, typeId, devId):  # 8.  power switch (ps)
        """
        Respond to a user selection from the dynamic list menu in the psName
        field of the device ConfigUI.  See the arSelected method for details.

        Note that no 'psSelected' hidden checkbox field is used in the ps
        ConfigUI fields.
        """
        dev = indigo.devices[devId]
        L.threaddebug('psSelected called "%s"', dev.name)

        if valuesDict['psName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['psName'] = ''           # Deselect psName.
        return valuesDict

    @staticmethod
    def mlSelected(valuesDict, typeId, devId):  # 9.  mechanical lock (ml)
        """
        Respond to a user selection from the dynamic list menu in the mlName
        field of the device ConfigUI.  See the arSelected method for details.

        Note that no 'mlSelected' hidden checkbox field is used in the ml
        ConfigUI fields.
        """
        dev = indigo.devices[devId]
        L.threaddebug('mlSelected called "%s"', dev.name)

        if valuesDict['mlName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['mlName'] = ''           # Deselect mlName.
        return valuesDict

    @staticmethod
    def oaSelected(valuesDict, typeId, devId):  # 10. opening action (oa)
        """
        Respond to a user selection from the dynamic list menu in the oaName
        field of the device ConfigUI.  See the arSelected method for details.

        Note that no 'oaSelected' hidden checkbox field is used in the oa
        ConfigUI fields.
        """
        dev = indigo.devices[devId]
        L.threaddebug('oaSelected called "%s"', dev.name)

        if valuesDict['oaName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['oaName'] = ''           # Deselect oaName.
        return valuesDict

    @staticmethod
    def caSelected(valuesDict, typeId, devId):  # 11. closing action (ca)
        """
        Respond to a user selection from the dynamic list menu in the caName
        field of the device ConfigUI.  See the arSelected method for details.

        Note that no 'caSelected' hidden checkbox field is used in the ca
        ConfigUI fields.
        """
        dev = indigo.devices[devId]
        L.threaddebug('caSelected called "%s"', dev.name)

        if valuesDict['caName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['caName'] = ''           # Deselect caName.
        return valuesDict

    @staticmethod
    def laSelected(valuesDict, typeId, devId):  # 12. locking action (la)
        """
        Respond to a user selection from the dynamic list menu in the laName
        field of the device ConfigUI.  See the arSelected method for details.

        Note that no 'laSelected' hidden checkbox field is used in the la
        ConfigUI fields.
        """
        dev = indigo.devices[devId]
        L.threaddebug('laSelected called "%s"', dev.name)

        if valuesDict['laName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['laName'] = ''           # Deselect laName.
        return valuesDict

    @staticmethod
    def uaSelected(valuesDict, typeId, devId):  # 13. unlocking action (ua)
        """
        Respond to a user selection from the dynamic list menu in the uaName
        field of the device ConfigUI.  See the arSelected method for details.

        Note that no 'uaSelected' hidden checkbox field is used in the ua
        ConfigUI fields.
        """
        dev = indigo.devices[devId]
        L.threaddebug('uaSelected called "%s"', dev.name)

        if valuesDict['uaName'] == 'None':      # 'NO SELECTION' selected.
            valuesDict['uaName'] = ''           # Deselect uaName.
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
    #  def _turnOnOffPhysicalLockDevice(vlDev, plAction)                      #
    #  def _lockGarageDoor(self, vlDev)                                       #
    #  def _unlockGarageDoor(self, vlDev)                                     #
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
        dev can be an opener or lock device.  action must be 'opening',
        'closing', 'locking', or 'unlocking'.

        Optionally execute an action group and delay based on opener or lock
        device pluginProps entries.  Do nothing if the action group or delay
        keys are not in the pluginProps dictionary.  This ensures backward
        compatibility with opener or lock devices created by older plugin
        versions.
        """
        L.threaddebug('_executeOptionalActions called "%s"', dev.name)

        actionGroupName = dev.pluginProps.get(action[0] + 'aName')
        if actionGroupName:
            indigo.actionGroup.execute(actionGroupName)

        delayTime = dev.pluginProps.get(action[0] + 'aDelay')
        if delayTime:
            sleep(float(delayTime))

    def _openGarageDoor(self, opDev):
        """
        Warn the user and abort if the latch sensor (ls) exists and is OFF (not
        latched).  Otherwise, execute optional opening actions and open the
        door if it is UNLOCKED and CLOSED or CLOSING.  Unlock the door before
        opening if requested.
        """
        L.threaddebug('_openGarageDoor called "%s"', opDev.name)

        vlState = self._getVirtualLockState(opDev)

        if not self._getLatchSensorState(opDev):  # Abort if the ls is OFF.
            L.warning('"%s" attempt to open the garage door when the latch '
                      'sensor is OFF; action ignored', opDev.name)

        elif (vlState  # Abort if LOCKED w/no unlock before opening (ubo).
                and not opDev.pluginProps.get('unlockBeforeOpening')):
            L.warning('"%s" attempt to open the garage door when it is '
                      'LOCKED; action ignored', opDev.name)

        elif opDev.states['doorState'] not in (self.CLOSED, self.CLOSING):
            L.warning('"%s" attempt to open the garage door when it is '
                      'not CLOSED or CLOSING; action ignored', opDev.name)

        else:  # If LOCKED, unlock the door then open it.
            if vlState:  # Door is locked, but ubo was requested.
                vlDev = self._getVirtualLockDevice(opDev)
                self._unlockGarageDoor(vlDev)

            # Execute optional opening actions and toggle the door OPEN.

            self._executeOptionalActions(opDev)
            self._toggleActivationRelay(opDev)

    def _closeGarageDoor(self, opDev):
        """
        Warn the user and abort if the latch sensor (ls) exists and is OFF (not
        latched).  Otherwise, execute optional closing actions and close the
        door if it is UNLOCKED and OPEN, OPENING, or OBSTRUCTED.
        """
        L.threaddebug('_closeGarageDoor called "%s"', opDev.name)

        if not self._getLatchSensorState(opDev):  # Abort if the ls is OFF.
            L.warning('"%s" attempt to close the garage door when the latch '
                      'sensor is OFF; action ignored', opDev.name)

        elif self._getVirtualLockState(opDev):  # Abort if LOCKED.
            L.warning('"%s" attempt to close the garage door when it is '
                      'LOCKED; action ignored', opDev.name)

        elif opDev.states['doorState'] not in (self.OPEN, self.OPENING,
                                               self.OBSTRUCTED):
            L.warning('"%s" attempt to close the garage door when it is '
                      'not OPEN, OPENING, or OBSTRUCTED; action ignored',
                      opDev.name)

        else:  # Execute optional closing actions and toggle the door CLOSED.
            self._executeOptionalActions(opDev, action='closing')
            self._toggleActivationRelay(opDev)

    def _turnOnOffPhysicalLockDevice(self, vlDev, plAction):
        """
        Turn on or turn off a physical lock (pl) device and wait for completion
        of the operation.  The physical lock device may be a power switch (ps)
        or a mechanical lock (ml) and is specified by the pl device type ('ps'
        or 'ml').  The plAction argument is a string containing the pl device
        type, a dash, and an on/off action (e.g., 'ps-on' or 'ml-off').

        Decode the plAction into a pl device type and a target state (either
        self.ON or self.OFF).  Check to see if the pl device is available and
        return if it is not.

        Get the pl device state and compare it to the target state.  Return if
        the device is already in the target state.  If it is not toggle the
        device to get to the target state.

        Wait for the toggle action to complete by sleeping and then checking
        the state again.  Log a warning message if the device is not in the
        target state after 100 milliseconds.
        """
        L.threaddebug('_turnOnOffPhysicalLockDevice called "%s" %s',
                      vlDev.name, plAction)

        plDevType = plAction[:2]
        targetState = self.ON if plAction[3:] == 'on' else self.OFF

        plDevId = vlDev.pluginProps[plDevType + 'DevId']
        if plDevId:  # pl device is available.
            plDevId = int(plDevId)

            # Get the current state for the pl device.

            plDev = indigo.devices[plDevId]
            plStateName = vlDev.pluginProps[plDevType + 'StateName']
            plState = plDev.states[plStateName]

            # Toggle the pl device if it is not in the targetState.

            if plState != targetState:
                indigo.device.toggle(plDevId)

                # Wait for toggle completion.

                maxDelay = 100  # Max number of delays.
                sleepTime = 0.001  # Delay increment in seconds.
                for _ in range(maxDelay):
                    sleep(sleepTime)
                    plDev = indigo.devices[plDevId]
                    plState = plDev.states[plStateName]
                    if plState == targetState:  # Toggle completed.
                        break
                else:
                    L.warning('"%s" %s device failed to turn %s after %s '
                              'milliseconds', vlDev.name, plDevType,
                              ('off', 'on')[targetState],
                              1000 * maxDelay * sleepTime)

    def _lockGarageDoor(self, vlDev):
        """
        Execute optional locking actions and lock the garage door if it is
        UNLOCKED and CLOSED.  If there is no link to an opener device or the
        door is not CLOSED, abort the lock request.

        Optionally execute locking actions to (1) execute a user-specified
        locking action group and/or delay, (2) turn off the garage door opener
        power, and (3) turn on (lock) a garage door mechanical lock.  Log a
        warning message and return if any of the optional actions fails to
        execute.

        If there are no exceptions, set the virtual lock device states on the
        server to LOCKED.
        """
        L.threaddebug('_lockGarageDoor called "%s"', vlDev.name)

        if not vlDev.onState:  # Lock door only if it is currently UNLOCKED.
            opDev = self._getOpenerDevice(vlDev)
            if not opDev:  # Abort if no opener device.
                L.warning('"%s" lock device is not linked to an opener '
                          'device; lock action ignored', vlDev.name)

            elif opDev.states['doorState'] != self.CLOSED:  # Abort
                L.warning('"%s" attempt to lock the garage door when it is '
                          'not closed; action ignored', vlDev.name)

            else:  # Lock it.
                try:  # Execute optional actions.
                    self._executeOptionalActions(vlDev, action='locking')
                    self._turnOnOffPhysicalLockDevice(vlDev, 'ps-off')
                    self._turnOnOffPhysicalLockDevice(vlDev, 'ml-on')

                except Exception as warningMessage:
                    L.warning('"%s" optional locking action failed: %s',
                              vlDev.name, warningMessage)

                else:  # Update virtual lock device states.
                    self._updateVirtualLockStatesOnServer(vlDev, self.LOCKED)

    def _unlockGarageDoor(self, vlDev):
        """
        Execute optional unlocking actions and unlock the garage door if it is
        LOCKED and the latch sensor (ls) is ON or nonexistent.

        Optionally execute unlocking actions to (1) turn off (unlock) a garage
        door mechanical lock, (2) turn on the garage door opener power, and (3)
        execute a user-specified unlocking action group and/or delay.  Log a
        warning message and return if any of the optional actions fails to
        execute.

        If there are no exceptions, set the virtual lock device states on the
        server to UNLOCKED.
        """
        L.threaddebug('_unlockGarageDoor called "%s"', vlDev.name)

        if vlDev.onState:  # Unlock only if the door is LOCKED.

            if not self._getLatchSensorState(vlDev):  # Abort if the ls is OFF.
                L.warning('"%s" attempt to unlock the garage door when the '
                          'latch sensor is OFF; action ignored', vlDev.name)

            else:  # ls is ON or nonexistent; unlock it.

                try:   # Execute optional actions.
                    self._turnOnOffPhysicalLockDevice(vlDev, 'ml-off')
                    self._turnOnOffPhysicalLockDevice(vlDev, 'ps-on')
                    self._executeOptionalActions(vlDev, action='unlocking')

                except Exception as warningMessage:
                    L.warning('"%s" optional unlocking action failed: %s',
                              vlDev.name, warningMessage)

                else:  # Update lock device states.
                    self._updateVirtualLockStatesOnServer(vlDev, self.UNLOCKED)

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
        the lock device obtained from the _getVirtualLockDevice method.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('lockGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'lock':  # dev is a lock device; lock it.
            self._lockGarageDoor(dev)

        elif dev.deviceTypeId == 'opener':  # dev is an opener device.
            vlDev = self._getVirtualLockDevice(dev)
            if vlDev:  # Valid lock device, lock it.
                self._lockGarageDoor(vlDev)
            else:  # Abort if no lock.
                L.warning('"%s" no available lock device; action ignored',
                          dev.name)

    def unlockGarageDoor(self, pluginAction):
        """
        Unlock a garage door given either a lock device or an opener device.
        If a lock device is provided in the pluginAction argument, use the
        lock device from the argument.  If an opener device is provided, use
        the lock device obtained from the _getVirtualLockDevice method.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('unlockGarageDoor called "%s"', dev.name)

        if dev.deviceTypeId == 'lock':  # dev is a lock device; unlock it.
            self._unlockGarageDoor(dev)

        elif dev.deviceTypeId == 'opener':  # dev is an opener device.
            vlDev = self._getVirtualLockDevice(dev)
            if vlDev:  # Valid lock device, unlock it.
                self._unlockGarageDoor(vlDev)
            else:  # Abort if no lock.
                L.warning('"%s" no available lock device; action ignored',
                          dev.name)

    def actionControlDevice(self, action, dev):
        """
        For an opener device, implement the device turnOn (close) and turnOff
        (open) actions using the internal _closeGarageDoor and _openGarageDoor
        methods.  Log a warning message if the device toggle action is
        selected.  Remote toggling of the garage door is not allowed for safety
        reasons.

        For a virtual lock device, implement the device lock and unlock actions
        using the internal _lockGarageDoor and _unlockGarageDoor methods.

        Ignore requests for any other device actions.
        """
        L.threaddebug('actionControlDevice called "%s"', dev.name)

        if dev.deviceTypeId == 'opener':
            if action.deviceAction == indigo.kDeviceAction.TurnOn:
                self._closeGarageDoor(dev)
            elif action.deviceAction == indigo.kDeviceAction.TurnOff:
                self._openGarageDoor(dev)
            elif action.deviceAction == indigo.kDeviceAction.Toggle:
                L.warning('"%s" toggling not allowed for opener devices; '
                      'action ignored', dev.name)

        elif dev.deviceTypeId == 'lock':
            if action.deviceAction == indigo.kDeviceAction.Lock:
                self._lockGarageDoor(dev)
            elif action.deviceAction == indigo.kDeviceAction.Unlock:
                self._unlockGarageDoor(dev)

    def actionControlUniversal(self, action, dev):
        """
        Implement the requestStatus command by logging the current door or lock
        status.
        """
        L.threaddebug('actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            if dev.deviceTypeId == 'opener':
                L.info('"%s" is %s', dev.name, dev.states['doorStatus'].upper())
            elif dev.deviceTypeId == 'lock':
                L.info('"%s" is %s', dev.name, dev.states['lockStatus'].upper())
