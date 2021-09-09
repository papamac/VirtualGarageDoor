# coding=utf-8
"""
###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                                                                             #
###############################################################################

 PACKAGE:  Virtual Garage Door
  MODULE:  plugin.py
   TITLE:  primary module in the Virtual Garage Door indigo plugin bundle
FUNCTION:  Monitors multiple indigo devices to track garage door motion
           and report the door state in the states dictionary of an opener
           device.
   USAGE:  plugin.py is included in a standard indigo plugin bundle.
  AUTHOR:  papamac
 VERSION:  1.1.2
    DATE:  September 9, 2021


MIT LICENSE:

Copyright (c) 2020-2021 David A. Krause, aka papamac

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

v1.1.1   2/16/2021  Allow the plugin to utilize on/off state names other than
                    the usual "onOffState".  This allows the use of EasyDAQ
                    digital input/output/relay devices that include the channel
                    number in the state name, e.g., "channel01".
v1.1.2    9/9/2021  Eliminate the numeric door state and change it to a
                    descriptive door status.  Improve the state display in the
                    primary indigo display.  Delete the travel timer device in
                    the deviceStopCom method to avoid the accumulation of
                    orphan timers.

"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = u'papamac'
__version__ = u'1.1.2'
__date__ = u'September 9, 2021'

from logging import getLogger, NOTSET

import indigo

# Globals:

LOG = getLogger(u'Plugin')                # Standard logger.
EASYDAQ_DEVICE_TYPE_IDs = (u'easyDaq4r4io',    u'easyDaq16r8io',
                           u'easyDaq24r',      u'easyDaq24io',
                           u'easyDaq8r',       u'easyDaq8ii4io4r'
                           u'easyDaqDo24Stack')
SENSOR_DEVICE_TYPE_IDs = ((u'alarmZone',       u'contactSensor',
                           u'digitalInput',    u'zwOnOffSensorType')
                          + EASYDAQ_DEVICE_TYPE_IDs)
RELAY_DEVICE_TYPE_IDs = ((u'digitalOutput',   u'relay')
                         + EASYDAQ_DEVICE_TYPE_IDs)


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

        # The devices dictionary is a local (non-persistent), compound
        # dictionary that stores device id's and properties for devices that
        # are monitored by the virtual garage door opener plugin.  It has the
        # following structure:
        #
        # self.devices = {devId: {mDevId: {mDevState: mDevType}}}
        # where:
        #    devId     is the device id of the opener device.
        #    mDevId    is the device id of a sensor or timer to be monitored by
        #              the opener plugin to determine the garage door state.
        #              Sensors must have an on/off bool state defined by
        #              <ValueType boolType="OnOff">Boolean</ValueType>.
        #    mDevState is the state name to be monitored by the plugin.  For
        #              most sensor devices it is typically "onOffState".  For
        #              EasyDAQ devices it is "channelnn" where nn is the
        #              numeric channel number.  For timers the state name is
        #              "timerStatus".
        #    mDevType  is the type of the monitored sensor/timer device
        #              that allows the plugin to interpret state changes. Types
        #              are "travelTimer", "closedSensor", "openSensor", and
        #              "actuatorRelay".
        #
        # self.devices is created/updated by the deviceStartComm method and
        # used by the deviceUpdated method to select devices of interest and
        # determine how to interpret their state changes.  self.devices is also
        # used in the validateDeviceConfigUi method to ensure that mDevId/
        # mDevState combinations are not reused across the various opener
        # devices/sensors.  Timers are exempt from this checking because they
        # are created by the deviceStartComm method and are thus guaranteed to
        # be unique for each opener device.

        self.devices = {}
        pluginId = u'com.perceptiveautomation.indigoplugin.timersandpesters'
        self.timerPlugin = indigo.server.getPlugin(pluginId)
        self.timerDevIds = {}

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

    def _timerAction(self, timerDevId, action):
        self.timerPlugin.executeAction(action, deviceId=timerDevId)

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
        devId = dev.id

        # Clear the devices dictionary for this opener device.

        self.devices[devId] = {}

        # Create an open/close travel timer and add it to the devices
        # dictionary.

        travelTimer = u'%s-timer' % devId
        description = (u'Automatically generated timer for "%s"'
                       % dev.name)
        pluginId = (u'com.perceptiveautomation.indigoplugin.'
                    u'timersandpesters')
        props = dict(amount=dev.pluginProps[u'travelTime'],
                     amountType=u'seconds')
        indigo.device.create(protocol=indigo.kProtocol.Plugin,
                             name=travelTimer,
                             description=description,
                             pluginId=pluginId,
                             deviceTypeId=u'timer',
                             props=props,
                             folder=u'doors')
        timerDev = indigo.devices[travelTimer]

        self.devices[devId][timerDev.id] = {}
        self.devices[devId][timerDev.id][u'timerStatus'] = u'travelTimer'
        self.timerDevIds[devId] = timerDev.id

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

                if not self.devices[devId].get(mDevId):
                    self.devices[devId][mDevId] = {}
                self.devices[devId][mDevId][mDevState] = mDevType

                # Return the normalized state of the monitored device.

                p = u'invert' + mDevType[0].upper() + mDevType[1:] + u'State'
                invert = dev.pluginProps.get(p, False)
                return mDev.states[mDevState] ^ invert

        # Optionally add entries for a closedSensor, openSensor, and
        # actuatorRelay.

        closedSensorState = addToDevicesDict(u'closedSensor')
        openSensorState = addToDevicesDict(u'openSensor')
        addToDevicesDict(u'actuatorRelay')
        LOG.debug(self.devices[devId])

        # Initialize status/state for the opener device.  Assume that door is
        # not in motion and that its status is closed unless the closedSensor
        # or openSensor indicate otherwise.

        doorState = u'closed'
        if not closedSensorState or openSensorState:
            doorState = u'open'
        self._updateDoorStates(dev, doorState)

    def deviceStopComm(self, dev):
        LOG.threaddebug(u'Plugin.deviceStopComm called "%s"', dev.name)

        # Find the timer device in the devices dictionary and delete it.

        for mDevId in self.devices[dev.id]:
            mDev = indigo.devices[mDevId]
            if mDev.deviceTypeId == u'timer':
                indigo.device.delete(mDevId)
                break

        # Delete the device's entry in the devices dictionary.

        del self.devices[dev.id]

    def deviceUpdated(self, oldDev, newDev):
        indigo.PluginBase.deviceUpdated(self, oldDev, newDev)
        for devId in self.devices:
            if oldDev.id in self.devices[devId]:
                mDevId = oldDev.id
                for mDevState in self.devices[devId][mDevId]:
                    if mDevState in oldDev.states:

                        # Both the oldDev and an oldDev state are in the
                        # monitored device dictionary.

                        dev = indigo.devices[devId]
                        priorDoorState = dev.states[u'state']
                        openSensor = dev.pluginProps.get(u'openSensor')
                        closedSensor = dev.pluginProps.get(u'closedSensor')
                        mDevType = self.devices[devId][mDevId][mDevState]
                        timerDevId = self.timerDevIds[devId]

                        if mDevType == u'travelTimer':
                            oldState = oldDev.states[mDevState]
                            newState = newDev.states[mDevState]

                            LOG.debug(u'received "%s" state change %s --> %s'
                                      % (oldDev.name, oldState, newState))

                            if oldState == (u'active'
                                            and newState == u'inactive'):

                                # Timer has expired.

                                if priorDoorState == u'opening':
                                    if openSensor:
                                        self._updateDoorStates(dev, u'stopped')
                                    else:
                                        self._updateDoorStates(dev, u'open')
                                elif priorDoorState == u'closing':
                                    if closedSensor:
                                        self._updateDoorStates(dev,
                                                               u'reversing')
                                    else:
                                        self._updateDoorStates(dev, u'closed')

                        elif mDevType == u'closedSensor':
                            invert = dev.pluginProps[u'invertClosedSensorState'
                                                     ]
                            oldState = oldDev.states[mDevState] ^ invert
                            newState = newDev.states[mDevState] ^ invert

                            # state == 0 <--> door not closed.
                            # state == 1 <--> door closed.

                            LOG.debug(u'received "%s" state change %s --> %s'
                                      % (oldDev.name, oldState, newState))

                            if oldState < newState:  # not closed --> closed.
                                self._updateDoorStates(dev, u'closed')
                                self._timerAction(timerDevId, u'stopTimer')
                            elif oldState > newState:  # closed --> not closed.
                                self._updateDoorStates(dev, u'opening')
                                self._timerAction(timerDevId, u'restartTimer')

                        elif mDevType == u'openSensor':
                            invert = dev.pluginProps[u'invertOpenSensorState']
                            oldState = oldDev.states[mDevState] ^ invert
                            newState = newDev.states[mDevState] ^ invert

                            # state == 0 <--> door not open.
                            # state == 1 <--> door open.

                            LOG.debug(u'received "%s" state change %s --> %s'
                                      % (oldDev.name, oldState, newState))

                            if oldState < newState:  # Not open --> open.
                                if priorDoorState == u'closing':
                                    self._updateDoorStates(dev, u'reversing')
                                self._updateDoorStates(dev, u'open')
                                self._timerAction(timerDevId, u'stopTimer')
                            elif oldState > newState:  # open --> not open.
                                self._updateDoorStates(dev, u'closing')
                                self._timerAction(timerDevId, u'startTimer')

                        elif mDevType == u'actuatorRelay':
                            oldState = oldDev.states[u'onOffState']
                            newState = newDev.states[u'onOffState']

                            # state == 0 <--> actuatorRelay is open.
                            # state == 1 <--> actuatorRelay is closed.

                            # The actuatorRelay is assumed to be momentary; it
                            # closes to start the actuator and then opens in a
                            # second or less to prepare for the next actuation.
                            # The following code ignores the closing event
                            # (oldState > newState) and uses the opening event
                            # (oldState < newState) as an indicator of opener
                            # actuation.

                            LOG.debug(u'received "%s" state change %s --> %s'
                                      % (oldDev.name, oldState, newState))

                            if oldState < newState:  # actuatorRelay opened.
                                if priorDoorState == u'closed':
                                    if not closedSensor:
                                        # Ignore if closedSensor.
                                        self._updateDoorStates(dev, u'opening')
                                        self._timerAction(timerDevId,
                                                          u'restartTimer')
                                else:  # Assume that door is open.
                                    if not openSensor:
                                        # Ignore if openSensor.
                                        self._updateDoorStates(dev, u'closing')
                                        self._timerAction(timerDevId,
                                                          u'restartTimer')

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

        # Clear self.devices for this opener to prevent previous device
        # configurations from generating ConfigUi errors.

        self.devices[devId] = {}

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
                for devId_ in self.devices:
                    for mDevId_ in self.devices[devId_]:
                        for mDevState_ in self.devices[devId_][mDevId_]:
                            if mDevId == mDevId_ and mDevState == mDevState_:
                                err = u'Device/state already in use'
                                errors[mDevType] = err
                                errors[mDevTypeStateName] = err
                                return

                # Add keys/values to self.devices to mark this device/state
                # combination as used.  Note that these additions are
                # overwritten (with the same data) when the opener device is
                # initialized by the deviceStartComm method.

                if not self.devices[devId].get(mDevId):
                    self.devices[devId][mDevId] = {}
                self.devices[devId][mDevId][mDevState] = mDevType
                LOG.debug(self.devices[devId])

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
