# coding=utf-8
###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Monitoring and control of conventional garage door openers for
           Indigo (Virtual Garage Door)
  MODULE:  plugin.py
   TITLE:  primary module in the Virtual Garage Door Indigo plugin bundle
FUNCTION:  Monitors multiple Indigo devices to track garage door motion
           and report the door state in the states dictionary of an opener
           device.
   USAGE:  plugin.py is included in a standard Indigo plugin bundle.
  AUTHOR:  papamac
 VERSION:  1.2
    DATE:  April 30, 2022


MIT LICENSE:

Copyright (c) 2021-2022 David A. Krause, aka papamac

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


DESCRIPTION:

****************************** needs work *************************************

DEPENDENCIES/LIMITATIONS:

****************************** needs work *************************************


CHANGE LOG:

Major changes to the Virtual Garage Door plugin are described in the CHANGES.md
file in the top level bundle directory.  Changes of lesser importance may be
described in individual module docstrings if appropriate.

v1.1.1   2/16/2021  Allow the plugin to utilize on/off state names other than
                    the usual "onOffState".  This allows the use of EasyDAQ
                    digital input/output/relay devices that include the channel
                    number in the state name, e.g., "channel01".
v1.1.2   9/ 9/2021  Eliminate the numeric door state and change it to a
                    descriptive door status.  Improve the state display in the
                    primary Indigo display.  Delete the travel timer device in
                    the deviceStopCom method to avoid the accumulation of
                    orphan timers.
v1.1.3   4/13/2022  Perform error checking for travel timer creation.  Abort
                    device startup on timer error.
v1.1.4   4/20/2022  Change the travelTimer state name from the text value
                    "timerStatus" to the boolean value "timerStatus.active"
                    for symmetry in device monitoring.
v1.2     4/30/2022  Revise the door state transition processing to use a state
                    transition model based on the behavior of LiftMaster garage
                    door openers.  A state transition diagram is included in
                    README file that is included in this bundle.  It is encoded
                    in the DOOR_STATE_TRANSITIONS dictionary in this module
                    with references to the state transition diagram.  LOG
                    warning messages for monitored device state changes that
                    are inconsistent with the model.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = u'papamac'
__version__ = u'1.2'
__date__ = u'April 30, 2022'

from datetime import datetime
from logging import getLogger, NOTSET

import indigo

# Globals:

LOG = getLogger(u'Plugin')  # Standard logger.
EASYDAQ_DEVICE_TYPE_IDs = (u'easyDaq4r4io',    u'easyDaq16r8io',
                           u'easyDaq24r',      u'easyDaq24io',
                           u'easyDaq8r',       u'easyDaq8ii4io4r',
                           u'easyDaqDo24Stack')
SENSOR_DEVICE_TYPE_IDs = ((u'alarmZone',       u'contactSensor',
                           u'digitalInput',    u'zwOnOffSensorType')
                          + EASYDAQ_DEVICE_TYPE_IDs)
RELAY_DEVICE_TYPE_IDs = ((u'digitalOutput',   u'relay')
                         + EASYDAQ_DEVICE_TYPE_IDs)

