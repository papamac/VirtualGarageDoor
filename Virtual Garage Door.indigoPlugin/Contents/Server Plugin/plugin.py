# coding=utf-8
###############################################################################
#                                                                             #
#                           VIRTUAL GARAGE DOOR                               #
#                             MODULE plugin.py                                #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Virtual Garage Door - Monitoring and control of conventional garage
           door openers for Indigo
  MODULE:  plugin.py
   TITLE:  primary module in the Virtual Garage Door Indigo plugin bundle
FUNCTION:  Monitors multiple Indigo devices to track garage door motion
           and report the door state in the states dictionary of an opener
           device.  Provides actions to open, close and toggle the garage door.
   USAGE:  plugin.py is included in a standard Indigo plugin bundle.
  AUTHOR:  papamac
 VERSION:  0.9.0
    DATE:  May 31, 2022


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
                    descriptive door status.  Improve the state display in the
                    primary Indigo display.  Delete the travel timer device in
                    the deviceStopCom method to avoid the accumulation of
                    orphan timers.
v0.7.1   4/13/2022  Perform error checking for travel timer creation.  Abort
                    device startup on timer error.
v0.7.2   4/20/2022  Change the travelTimer state name from the text value
                    "timerStatus" to the boolean value "timerStatus.active"
                    for symmetry in device monitoring.
v0.8.0   4/30/2022  Revise the door state transition processing to use a state
                    transition model based on the behavior of LiftMaster garage
                    door openers.  A state transition diagram is included in
                    README file that is included in this bundle.  It is encoded
                    in the DOOR_STATE_TRANSITIONS dictionary in this module
                    with references to the state transition diagram.  LOG
                    warning messages for monitored device state changes that
                    are inconsistent with the model.
v0.9.0   5/31/2022  (1) Add a new monitored device called activationSensor that
                    turns on when the garage door opener is activated.  Keep
                    the openerRelay (formally actuatorRelay) only for use in
                    controlling the door.
                    (2) Add openerRelay processing for activating an EasyDAQ
                    relay.
                    (3) Update for Python 3.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.9.0'
__date__ = 'May 31, 2022'

from datetime import datetime
from logging import getLogger, NOTSET

import indigo

# Globals:

LOG = getLogger('Plugin')  # Standard logger.
TIMER_PLUGIN_ID = 'com.perceptiveautomation.indigoplugin.timersandpesters'

EASYDAQ_DEVICE_TYPE_IDs = ('easyDaq4r4io',    'easyDaq16r8io',
                           'easyDaq24r',      'easyDaq24io',
                           'easyDaq8r',       'easyDaq8ii4io4r',
                           'easyDaqDo24Stack')
RELAY_DEVICE_TYPE_IDs = (('digitalOutput',   'relay')
                         + EASYDAQ_DEVICE_TYPE_IDs)
SENSOR_DEVICE_TYPE_IDs = (('alarmZone',       'contactSensor',
                           'digitalInput',    'zwOnOffSensorType')
                          + RELAY_DEVICE_TYPE_IDs)

