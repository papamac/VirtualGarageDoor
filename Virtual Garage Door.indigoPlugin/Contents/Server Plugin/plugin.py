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
 VERSION:  1.0.6
    DATE:  September 8, 2022


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

****************************** needs work *************************************

DEPENDENCIES/LIMITATIONS:

****************************** needs work *************************************


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
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '1.0.6'
__date__ = 'September 8, 2022'

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

MONITORED_DEVICE_TYPES = ('ar', 'cs', 'os', 'vs', 'tt')

# activation relay momentary closure time (seconds).

AR_CLOSURE_TIME = 1

# Valid door state transitions used by the deviceUpdated method to select a new
# door state after the occurrence of a monitored device event.

DOOR_STATE_TRANSITIONS = {

    #  door       event          new door     reference       transition
    # state    w/qualifiers       state        number          function

    'closed':   {'ar-on':       'opening',      # 1      normal --> opening
                 'cs-off':      'opening',      # 2      normal --> opening
                 'vs-on':       'opening',      # 3      normal --> opening
                 'os-on':       'open'},        # 4      recovery from anomaly
    'opening':  {'os-on':       'open',         # 5      normal --> open
                 'tt-exp&!os':  'open',         # 6      normal --> open
                 'ar-on':       'stopped',      # 7      interrupted opening
                 'tt-exp':      'stopped',      # 8      interrupted opening
                 'cs-off':      'opening',      # 9      redundant event
                 'vs-on':       'opening',      # 10     redundant event
                 'cs-on':       'closed'},      # 11     recovery from anomaly
    'open':     {'ar-on':       'closing',      # 12     normal --> closing
                 'os-off':      'closing',      # 13     normal --> closing
                 'vs-on':       'closing',      # 14     normal --> closing
                 'cs-on':       'closed'},      # 15     recovery from anomaly
    'closing':  {'cs-on':       'closed',       # 16     normal --> closed
                 'tt-exp&!cs':  'closed',       # 17     normal --> closed
                 'ar-on':       'opening',      # 18     interrupted closing
                 'tt-exp':      'opening',      # 19     interrupted closing
                 'os-off':      'closing',      # 20     redundant event
                 'vs-on':       'closing',      # 21     redundant event
                 'os-on':       'open'},        # 22     recovery from anomaly
    'stopped':  {'ar-on':       'closing',      # 23     normal --> closing
                 'vs-on':       'closing',      # 24     normal --> closing
                 'cs-on':       'closed',       # 25     recovery from anomaly
                 'os-on':       'open'}}        # 26     recovery from anomaly

# Sensor and relay device type id tuples used by the dynamic list callback
# methods in Plugin Part III.

easyDaqComboTypeIds = (     'easyDaq4r4io',      'easyDaq16r8io',
                            'easyDaq8ii4io4r')
easyDaqRelayTypeIds = (     'easyDaq8r',         'easyDaq24r',
                            'easyDaqDo24Stack',  'easyDaqOutputRelay')
easyDaqSensorTypeIds = (    'easyDaq24io',)

shellyDirectRelayTypeIds = ('shelly1',           'shelly1l',
                            'shelly1pm',         'shelly4pro,'
                            'shellyem',          'shellyem3')
shellyMQTTRelayTypeIds = (  'shelly-1',          'shelly-1pm',
                            'shelly-2-5-relay',  'shelly-2-5-roller',
                            'shelly-4-pro',      'shelly-em-relay',
                            'shelly-uni-relay')

genericRelayTypeIds = (     'digitalOutput',    'pseudoRelay',
                            'zwDimmerType',     'zwRelayType')
genericSensorTypeIds = (    'alarmZone',        'contactSensor',
                            'digitalInput',     'masqSensor',
                            'zwOnOffSensorType')

RELAY_DEVICE_TYPE_IDs = (   easyDaqComboTypeIds + easyDaqRelayTypeIds
                            + shellyDirectRelayTypeIds + shellyMQTTRelayTypeIds
                            + genericRelayTypeIds)

SENSOR_DEVICE_TYPE_IDs = (  easyDaqComboTypeIds + easyDaqSensorTypeIds
                            + genericSensorTypeIds)


###############################################################################
#                                                                             #
#                               CLASS Plugin                                  #
#                                                                             #
###############################################################################