DOOR_STATE_TRANSITIONS = {

    # doorState    mDevEvent+condition                new doorState   ref no

    u'closed':    {u'travelTimerOff':                 u'noChange',     # 1
                   u'closedSensorOff':                u'opening',      # 2
                   u'openSensorOn':                   u'open',         # 3
                   u'actuatorRelayOn':                u'opening'},     # 4
    u'opening':   {u'travelTimerOff+noOpenSensor':    u'open',         # 5
                   u'travelTimerOff':                 u'stopped',      # 6
                   u'closedSensorOff':                u'noChange',     # 7
                   u'openSensorOn':                   u'open',         # 8
                   u'actuatorRelayOn':                u'stopped'},     # 8
    u'open':      {u'travelTimerOff':                 u'noChange',     # 10
                   u'closedSensorOn':                 u'closed',       # 11
                   u'openSensorOff':                  u'closing',      # 12
                   u'actuatorRelayOn':                u'closing'},     # 13
    u'closing':   {u'travelTimerOff+noClosingSensor': u'closed',       # 14
                   u'travelTimerOff':                 u'opening',      # 15
                   u'closedSensorOn':                 u'closed',       # 16
                   u'openSensorOff':                  u'noChange',     # 17
                   u'openSensorOn':                   u'open',         # 18
                   u'actuatorRelayOn':                u'opening'},     # 19
    u'stopped':   {u'travelTimerOff':                 u'noChange',     # 20
                   u'closedSensorOn':                 u'closed',       # 21
                   u'openSensorOn':                   u'open',         # 22
                   u'actuatorRelayOn':                u'closing'}}     # 23


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
        #              "actuatorRelay".
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

        pluginId = u'com.perceptiveautomation.indigoplugin.timersandpesters'
        self._timerPlugin = indigo.server.getPlugin(pluginId)
        self._timerDevices = {}

        self._priorEventTime = datetime.now()

    def __del__(self):
        LOG.threaddebug(u'Plugin.__del__ called')
        indigo.PluginBase.__del__(self)

    @staticmethod
    def _updateDoorStates(dev, doorState):
        dev.updateStateOnServer(u'state', doorState)
        onOffState = doorState != u'closed'
        dev.updateStateOnServer(u'onOffState', onOffState, uiValue=doorState)
        if onOffState:
            dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
        else:
            dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
        LOG.info(u'"%s" update to %s', dev.name, doorState)

    def _timerAction(self, devId, action):
        tDevId = self._timerDevices[devId]
        tDev = indigo.devices[tDevId]
        LOG.debug(u'"%s" %s', tDev.name, action)
        self._timerPlugin.executeAction(action, deviceId=tDevId)

    # Indigo plugin.py standard public instance methods:

    def startup(self):
        self.indigo_log_handler.setLevel(NOTSET)
        level = self.pluginPrefs[u'loggingLevel']
        LOG.setLevel(u'THREADDEBUG' if level == u'THREAD' else level)
        LOG.threaddebug(u'Plugin.startup called')
        LOG.debug(self.pluginPrefs)
        indigo.devices.subscribeToChanges()

    def deviceStartComm(self, dev):
        LOG.threaddebug(u'Plugin.deviceStartComm called "%s"', dev.name)

        # Create a new monitored devices dictionary entry for this opener
        # device.

        devId = dev.id
        self._monitoredDevices[devId] = {}

        # Check for an existing travel timer device.

        travelTimer = u'%s-timer' % devId
        if travelTimer not in indigo.devices:

            # No timer device found, create a new one.

            description = (u'Automatically generated timer for "%s"'
                           % dev.name)
            pluginId = (u'com.perceptiveautomation.indigoplugin.'
                        u'timersandpesters')
            props = dict(amount=dev.pluginProps[u'travelTime'],
                         amountType=u'seconds')

            try:
                indigo.device.create(protocol=indigo.kProtocol.Plugin,
                                     name=travelTimer,
                                     description=description,
                                     pluginId=pluginId,
                                     deviceTypeId=u'timer',
                                     props=props,
                                     folder=u'doors')
            except Exception as errorMessage:
                LOG.error(u'"%s" timer error: %s; device start aborted',
                          dev, errorMessage)
                self.deviceStopComm(dev)
                return

        # Good timer; add it to the devices dictionary.

        tDev = indigo.devices[travelTimer]
        self._monitoredDevices[devId][tDev.id] = {}
        self._monitoredDevices[devId][tDev.id][u'timerStatus.active'] = \
            u'travelTimer'
        self._timerDevices[devId] = tDev.id

        # Optionally add entries to the devices dictionary for monitored
        # devices that are specified in the ConfigUi.  Return the current state
        # of the monitored device.

        def addToDevicesDict(mDevType):
            mDevName = dev.pluginProps.get(mDevType)
            if mDevName:  # Monitored device is specified in the ConfigUi.
                mDev = indigo.devices[mDevName]
                mDevId = mDev.id
                mDevState = dev.pluginProps[mDevType + u'StateName']

                # Add a new entry in the devices dictionary.

                if not self._monitoredDevices[devId].get(mDevId):
                    self._monitoredDevices[devId][mDevId] = {}
                self._monitoredDevices[devId][mDevId][mDevState] = mDevType

                # Return the normalized state of the monitored device.

                invName = u'invert%s%sState' % (mDevType[0].upper(),
                                                mDevType[1:])
                invert = dev.pluginProps.get(invName, False)
                return mDev.states[mDevState] ^ invert

        # Optionally add entries for a closedSensor, openSensor, and
        # actuatorRelay.

        closedSensorState = addToDevicesDict(u'closedSensor')
        openSensorState = addToDevicesDict(u'openSensor')
        addToDevicesDict(u'actuatorRelay')
        LOG.debug(self._monitoredDevices[devId])

        # Initialize the state of the opener device.  Assume that door is
        # not in motion and that it is closed unless the closedSensor and
        # openSensor indicate otherwise.

        doorState = u'closed'
        if not closedSensorState and openSensorState:
            doorState = u'open'
        self._updateDoorStates(dev, doorState)

    def deviceStopComm(self, dev):
        LOG.threaddebug(u'Plugin.deviceStopComm called "%s"', dev.name)

        # Delete the entry in the devices dictionary, if present.

        if dev.id in self._monitoredDevices:
            del self._monitoredDevices[dev.id]

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
                        LOG.warning(u'"%s" monitored device "%s" has no '
                                    u'state %s',
                                    dev.name, oldDev.name, mDevState)
                        continue

                    # Both the oldDev and an oldDev state are in the
                    # monitored devices dictionary.  Get the mDevStates
                    # for both the old (unchanged) device object and the
                    # new (updated) device object.

                    mDevType = (self._monitoredDevices
                               [devId][mDevId][mDevState])
                    invName = u'invert%s%sState' % (mDevType[0].upper(),
                                                    mDevType[1:])
                    invert = dev.pluginProps.get(invName, False)
                    oldState = oldDev.states[mDevState] ^ invert
                    newState = newDev.states[mDevState] ^ invert

                    # Ignore most mDevState state changes that don't affect the
                    # doorState.  These include:
                    #   No change (oldState == newState).
                    #   travelTimer changed to on (active).
                    #   actuatorRelay changed to off (open).

                    doorState = dev.states[u'state']
                    if (oldState == newState
                            or (mDevType == u'travelTimer'
                                and newState)
                            or (mDevType == u'actuatorRelay'
                                and not newState)):
                        continue

                    # Log relevant mDevState change for debug.

                    LOG.debug(u'"%s" %s updated to %s',
                              dev.name, mDevType, (u'off', u'on')[newState])

                    # Create a key and look up the new doorState in the
                    # doorStates dictionary.

                    mDevEvent = mDevType + (u'Off', u'On')[newState]

                    # Add "noSensor" conditions for travelTimerOff events that
                    # have different meanings for opening and closing
                    # doorStates.

                    if mDevEvent == u'travelTimerOff':
                        if doorState == u'opening':
                            openSensor = dev.pluginProps.get(u'openSensor')
                            mDevEvent += (u'+noOpenSensor' if not openSensor
                                          else u'')
                        elif doorState == u'closing':
                            closedSensor = dev.pluginProps.get(u'closedSensor')
                            mDevEvent += (u'+noClosedSensor'
                                          if not closedSensor else u'')

                    # Update doorState using the DOOR_STATE_TRANSITIONS
                    # dictionary.

                    try:
                        newDoorState = (DOOR_STATE_TRANSITIONS
                                        [doorState][mDevEvent])
                    except KeyError:
                        LOG.warning(u'"%s" mDevEvent %s is inconsistent '
                                    u'with doorState %s',
                                    dev.name, mDevEvent, doorState)
                        continue
                    if newDoorState == u'noChange':
                        continue

                    self._updateDoorStates(dev, newDoorState)

                    eventTime = datetime.now()
                    dt = (eventTime - self._priorEventTime).total_seconds()
                    self._priorEventTime = eventTime
                    if dt > 100:
                        dt = 0
                    LOG.warning(u'%s %5.2f %s %s %s', str(eventTime)[-15:], dt,
                                doorState, mDevEvent, newDoorState)

                    if newDoorState.endswith(u'ing'):
                        self._timerAction(devId, u'restartTimer')
                    else:
                        self._timerAction(devId, u'stopTimer')

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
        LOG.threaddebug(u'Plugin.validatePrefsConfigUi called')
        level = valuesDict[u'loggingLevel']
        LOG.setLevel(u'THREADDEBUG' if level == u'THREAD' else level)
        return True

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        dev = indigo.devices[devId]
        LOG.threaddebug(u'Plugin.validateDeviceConfigUi called "%s"', dev.name)
        for item in valuesDict:
            if valuesDict[item] == u'None':
                valuesDict[item] = None
        LOG.debug(valuesDict)
        errors = indigo.Dict()

        # Clear self._monitoredDevices for this opener to prevent previous
        # device configurations from generating ConfigUi errors.

        self._monitoredDevices[devId] = {}

        # Validate open/close travel time entry.

        travelTime = valuesDict[u'travelTime']
        if not (travelTime.isdigit() and 20 >= int(travelTime) >= 8):
            error = (u'Open/close travel time must be an integer between 8 '
                     u'and 20')
            errors[u'travelTime'] = error

        # Validate closedSensor, openSensor, and actuatorRelay device entries
        # if these are specified in the ConfigUi.

        def validateMonitoredDeviceEntry(mDevType):
            mDevName = valuesDict.get(mDevType)
            if mDevName:

                # Validate the state name for this device type.

                mDevTypeStateName = mDevType + u'StateName'
                mDevState = valuesDict.get(mDevTypeStateName)
                mDev = indigo.devices[mDevName]
                if mDev.deviceTypeId in EASYDAQ_DEVICE_TYPE_IDs:
                    if not (mDevState[:7] == u'channel'
                            and mDevState[7:].isnumeric()):
                        errors[mDevTypeStateName] = u'Invalid state name'
                        return
                elif mDevState != u'onOffState':
                    errors[mDevTypeStateName] = u'Invalid state name'
                    return

                # Check to ensure that no device/state combinations are reused
                # by this opener or other openers.

                mDevId = indigo.devices[mDevName].id
                for devId_ in self._monitoredDevices:
                    for mDevId_ in self._monitoredDevices[devId_]:
                        for mDevState_ in self._monitoredDevices[devId_]\
                                [mDevId_]:
                            if mDevId == mDevId_ and mDevState == mDevState_:
                                err = u'Device/state already in use'
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

        validateMonitoredDeviceEntry(u'closedSensor')
        validateMonitoredDeviceEntry(u'openSensor')
        validateMonitoredDeviceEntry(u'actuatorRelay')

        if errors:
            return False, valuesDict, errors
        else:
            return True, valuesDict

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
    def getSensorDeviceList(filter="", valuesDict=None, typeId="", targetId=0):
        LOG.threaddebug(u'Plugin.getSSensorDeviceList called')
        sensors = []
        for dev in indigo.devices:
            if dev.deviceTypeId in SENSOR_DEVICE_TYPE_IDs:
                sensors.append(dev.name)
        return [u'None'] + sorted(sensors)

    @staticmethod
    def getRelayDeviceList(filter="", valuesDict=None, typeId="", targetId=0):
        LOG.threaddebug(u'Plugin.getRelayDeviceList called')
        relays = []
        for dev in indigo.devices:
            if dev.deviceTypeId in RELAY_DEVICE_TYPE_IDs:
                relays.append(dev.name)
        return [u'None'] + sorted(relays)

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
    # def _closeGarageDoor(dev)                                               #
    # def _openGarageDoor(dev)                                                #
    # def _toggleGarageDoor(dev)                                              #
    # def closeGarageDoor(self, pluginAction)                                 #
    # def openGarageDoor(self, pluginAction)                                  #
    # def toggleGarageDoor(self, pluginAction)                                #
    # def actionControlDevice(self, action, dev)                              #
    # def actionControlUniversal(action, dev)                                 #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def _closeGarageDoor(dev):
        LOG.threaddebug(u'Plugin._closeGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            if dev.states[u'state.open']:
                indigo.device.turnOn(actuatorRelay, duration=1)
        else:
            error = u'close garage door ignored; no actuator relay specified.'
            LOG.error(error)

    @staticmethod
    def _openGarageDoor(dev):
        LOG.threaddebug(u'Plugin._openGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            if dev.states[u'state.closed']:
                indigo.device.turnOn(actuatorRelay, duration=1)
        else:
            error = u'open garage door ignored; no actuator relay specified.'
            LOG.error(error)

    @staticmethod
    def _toggleGarageDoor(dev):
        LOG.threaddebug(u'Plugin._toggleGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            indigo.device.turnOn(actuatorRelay, duration=1)
        else:
            error = u'toggle garage door ignored; no actuator relay specified.'
            LOG.error(error)

    def closeGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        self._closeGarageDoor(dev)

    def openGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        self._openGarageDoor(dev)

    def toggleGarageDoor(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        self._toggleGarageDoor(dev)

    def actionControlDevice(self, action, dev):
        LOG.threaddebug(u'Plugin.actionControlDevice called "%s"', dev.name)
        if action.deviceAction == indigo.kDeviceAction.TurnOff:
            self._closeGarageDoor(dev)
        elif action.deviceAction == indigo.kDeviceAction.TurnOn:
            self._openGarageDoor(dev)
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            self._toggleGarageDoor(dev)

    @staticmethod
    def actionControlUniversal(action, dev):
        LOG.threaddebug(u'Plugin.actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            doorState = dev.states[u'state']
            LOG.info(u'"%s" is %s', dev.name, doorState)