DOOR_STATE_TRANSITIONS = {

    # doorState   mDevEvent+condition              new doorState   ref no

    'closed':    {'travelTimerOff':                 'noChange',     # 1
                  'closedSensorOff':                'opening',      # 2
                  'openSensorOn':                   'open',         # 3
                  'activationSensorOn':             'opening'},     # 4
    'opening':   {'travelTimerOff+noOpenSensor':    'open',         # 5
                  'travelTimerOff':                 'stopped',      # 6
                  'closedSensorOff':                'noChange',     # 7
                  'openSensorOn':                   'open',         # 8
                  'activationSensorOn':             'stopped'},     # 9
    'open':      {'travelTimerOff':                 'noChange',     # 10
                  'closedSensorOn':                 'closed',       # 11
                  'openSensorOff':                  'closing',      # 12
                  'activationSensorOn':             'closing'},     # 13
    'closing':   {'travelTimerOff+noClosingSensor': 'closed',       # 14
                  'travelTimerOff':                 'opening',      # 15
                  'closedSensorOn':                 'closed',       # 16
                  'openSensorOff':                  'noChange',     # 17
                  'openSensorOn':                   'open',         # 18
                  'activationSensorOn':             'opening'},     # 19
    'stopped':   {'travelTimerOff':                 'noChange',     # 20
                  'closedSensorOn':                 'closed',       # 21
                  'openSensorOn':                   'open',         # 22
                  'activationSensorOn':             'closing'}}     # 23


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
    #                INITILIZATION, STARTUP, AND RUN/STOP METHODS             #
    #                                                                         #
    ###########################################################################

    # Private methods:

    def __init__(self, pluginId, pluginDisplayName,
                 pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        # The monitored devices dictionary is a local (non-persistent),
        # compound dictionary that stores device id's and properties for
        # devices that are monitored by the virtual garage door opener plugin.
        # It has the following structure:
        #
        # self._monitoredDevices = {devId: {mDevId: {mDevState: mDevType}}}
        # where:
        #    devId     is the device id of the opener device.
        #    mDevId    is the device id of a timer, sensor, or relay device to
        #              be monitored by the opener plugin to determine the
        #              garage door state.  All monitored devices must have an
        #              on/off bool state defined in the devices xml by
        #              <ValueType boolType="OnOff">Boolean</ValueType>.
        #    mDevState is the state name to be monitored by the plugin.  For
        #              most sensor devices it is typically "onOffState".  For
        #              EasyDAQ devices it is "channelnn" where nn is the
        #              numeric channel number.  For timers the state name is
        #              "timerStatus.active".
        #    mDevType  is the type of the monitored device that allows the
        #              plugin to interpret state changes. Types are
        #              "travelTimer", "closedSensor", "openSensor", and
        #              "activationSensor".
        #
        # self._monitoredDevices is created by the deviceStartComm method and
        # used by the deviceUpdated method to select monitored devices and
        # interpret their state changes.  self._monitoredDevices is also used
        # in the validateDeviceConfigUi method to ensure that mDevId/mDevState
        # combinations are not reused across the various opener devices/
        # sensors.  Timers are exempt from this checking because they are
        # created by the deviceStartComm method and are thus guaranteed to be
        # unique for each opener device.

        self._monitoredDevices = {}

        self._timerPlugin = indigo.server.getPlugin(TIMER_PLUGIN_ID)
        self._timerDevices = {}

        self._priorEventTime = datetime.now()

    def __del__(self):
        LOG.threaddebug('Plugin.__del__ called')
        indigo.PluginBase.__del__(self)

    @staticmethod
    def _updateDoorStates(dev, doorState):
        dev.updateStateOnServer('state', doorState)
        onOffState = doorState != 'closed'
        dev.updateStateOnServer('onOffState', onOffState, uiValue=doorState)
        if onOffState:
            dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
        else:
            dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
        LOG.info('"%s" update to %s', dev.name, doorState)

    # Indigo plugin.py standard public instance methods:

    def startup(self):
        self.indigo_log_handler.setLevel(NOTSET)
        level = self.pluginPrefs['loggingLevel']
        LOG.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        LOG.threaddebug('Plugin.startup called')
        LOG.debug(self.pluginPrefs)
        indigo.devices.subscribeToChanges()

    def deviceStartComm(self, dev):
        LOG.threaddebug('Plugin.deviceStartComm called "%s"', dev.name)

        # Create a new monitored devices dictionary entry for this opener
        # device.

        devId = dev.id
        self._monitoredDevices[devId] = {}

        # Delete travel timer, if any, from a previous execution.

        travelTimer = '%s-timer' % devId
        if travelTimer in indigo.devices:
            LOG.warning('"%s" travel timer already exists', travelTimer)
            indigo.device.delete(travelTimer)

        # Create a new timer with props for this opener.

        description = ('Automatically generated timer for "%s"'
                       % dev.name)
        props = dict(amount=dev.pluginProps['travelTime'],
                     amountType='seconds')

        try:
            indigo.device.create(protocol=indigo.kProtocol.Plugin,
                                 name=travelTimer,
                                 description=description,
                                 pluginId=TIMER_PLUGIN_ID,
                                 deviceTypeId='timer',
                                 props=props,
                                 folder='doors')
        except Exception as errorMessage:
            LOG.error('"%s" timer error: %s; device start aborted',
                      dev, errorMessage)
            self.deviceStopComm(dev)
            return

        # Good timer; add it to the devices dictionary.

        tDev = indigo.devices[travelTimer]
        self._monitoredDevices[devId][tDev.id] = {}
        self._monitoredDevices[devId][tDev.id]['timerStatus.active'] = \
            'travelTimer'
        self._timerDevices[devId] = tDev.id

        # Optionally add entries to the devices dictionary for monitored
        # devices that are specified in the ConfigUi.  Return the current state
        # of the monitored device.

        def addToDevicesDict(mDevType):
            mDevName = dev.pluginProps.get(mDevType)
            if mDevName:  # Monitored device is specified in the ConfigUi.
                mDev = indigo.devices[mDevName]
                mDevId = mDev.id
                mDevState = dev.pluginProps[mDevType + 'StateName']

                # Add a new entry in the devices dictionary.

                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevState] = mDevType

                # Return the normalized state of the monitored device.

                invName = 'invert%s%sState' % (mDevType[0].upper(),
                                               mDevType[1:])
                invert = dev.pluginProps.get(invName, False)
                return mDev.states[mDevState] ^ invert

        # Optionally add entries for a closedSensor, openSensor, and
        # activationSensor.

        closedSensorState = addToDevicesDict('closedSensor')
        openSensorState = addToDevicesDict('openSensor')
        addToDevicesDict('activationSensor')
        LOG.debug(self._monitoredDevices[devId])

        # Initialize the state of the opener device.  Assume that door is
        # not in motion and that it is closed unless the closedSensor and
        # openSensor indicate otherwise.

        doorState = 'closed'
        if not closedSensorState and openSensorState:
            doorState = 'open'
        self._updateDoorStates(dev, doorState)

    def deviceStopComm(self, dev):
        LOG.threaddebug('Plugin.deviceStopComm called "%s"', dev.name)

        # Delete the entry in the monitored devices dictionary, if present.

        if dev.id in self._monitoredDevices:
            del self._monitoredDevices[dev.id]

        # Delete the travel timer associated with this device.

        tDevId = self._timerDevices.get(dev.id)
        if tDevId:
            indigo.device.delete(tDevId)

    def deviceUpdated(self, oldDev, newDev):
        indigo.PluginBase.deviceUpdated(self, oldDev, newDev)
        for devId in self._monitoredDevices:
            if oldDev.id in self._monitoredDevices[devId]:
                dev = indigo.devices[devId]
                mDevId = oldDev.id
                for mDevState in self._monitoredDevices[devId][mDevId]:

                    # Check to ensure that mDevState is in the oldDev states
                    # dictionary.

                    if mDevState not in oldDev.states:
                        LOG.warning('"%s" monitored device "%s" has no '
                                    'state %s',
                                    dev.name, oldDev.name, mDevState)
                        continue

                    # Both the oldDev and an oldDev state are in the
                    # monitored devices dictionary.  Get the mDevStates
                    # for both the old (unchanged) device object and the
                    # new (updated) device object.

                    mDevType = (self._monitoredDevices
                               [devId][mDevId][mDevState])
                    invName = 'invert%s%sState' % (mDevType[0].upper(),
                                                   mDevType[1:])
                    invert = dev.pluginProps.get(invName, False)
                    oldState = oldDev.states[mDevState] ^ invert
                    newState = newDev.states[mDevState] ^ invert

                    # Ignore most mDevState state changes that don't affect the
                    # doorState.  These include:
                    #   No change (oldState == newState).
                    #   travelTimer changed to on (active).
                    #   activationSensor changed to off.

                    doorState = dev.states['state']
                    if (oldState == newState
                            or (mDevType == 'travelTimer'
                                and newState)
                            or (mDevType == 'activationSensor'
                                and not newState)):
                        continue

                    # Log relevant mDevState change for debug.

                    LOG.debug('"%s" %s updated to %s',
                              dev.name, mDevType, ('off', 'on')[newState])

                    # Create a key and look up the new doorState in the
                    # doorStates dictionary.

                    mDevEvent = mDevType + ('Off', 'On')[newState]

                    # Add "noSensor" conditions for travelTimerOff events that
                    # have different meanings for opening and closing
                    # doorStates.

                    if mDevEvent == 'travelTimerOff':
                        if doorState == 'opening':
                            openSensor = dev.pluginProps.get('openSensor')
                            mDevEvent += ('+noOpenSensor' if not openSensor
                                          else '')
                        elif doorState == 'closing':
                            closedSensor = dev.pluginProps.get('closedSensor')
                            mDevEvent += ('+noClosedSensor' if not closedSensor
                                          else '')

                    # Update doorState using the DOOR_STATE_TRANSITIONS
                    # dictionary.

                    try:
                        newDoorState = (DOOR_STATE_TRANSITIONS
                                        [doorState][mDevEvent])
                    except KeyError:
                        LOG.warning('"%s" mDevEvent %s is inconsistent '
                                    'with doorState %s',
                                    dev.name, mDevEvent, doorState)
                        continue
                    if newDoorState == 'noChange':
                        continue

                    self._updateDoorStates(dev, newDoorState)

                    # Log state change details with time since last change for
                    # debug.

                    eventTime = datetime.now()
                    dt = (eventTime - self._priorEventTime).total_seconds()
                    self._priorEventTime = eventTime
                    if dt > 100:
                        dt = 0
                    LOG.debug('%s %5.2f %s %s %s', str(eventTime)[-15:], dt,
                              doorState, mDevEvent, newDoorState)

                    # Conclude with the appropriate timer action.

                    action = ('restartTimer' if newDoorState.endswith('ing')
                              else 'stopTimer')
                    tDevId = self._timerDevices[devId]
                    self._timerPlugin.executeAction(action, deviceId=tDevId)

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
    ###########################################################################

    @staticmethod
    def validatePrefsConfigUi(valuesDict):
        LOG.threaddebug('Plugin.validatePrefsConfigUi called')
        level = valuesDict['loggingLevel']
        LOG.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        return True

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        dev = indigo.devices[devId]
        LOG.threaddebug('Plugin.validateDeviceConfigUi called "%s"', dev.name)
        for item in valuesDict:
            if valuesDict[item] == 'None':
                valuesDict[item] = None
        LOG.debug(valuesDict)
        errors = indigo.Dict()

        # Clear self._monitoredDevices for this opener to prevent previous
        # device configurations from generating ConfigUi errors.

        self._monitoredDevices[devId] = {}

        # Validate open/close travel time entry.

        travelTime = valuesDict['travelTime']
        tTime = 0
        try:
            tTime = int(travelTime)
        except ValueError:
            pass
        if not 8 <= tTime <= 20:
            error = 'Travel time must be an integer between 8 and 20'
            errors['travelTime'] = error

        # Validate closedSensor, openSensor, and activationSensor device
        # entries if these are specified in the ConfigUi.

        def validateMonitoredDeviceEntry(mDevType):
            mDevName = valuesDict.get(mDevType)
            if mDevName:

                # Validate the state name for this device type.

                mDevTypeStateName = mDevType + 'StateName'
                mDevState = valuesDict.get(mDevTypeStateName)
                mDev = indigo.devices[mDevName]
                if mDev.deviceTypeId in EASYDAQ_DEVICE_TYPE_IDs:
                    if (len(mDevState) != 9
                            or mDevState[:7] != 'channel'
                            or not mDevState[7:8].isdigit()):
                        err = 'Invalid EasyDAQ state name'
                        errors[mDevTypeStateName] = err
                        return
                    else:
                        channel = int(mDevState[7:8])
                        if not 1 <= channel <= 24:
                            err = ('EasyDAQ channel number must be an integer '
                                   'between 01 and 24')
                            errors[mDevTypeStateName] = err
                            return

                elif mDevState != 'onOffState':
                    errors[mDevTypeStateName] = 'Invalid state name'
                    return

                # Check to ensure that no device/state combinations are reused
                # by this opener or other openers.

                mDevId = indigo.devices[mDevName].id
                for devId_ in self._monitoredDevices:
                    for mDevId_ in self._monitoredDevices[devId_]:
                        for mDevState_ in (self._monitoredDevices[devId_]
                                          [mDevId_]):
                            if mDevId == mDevId_ and mDevState == mDevState_:
                                err = 'Device/state already in use'
                                errors[mDevType] = err
                                errors[mDevTypeStateName] = err
                                return

                # Add keys/values to self._monitoredDevices to mark this
                # device/state combination as used.  Note that these additions
                # are overwritten (with the same data) when the opener device
                # is initialized by the deviceStartComm method.

                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevState] = mDevType
                LOG.debug(self._monitoredDevices[devId])

        validateMonitoredDeviceEntry('closedSensor')
        validateMonitoredDeviceEntry('openSensor')
        validateMonitoredDeviceEntry('activationSensor')

        # Validate the openerRelay device entries if specified in the ConfigUi.

        openerRelay = valuesDict.get('openerRelay')
        if openerRelay:
            rDev = indigo.devices[openerRelay]
            if rDev.deviceTypeId in EASYDAQ_DEVICE_TYPE_IDs:
                relayChannel = 0
                try:
                    relayChannel = int(valuesDict['easyDAQRelayChannel'])
                except ValueError:
                    pass
                if not 1 <= relayChannel <= 16:
                    error = ('EasyDAQ relay channel must be an integer '
                             'between 1 and 16')
                    errors['openerRelay'] = error

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
    #  def getSensorDeviceList(filter="", valuesDict=None, typeId="",         #
    #                          targetId=0)                                    #
    #  def getRelayDeviceList(filter="", valuesDict=None, typeId="",          #
    #                         targetId=0)                                     #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def getSensorDeviceList(*args):
        LOG.threaddebug('Plugin.getSSensorDeviceList called')
        sensors = []
        for dev in indigo.devices:
            if dev.deviceTypeId in SENSOR_DEVICE_TYPE_IDs:
                sensors.append(dev.name)
        return ['None'] + sorted(sensors)

    #  def getRelayDeviceList(filter="", valuesDict=None, typeId="", targetId=0

    @staticmethod
    def getRelayDeviceList(*args):
        LOG.threaddebug('Plugin.getRelayDeviceList called')
        relays = []
        for dev in indigo.devices:
            if dev.deviceTypeId in RELAY_DEVICE_TYPE_IDs:
                relays.append(dev.name)
        return ['None'] + sorted(relays)

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
    # def _activateOpenerRelay(relay)                                         #
    # def closeGarageDoor(self, pluginAction)                                 #
    # def openGarageDoor(self, pluginAction)                                  #
    # def toggleGarageDoor(self, pluginAction)                                #
    # def actionControlDevice(self, action, dev)                              #
    # def actionControlUniversal(action, dev)                                 #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def _activateOpenerRelay(dev):
        LOG.threaddebug('Plugin._activateOpenerRelay called "%s"', dev.name)
        openerRelay = dev.pluginProps.get('openerRelay')
        if openerRelay:
            rDev = indigo.devices[openerRelay]
            if rDev.deviceTypeId in EASYDAQ_DEVICE_TYPE_IDs:  # EasyDAQ relay.
                plugin = indigo.server.getPlugin(rDev.pluginId)
                relayChannel = int(dev.pluginProps['easyDAQRelayChannel'])
                props = dict(channelSel=relayChannel)
                plugin.executeAction('turnOnOutput', deviceId=rDev.id,
                                     props=props)
                plugin.executeAction('turnOffOutput', deviceId=rDev.id,
                                     props=props)
            else:  # Standalone relay device.
                indigo.device.turnOn(openerRelay, duration=1)
        else:
            error = 'garage door action ignored; no opener relay specified.'
            LOG.error(error)

    def closeGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        if dev.states['state.open']:  # Close only if currently open.
            self._activateOpenerRelay(dev)

    def openGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        if dev.states['state.closed']:  # Open only if currently closed.
            self._activateOpenerRelay(dev)

    def toggleGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        self._activateOpenerRelay(dev)

    def actionControlDevice(self, action, dev):
        LOG.threaddebug('Plugin.actionControlDevice called "%s"', dev.name)
        if action.deviceAction == indigo.kDeviceAction.TurnOff:
            if dev.states['state.open']:  # Close only if currently open.
                self._activateOpenerRelay(dev)
        elif action.deviceAction == indigo.kDeviceAction.TurnOn:
            if dev.states['state.closed']:  # Open only if currently closed.
                self._activateOpenerRelay(dev)
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            self._activateOpenerRelay(dev)

    def actionControlUniversal(self, action, dev):
        LOG.threaddebug('Plugin.actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            doorState = dev.states['state']
            LOG.info('"%s" is %s', dev.name, doorState)