class Plugin(indigo.PluginBase):
    """
    **************************** needs work ***********************************
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
    #  def _updateDoorStates(dev, doorState)                                  #
    #                                                                         #
    ###########################################################################

    # Private methods:

    def __init__(self, pluginId, pluginDisplayName,
                 pluginVersion, pluginPrefs):
        """
        Initialize plugin data and private instance attributes for the Plugin
        class.

        Two local dictionaries are private to the Plugin class: the monitored
        devices dictionary and the sequences dictionary.  Both are keyed by the
        device id of a Plugin opener device.  self,__init__ initializes these
        to empty dictionaries to be filled later by Plugin methods.

        The monitored devices dictionary is key to the operation of the Plugin
        class.  It is a compound dictionary that stores device id's and
        properties for devices that are monitored by the plugin.  It has the
        following structure:

        self._monitoredDevices = {devId: {mDevId: {mDevState: mDevType}}}
        where:
           devId     is the device id of the opener device.
           mDevId    is the device id of a timer, sensor, or relay device to be
                     monitored by the opener plugin to determine the garage
                     door state.  All monitored devices must have an on/off
                     bool state defined in the devices xml by
                     <ValueType boolType="OnOff">Boolean</ValueType>.
           mDevState is the state name to be monitored by the plugin.  For
                     most sensor devices it is typically "onOffState".  For
                     EasyDAQ devices it is "channelnn" where nn is the
                     numeric channel number.  For timers the state name is
                     "timerStatus.active".
           mDevType  is the type of the monitored device that allows the
                     plugin to interpret state changes. Types are
                     travel timer "tt", closed sensor "cs", open sensor "os",
                     vibration sensor "vs", and activation relay "ar".

        self._monitoredDevices is created by the deviceStartComm method and
        used by the deviceUpdated method to select monitored devices and
        interpret their state changes.  self._monitoredDevices is also used
        in the validateDeviceConfigUi method to ensure that mDevId/mDevState
        combinations are not reused across the various opener devices/sensors.

        The self._sequences dictionary captures the current monitored device
        event/door state sequence for each opener device. This sequence is used
        in debug mode to ensure that the right door state transitions were
        selected in response to the detected events.
        """
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)
        self._monitoredDevices = {}
        self._lastEventTimes = {}  # Last event time by devId.
        self._sequences = {}       # Door state transition sequence by devId.

    def __del__(self):
        """
        Delete the Plugin instance object.
        """
        LOG.threaddebug('Plugin.__del__ called')
        indigo.PluginBase.__del__(self)

    @staticmethod
    def _updateDoorStates(dev, doorState):
        """
        Update the doorState and the onOffState for an opener device.

        The doorState value can be closed, opening, open, closing, or stopped.
        Set the onOffState to on if the door is closed and off otherwise.  Set
        the user interface image to green if the onOffState is on (closed) and
        red otherwise.
        """
        dev.updateStateOnServer('doorStatus', doorState)
        onOffState = doorState == 'closed'
        dev.updateStateOnServer('onOffState', onOffState, uiValue=doorState)
        image = (indigo.kStateImageSel.SensorOn if onOffState
                 else indigo.kStateImageSel.SensorTripped)
        dev.updateStateImageOnServer(image)
        LOG.info('"%s" update to %s', dev.name, doorState)

    # Indigo standard public instance methods:

    def startup(self):
        self.indigo_log_handler.setLevel(NOTSET)
        level = self.pluginPrefs['loggingLevel']
        LOG.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        LOG.threaddebug('Plugin.startup called')
        indigo.devices.subscribeToChanges()

    def deviceStartComm(self, dev):
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
                mDevStateName = mDevType + 'State'
                mDevState = dev.pluginProps[mDevStateName]
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
            LOG.error('"%s" one or more errors occurred during initilization; '
                      'check ConfigUi', dev.name)
            self.deviceStopComm(dev)
            return

        # Initialize the last event time for this device.

        self._lastEventTimes[devId] = datetime.now()

        # Initialize the opener device state.  Assume that door is not in
        # motion and that it is closed unless the closedSensor is off and
        # openSensor is on.

        csState = states.get('cs')
        osState = states.get('os')
        doorState = 'open' if not csState and osState else 'closed'
        self._sequences[devId] = '<%s>' % doorState
        if doorState != dev.states.get('doorStatus'):
            self._updateDoorStates(dev, doorState)

    def deviceStopComm(self, dev):
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

                    doorState = dev.states['doorStatus']

                    # Create monitored device event name.

                    mDevEvent = mDevType + ('-off', '-on')[newState]
                    if self.pluginPrefs['logAll']:
                        LOG.debug('"%s" %s', dev.name, mDevEvent)

                    # Check for expired timer.

                    if mDevEvent == 'tt-off':  # Timer is inactive.
                        if newDev.states['timeLeftSeconds'] == '0':
                            mDevEvent = 'tt-exp'  # Timer has expired.

                            # Add qualifiers for travel timer expired events
                            # that have different meanings during opening and
                            # closing.

                            if doorState == 'opening':
                                os = dev.pluginProps.get('os')
                                mDevEvent += '&!os' if not os else ''
                            elif doorState == 'closing':
                                cs = dev.pluginProps.get('cs')
                                mDevEvent += '&!cs' if not cs else ''

                    # Ignore events that can't affect the door state.

                    if mDevEvent in ('ar-off', 'vs-off', 'tt-on', 'tt-off'):
                        continue

                    # Get the new door state from the DOOR_STATE_TRANSITIONS
                    # dictionary as a function of the current door state and
                    # the monitored device event.

                    try:
                        newDoorState = (DOOR_STATE_TRANSITIONS
                                        [doorState][mDevEvent])

                    # Ignore the event if it is not legal for the current door
                    # state (key error).

                    except KeyError:
                        LOG.warning('"%s" mDevEvent %s is inconsistent '
                                    'with door state %s',
                                    dev.name, mDevEvent, doorState)
                        continue

                    # Compute the time since the last event and append the
                    # transition data to the door state transition sequence.

                    eventTime = datetime.now()
                    dt = eventTime - self._lastEventTimes[devId]
                    timeSinceLastEvent = dt.total_seconds()
                    if timeSinceLastEvent > 99:
                        timeSinceLastEvent = 99
                    self._lastEventTimes[devId] = eventTime
                    self._sequences[devId] += (' [%.3f %s <%s>]'
                                               % (timeSinceLastEvent,
                                                  mDevEvent,
                                                  newDoorState))

                    if newDoorState != doorState:  # Door state has changed.

                        # Update the door states on the server and perform new
                        # state processing.

                        self._updateDoorStates(dev, newDoorState)

                        ttDevId = int(dev.pluginProps['ttDevId'])
                        if newDoorState.endswith('ing'):  # Door is moving.
                            TIMER.executeAction('restartTimer',
                                                deviceId=ttDevId)

                        else:  # Door is stationary (open, closed, or stopped).
                            TIMER.executeAction('stopTimer', deviceId=ttDevId)

                            # Log the current sequence, and initialize the next
                            # sequence.

                            LOG.debug('"%s" %s %s', dev.name,
                                      dev.pluginProps['mDevConfig'],
                                      self._sequences[devId])
                            self._sequences[devId] = '<%s>' % newDoorState

                            # Reset vibration sensor, if present, after a
                            # delay.

                            vsDevIdStr = dev.pluginProps['vsDevId']
                            if vsDevIdStr:
                                vsDevId = int(vsDevIdStr)
                                vsResetDelay = float(dev.pluginProps
                                                     ['vsResetDelay'])
                                sleep(vsResetDelay)
                                indigo.device.turnOff(vsDevId)

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
        LOG.threaddebug('Plugin.validatePrefsConfigUi called')
        level = valuesDict['loggingLevel']
        LOG.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        return True

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
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
                    err = 'Device not in devices dictionary'
                    errors[mDevType] = err
                    continue

                # Validate the state name.

                mDevStateName = mDevType + 'State'
                mDevState = valuesDict[mDevStateName]
                if mDevState not in mDev.states:
                    err = 'on/off state not in device states dictionary'
                    errors[mDevStateName] = err
                    continue

                # Check to ensure that no device/state pairs are reused by this
                # opener device or others.

                mDevId = indigo.devices[mDevName].id
                for devId_ in self._monitoredDevices:
                    for mDevId_ in self._monitoredDevices[devId_]:
                        for mDevState_ in (self._monitoredDevices[devId_]
                                          [mDevId_]):
                            if mDevId == mDevId_ and mDevState == mDevState_:
                                err = 'Device/state already in use'
                                errors[mDevType] = err
                                errors[mDevStateName] = err
                                continue

                # Validate the vs reset delay time.

                if mDevType == 'vs':
                    vsResetDelay = -1  # Force an error if try fails.
                    try:
                        vsResetDelay = float(valuesDict['vsResetDelay'])
                    except ValueError:
                        pass
                    if not 0 <= vsResetDelay <= 5:
                        error = ('Reset delay time must be a number between '
                                 '0 and 5 seconds')
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
        LOG.threaddebug('Plugin._activateOpenerRelay called "%s"', dev.name)
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
            error = 'door action ignored; no activation relay specified.'
            LOG.error(error)

    def closeGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug('Plugin.closeGarageDoor called "%s"', dev.name)
        if dev.states['doorStatus.open']:  # Close only if currently open.
            self._toggleActivationRelay(dev)

    def openGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug('Plugin.openGarageDoor called "%s"', dev.name)
        if dev.states['doorStatus.closed']:  # Open only if currently closed.
            self._toggleActivationRelay(dev)

    def toggleGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug('Plugin.toggleGarageDoor called "%s"', dev.name)
        self._toggleActivationRelay(dev)

    def actionControlDevice(self, action, dev):
        LOG.threaddebug('Plugin.actionControlDevice called "%s"', dev.name)
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            if dev.states['doorStatus.open']:  # Close only if currently open.
                self._toggleActivationRelay(dev)
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            if dev.states['doorStatus.closed']:  # Open only if closed.
                self._toggleActivationRelay(dev)
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            self._toggleActivationRelay(dev)

    def actionControlUniversal(self, action, dev):
        LOG.threaddebug('Plugin.actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            LOG.info('"%s" is %s', dev.name, dev.states['doorStatus'])
