# coding=utf-8
"""
 PACKAGE:  indigo plugin interface to PiDACS (PiDACS-Bridge)
  MODULE:  plugin.py
   TITLE:  primary Python module in the PiDACS indigo plugin bundle (plugin)
FUNCTION:  plugin is a PiDACS client that can connect to multiple PiDACS
           servers (instances of pidacs) and interface with indigo GUIs and
           device objects.
   USAGE:  plugin.py is included in a standard indigo plugin bundle.
  AUTHOR:  papamac
 VERSION:  1.5.2
    DATE:  June 8, 2020


MIT LICENSE:

Copyright (c) 2018-2020 David A. Krause, aka papamac

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

plugin imports the modules colortext and messagesocket from papamaclib.
Because the indigo plugin bundle is a standalone container, the primary
papamaclib cannot be externally referenced.  A copy of papamaclib with the
modules colortext and messagesocket (and __init__.py) must be included in the
bundle.

"""

__author__ = u'papamac'
__version__ = u'1.5.2'
__date__ = u'June 8, 2020'

from logging import getLogger, NOTSET

import indigo
from indigoAttachments import pluginAction

# Globals:

LOG = getLogger(u'Plugin')                # Standard logger.
DOOR_STATES = {u'open':    0,  u'closed':  1,  u'opening':   2,
               u'closing': 3,  u'stopped': 4,  u'reversed': 5}


