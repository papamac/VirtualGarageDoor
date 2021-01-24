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
 VERSION:  1.1.0
    DATE:  December 27, 2020


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
__version__ = u'1.1.0'
__date__ = u'December 27, 2020'

from logging import getLogger, NOTSET

import indigo
from indigoAttachments import pluginAction

# Globals:

LOG = getLogger(u'Plugin')                # Standard logger.
DOOR_STATES = {u'open':    0,  u'closed':  1,  u'opening':   2,
               u'closing': 3,  u'stopped': 4,  u'reversing': 5}


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

        # The devices dictionary is a local (non-persistent) dictionary that
        # provides device id's and properties for devices that are monitored by
        # the virtual garage door opener plugin.  It has the following
        # structure:

        # self.devices = {openerDevId: {monitoredDevId: devType}}
        #     where devType is in (u'travelTimer', u'closedSensor',
        #                          u'openSensor', u'actuatorRelay')

        # self.devices is created/updated by the deviceStartComm method and
        # used by the deviceUpdated method to select devices of interest and
        # determine how to interpret their state changes.

        self.devices = {}

    def __del__(self):
        LOG.threaddebug(u'Plugin.__del__ called')
        indigo.PluginBase.__del__(self)

    @staticmethod
    def _getNormalizedState(sensorType, sensorDev, openerDev):
        sensorType = sensorType[0].upper() + sensorType[1:]
        sensorState = int(sensorDev.states[u'onOffState'])
        if openerDev.pluginProps[u'invert' + sensorType + u'State']:
            sensorState = 0 if sensorState else 1
        return sensorState

    @staticmethod
    def _updateDoorStates(dev, doorStatus):
        dev.updateStateOnServer(key=u'doorState',
                                value=DOOR_STATES[doorStatus])
        dev.updateStateOnServer(key=u'doorStatus', value=doorStatus)
        displayState = u'enabled' if doorStatus == u'closed' else u'faulted'
        dev.updateStateOnServer(key=u'displayState',
                                value=displayState,
                                uiValue=doorStatus)
        onOffState = 0 if doorStatus == u'closed' else 1
        dev.updateStateOnServer(key=u'onOffState', value=onOffState)
        LOG.info(u'updated "%s" status to %s' % (dev.name, doorStatus))

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
        self.devices[dev.id] = {}

        # Assume that door is not in motion at device initialization and that
        # its status is closed unless the closedSensor or openSensor indicate
        # otherwise.

        doorStatus = u'closed'

        # Initialize open/close travel timer and add it to the devices
        # dictionary.

        travelTimer = u'gar-%s-timer' % unicode(dev.id)
        timerDev = indigo.devices.get(travelTimer)
        props = dict(amount=dev.pluginProps[u'travelTime'],
                     amountType=u'seconds')

        if timerDev:  # Timer already exists.
            pluginAction(travelTimer, u'setTimerStartValue', props)

        else:  # No existing times; create a new one.
            description = u'Automatically generated timer for "%s"' % dev.name
            pluginId = (u'com.perceptiveautomation.indigoplugin.'
                        u'timersandpesters')
            indigo.device.create(protocol=indigo.kProtocol.Plugin,
                                 name=travelTimer,
                                 description=description,
                                 pluginId=pluginId,
                                 deviceTypeId=u'timer',
                                 props=props,
                                 folder=u'security')
            timerDev = indigo.devices[travelTimer]
        self.devices[dev.id][timerDev.id] = u'travelTimer'

        # Add closed sensor, if specified, to devices dictionary and set
        # initial door status.

        closedSensor = dev.pluginProps[u'closedSensor']
        if closedSensor:
            closedSensorDev = indigo.devices[closedSensor]
            self.devices[dev.id][closedSensorDev.id] = u'closedSensor'
            closedSensorState = self._getNormalizedState(u'closedSensor',
                                                         closedSensorDev, dev)
            doorStatus = u'closed' if closedSensorState else u'open'

        # Add open sensor, if specified, to devices dictionary and set
        # initial door status.

        openSensor = dev.pluginProps.get(u'openSensor')
        if openSensor:
            openSensorDev = indigo.devices[openSensor]
            self.devices[dev.id][openSensorDev.id] = u'openSensor'
            openSensorState = self._getNormalizedState(u'openSensor',
                                                       openSensorDev, dev)
            doorStatus = u'open' if openSensorState else u'closed'

        # Update initial door states based on closed/open sensor states.

        self._updateDoorStates(dev, doorStatus)

        # Initialize actuatorRelay, if specified.

        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            relayDev = indigo.devices[actuatorRelay]
            self.devices[dev.id][relayDev.id] = u'actuatorRelay'

        LOG.debug(unicode(self.devices[dev.id]))

    def deviceStopComm(self, dev):
        LOG.threaddebug(u'Plugin.deviceStopComm called "%s"', dev.name)
        del self.devices[dev.id]

    def deviceDeleted(self, dev):
        LOG.threaddebug(u'Plugin.deviceDeleted called "%s"', dev.name)
        if dev.deviceTypeId == u'opener':
            travelTimer = u'devId%s-travelTimer' % unicode(dev.id)
            timerDev = indigo.devices[travelTimer]
            indigo.device.delete(timerDev)
            self.deviceStopComm(dev)

    def deviceUpdated(self, oldDev, newDev):
        indigo.PluginBase.deviceUpdated(self, oldDev, newDev)
        for devId in self.devices:
            if oldDev.id in self.devices[devId]:
                devType = self.devices[devId][oldDev.id]
                dev = indigo.devices[devId]
                priorDoorStatus = dev.states[u'doorStatus']
                openSensor = dev.pluginProps.get(u'openSensor')
                closedSensor = dev.pluginProps.get(u'closedSensor')
                travelTimer = u'gar-%s-timer' % unicode(dev.id)

                if devType == u'travelTimer':
                    oldStatus = oldDev.states[u'timerStatus']
                    oldTime = oldDev.states[u'timeLeftSeconds']
                    newStatus = newDev.states[u'timerStatus']
                    newTime = newDev.states[u'timeLeftSeconds']

                    LOG.debug(u'received "%s" state change %s %s --> %s %s'
                              % (oldDev.name, oldStatus, oldTime, newStatus,
                                 newTime))

                    if oldStatus == u'active' and newStatus == u'inactive':

                        # Timer has expired.

                        if priorDoorStatus == u'opening':
                            if openSensor:
                                self._updateDoorStates(dev, u'stopped')
                            else:
                                self._updateDoorStates(dev, u'open')
                        elif priorDoorStatus == u'closing':
                            if closedSensor:
                                self._updateDoorStates(dev, u'reversing')
                            else:
                                self._updateDoorStates(dev, u'closed')

                elif devType == u'closedSensor':
                    oldState = self._getNormalizedState(devType, oldDev, dev)
                    newState = self._getNormalizedState(devType, newDev, dev)

                    # onOffState == 0 <--> door not closed.
                    # onOffState == 1 <--> door fully closed.

                    LOG.debug(u'received "%s" state change %s --> %s'
                              % (oldDev.name, oldState, newState))

                    if oldState < newState:  # not closed --> fully closed.
                        self._updateDoorStates(dev, u'closed')
                        pluginAction(travelTimer, u'stopTimer')
                    elif oldState > newState:  # fully closed --> not closed.
                        self._updateDoorStates(dev, u'opening')
                        pluginAction(travelTimer, u'restartTimer')

                elif devType == u'openSensor':
                    oldState = self._getNormalizedState(devType, oldDev, dev)
                    newState = self._getNormalizedState(devType, newDev, dev)

                    # onOffState == 0 <--> door not open.
                    # onOffState == 1 <--> door fully open.

                    LOG.debug(u'received "%s" state change %s --> %s'
                              % (oldDev.name, oldState, newState))

                    if oldState < newState:  # Not open --> fully open.
                        if priorDoorStatus == u'closing':
                            self._updateDoorStates(dev, u'reversing')
                        self._updateDoorStates(dev, u'open')
                        pluginAction(travelTimer, u'stopTimer')
                    elif oldState > newState:  # Fully open --> not open.
                        self._updateDoorStates(dev, u'closing')
                        pluginAction(travelTimer, u'startTimer')

                elif devType == u'actuatorRelay':
                    oldState = int(oldDev.states[u'onOffState'])
                    newState = int(newDev.states[u'onOffState'])

                    # onOffState == 0 <--> actuatorRelay is open.
                    # onOffState == 1 <--> actuatorRelay is closed.

                    # The actuatorRelay is assumed to be momentary; it closes
                    # to start the actuator and then opens in a second or less
                    # to prepare for the next actuation.  The following code
                    # ignores the closing event (oldState > newState) and uses
                    # the opening event (oldState < newState) as an indicator
                    # of opener actuation.

                    LOG.debug(u'received "%s" state change %s --> %s'
                              % (oldDev.name, oldState, newState))

                    if oldState < newState:  # ActuatorRelay opened.
                        if priorDoorStatus == u'closed':
                            if not closedSensor:  # Ignore if closedSensor.
                                self._updateDoorStates(dev, u'opening')
                                pluginAction(travelTimer, u'restartTimer')
                        else:  # Assume that door is open.
                            if not openSensor:  # Ignore if openSensor.
                                self._updateDoorStates(dev, u'closing')
                                pluginAction(travelTimer, u'restartTimer')

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

        LOG.debug(unicode(valuesDict))
        for item in valuesDict:
            if valuesDict[item] == u'None':
                valuesDict[item] = None
        errors = indigo.Dict()
        self.devices[devId] = {}

        # Validate open/close travel time entry.

        travelTime = valuesDict[u'travelTime']
        if not (travelTime.isdigit() and 20 >= int(travelTime) >= 8):
            error = (u'Open/close travel time must be an integer between 8 '
                     u'and 20')
            errors[u'travelTime'] = error

        # Validate closedSensor entry, if any.

        closedSensor = valuesDict.get(u'closedSensor')
        if closedSensor:
            closedSensorDev = indigo.devices[closedSensor]
            for devId in self.devices:
                if closedSensorDev.id in self.devices[devId]:
                    error = u'Closed sensor already in use; choose another'
                    errors[u'closedSensor'] = error
                    break

        # Validate openSensor entry, if any.

        openSensor = valuesDict.get(u'openSensor')
        if openSensor:
            error = u'Open sensor already in use; choose another'
            if openSensor == closedSensor:
                errors[u'openSensor'] = error
            else:
                openSensorDev = indigo.devices[openSensor]
                for devId in self.devices:
                    if openSensorDev.id in self.devices[devId]:
                        errors[u'openSensor'] = error
                        break

        # Validate actuatorRelay entry, if any.

        actuatorRelay = valuesDict.get(u'actuatorRelay')
        if actuatorRelay:
            relayDev = indigo.devices[actuatorRelay]
            for devId in self.devices:
                if relayDev.id in self.devices[devId]:
                    error = u'Actuator relay already in use; choose another'
                    errors[u'travelTimer'] = error
                    break

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
    def getSensorDeviceList(filter="", valuesDict=None, typeId="", targetId=0):
        LOG.threaddebug(u'Plugin.getSSensorDeviceList called')
        sensors = []
        for dev in indigo.devices:
            if dev.deviceTypeId in (u'alarmZone',
                                    u'digitalInput',
                                    u'zwOnOffSensorType'):
                sensors.append(dev.name)
        return [u'None'] + sorted(sensors)

    @staticmethod
    def getRelayDeviceList(filter="", valuesDict=None, typeId="", targetId=0):
        LOG.threaddebug(u'Plugin.getRelayDeviceList called')
        relays = []
        for dev in indigo.devices:
            if dev.deviceTypeId == u'digitalOutput':
                relays.append(dev.name)
        return [u'None'] + sorted(relays)

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
    def closeGarageDoor(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug(u'Plugin.closeGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            if dev.states[u'doorStatus.open']:
                indigo.device.turnOn(actuatorRelay)
        else:
            error = u'close garage door ignored; no actuator relay specified.'
            LOG.error(error)

    @staticmethod
    def openGarageDoor(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug(u'Plugin.openGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            if dev.states[u'doorStatus.closed']:
                indigo.device.turnOn(actuatorRelay)
        else:
            error = u'open garage door ignored; no actuator relay specified.'
            LOG.error(error)

    @staticmethod
    def toggleGarageDoor(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug(u'Plugin.toggleGarageDoor called "%s"', dev.name)
        actuatorRelay = dev.pluginProps.get(u'actuatorRelay')
        if actuatorRelay:
            indigo.device.turnOn(actuatorRelay)
        else:
            error = u'toggle garage door ignored; no actuator relay specified.'
            LOG.error(error)