class Plugin(indigo.PluginBase):
    """
    **************************** needs work ***********************************
    """
    ###########################################################################
    #                                                                         #
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
        self.devices = {}

    def __del__(self):
        LOG.threaddebug(u'Plugin.__del__ called')
        indigo.PluginBase.__del__(self)

    @staticmethod
    def _getNormalizedSensorState(dev, sensorDev, sensorType):
        LOG.threaddebug(u'Plugin._getNormalizedSensorState called "%s" %s'
                        % (sensorDev.name, sensorType))
        sensorType = sensorType[0].upper() + sensorType[1:]
        sensorState = int(sensorDev.states[u'onOffState'])
        if dev.pluginProps.get(u'invert' + sensorType + u'State'):
            sensorState = 0 if sensorState else 1
        return sensorState

    @staticmethod
    def _updateDoorStates(dev, doorStatus):
        LOG.threaddebug(u'Plugin._updateDoorStates called "%s" %s'
                        % (dev.name, doorStatus))
        dev.updateStateOnServer(key=u'doorState',
                                value=DOOR_STATES[doorStatus])
        dev.updateStateOnServer(key=u'doorStatus', value=doorStatus)
        displayState = u'enabled' if doorStatus == u'closed' else u'faulted'
        dev.updateStateOnServer(key=u'displayState',
                                value=displayState,
                                uiValue=doorStatus)
        onOffState = 0 if doorStatus == u'closed' else 1
        dev.updateStateOnServer(key=u'onOffState', value=onOffState)

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

        # Initialize closed sensor and set initial door states.

        closedSensor = dev.pluginProps[u'closedSensor']
        closedSensorDev = indigo.devices[closedSensor]
        self.devices[closedSensorDev.id] = dev.id, u'closedSensor'
        closedSensorState = self._getNormalizedSensorState(dev,
                            closedSensorDev, u'closedSensor')
        doorStatus = u'closed' if closedSensorState else u'open'
        self._updateDoorStates(dev, doorStatus)

        # Initialize open sensor, if specified.

        openSensor = dev.pluginProps.get(u'openSensor')
        if openSensor:
            openSensorDev = indigo.devices[openSensor]
            self.devices[openSensorDev.id] = dev.id, u'openSensor'

        # Initialize open/close timer, if specified.

        timer = dev.pluginProps.get(u'timer')
        if timer:
            timerDev = indigo.devices[timer]
            self.devices[timerDev.id] = dev.id, u'timer'
            props = dict(amount=dev.pluginProps[u'timeoutValue'],
                         amountType=u'seconds')
            pluginAction(timer, u'setTimerStartValue', props)

        # Initialize actuator relay, if specified.

        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            actuatorRelayDev = indigo.devices[actuatorRelay]
            self.devices[actuatorRelayDev.id] = dev.id, u'actuatorRelay'

    def deviceStopComm(self, dev):
        LOG.threaddebug(u'Plugin.deviceStopComm called "%s"', dev.name)
        for devId in self.devices:
            if self.devices[devId] == dev.id:
                del self.devices[devId]

    def deviceUpdated(self, oldDev, newDev):
        indigo.PluginBase.deviceUpdated(self, oldDev, newDev)
        if oldDev.id in self.devices:
            devId, devType = self.devices[oldDev.id]
            dev = indigo.devices[devId]
            timer = dev.pluginProps.get(u'timer')

            if devType == u'closedSensor':
                oldState = self._getNormalizedSensorState(dev, oldDev, devType)
                newState = self._getNormalizedSensorState(dev, newDev, devType)
                # onOffState == 0 --> door not closed.
                # onOffState == 1 --> door fully closed.
                if oldState < newState:  # not closed --> fully closed.
                    self._updateDoorStates(dev, u'closed')
                    if timer:
                        pluginAction(timer, u'stopTimer')
                elif oldState > newState:  # fully closed --> not closed.
                    self._updateDoorStates(dev, u'opening')
                    if timer:
                        pluginAction(timer, u'startTimer')

            elif devType == u'openSensor':
                oldState = self._getNormalizedSensorState(dev, oldDev, devType)
                newState = self._getNormalizedSensorState(dev, newDev, devType)
                # onOffState == 0 --> door not open.
                # onOffState == 1 --> door fully open.
                if oldState < newState:  # not open --> fully open.
                    priorDoorStatus = dev.states[u'doorStatus']
                    if priorDoorStatus == u'closing':
                        self._updateDoorStates(dev, u'reversed')
                    self._updateDoorStates(dev, u'open')
                    if timer:
                        pluginAction(timer, u'stopTimer')
                elif oldState > newState:  # fully open --> not open.
                    self._updateDoorStates(dev, u'closing')
                    if timer:
                        pluginAction(timer, u'startTimer')

            elif devType == u'timer':
                oldTime = int(oldDev.states[u'timeLeftSeconds'])
                newTime = int(newDev.states[u'timeLeftSeconds'])
                newStatus = newDev.states[u'timerStatus']
                # timeLeftSeconds  > 0 --> door in motion.
                # timeLeftSeconds == 0 --> door has stopped.
                if (oldTime > 0
                        and newTime == 0
                        and newStatus == 'active'):  # Timer has expired.
                    priorDoorStatus = dev.states[u'doorStatus']
                    if priorDoorStatus == u'opening':
                        if dev.pluginProps[u'openSensor']:
                            self._updateDoorStates(dev, u'stopped')
                        else:
                            self._updateDoorStates(dev, u'open')
                    elif priorDoorStatus == u'closing':
                        self._updateDoorStates(dev, u'reversed')

    ###########################################################################
    #                                                                         #
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
        LOG.threaddebug(u'Plugin.validateDeviceConfigUi called "%s"',
                        dev.name)
        errors = indigo.Dict()

        closedSensor = valuesDict.get(u'closedSensor')
        if closedSensor:
            sensorDev = indigo.devices[closedSensor]
            if sensorDev.id in self.devices:
                error = 'Closed sensor already in use; choose another'
                errors[u'closedSensor'] = error
        else:
            errors[u'closedSensor'] = u'Must select a closed sensor'

        openSensor = valuesDict.get(u'openSensor')
        if openSensor:
            sensorDev = indigo.devices[openSensor]
            if sensorDev.id in self.devices or openSensor == closedSensor:
                error = 'Open sensor already in use; choose another'
                errors[u'openSensor'] = error

        timer = valuesDict.get(u'timer')
        if timer:
            timerDev = indigo.devices[timer]
            if timerDev.id in self.devices:
                error = 'Open/close timer already in use; choose another'
                errors[u'timer'] = error
            timeoutValue = valuesDict.get(u'timeoutValue', u'')
            if not (timeoutValue.isdigit() and 20 >= int(timeoutValue) >= 8):
                error = (u'Open/close timeout value must be an integer '
                         'between 8 and 20')
                errors[u'timeoutValue'] = error

        actuatorRelay = valuesDict.get(u'actuatorRelay')
        if actuatorRelay:
            relayDev = indigo.devices[actuatorRelay]
            if relayDev.id in self.devices:
                error = 'Actuator relay already in use; choose another'
                errors[u'actuatorRelay'] = error

        if errors:
            return False, valuesDict, errors
        else:
            return True, valuesDict

    ###########################################################################
    #                                                                         #
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
    def getSensors(filter="", valuesDict=None, typeId="", targetId=0):
        LOG.threaddebug(u'Plugin.getSSensors called')
        sensors = []
        for dev in indigo.devices:
            if dev.deviceTypeId in (u'digitalInput', u'alarmZone',
                                    u'alarmZoneVirtual'):
                sensors.append(dev.name)
        return sorted(sensors)

    @staticmethod
    def getTimers(filter="", valuesDict=None, typeId="", targetId=0):
        LOG.threaddebug(u'Plugin.getTimers called')
        timers = []
        for dev in indigo.devices:
            if dev.deviceTypeId == u'timer':
                timers.append(dev.name)
        return sorted(timers)

    @staticmethod
    def getRelays(filter="", valuesDict=None, typeId="", targetId=0):
        LOG.threaddebug(u'Plugin.getRelays called')
        relays = []
        for dev in indigo.devices:
            if dev.deviceTypeId == u'digitalOutput':
                relays.append(dev.name)
        return sorted(relays)

    ###########################################################################
    #                                                                         #
    #                                     PART                                #
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
    def closeGarageDoor(action, dev):
        LOG.threaddebug(u'Plugin.closeGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            if dev.states[u'doorStatus.open']:
                if action.deviceAction == indigo.kDeviceAction.TurnOn:
                    indigo.device.turnOn(actuatorRelay, duration=1)

    @staticmethod
    def openGarageDoor(action, dev):
        LOG.threaddebug(u'Plugin.openGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            if dev.states[u'doorStatus.closed']:
                if action.deviceAction == indigo.kDeviceAction.TurnOn:
                    indigo.device.turnOn(actuatorRelay, duration=1)
