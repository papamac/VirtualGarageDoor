# coding=utf-8
"""
###############################################################################
#                                                                             #
#                     Virtual Garage Door Indigo Plugin                       #
#                        MODULE virtualGarageDoor.py                          #
#                                                                             #
###############################################################################

  BUNDLE:  Monitoring and control of conventional garage door openers in Indigo
           (Virtual Garage Door.indigoPlugin)
  MODULE:  virtualGarageDoor.py
   TITLE:  Virtual state transition modeling and tracking
FUNCTION:  Receives and checks monitored device events from plugin.py.
           Uses the events to update door states and tracks.
   USAGE:  virtualGarageDoor.py is included in a standard Indigo plugin bundle.
  AUTHOR:  papamac
 VERSION:  1.4.0
    DATE:  December 3, 2024


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
virtualGarageDoor.py encapsulates detailed door behavior in the
VirtualGarageDoor class, and plugin.py, encapsulates the Indigo device behavior
in the Plugin class.  A VirtualGarageDoor instance is created for each VGD
device defined by plugin.py.  The plugin bundle also includes several xml
files that define Indigo GUIs and actions.

MODULE virtualGarageDoor.py DESCRIPTION:

The virtualGarageDoor.py module defines the VirtualGarageDoor class to model
garage door behavior based on monitored device events.  See the class docstring
for details.

DEPENDENCIES/LIMITATIONS:

The VGD plugin will work only with conventional garage door openers that
automatically reverse when obstructed during a closing cycle.  It will not
accurately track door state transitions in this case for a non-auto-reversing
door.

CHANGE LOG:

v1.2.0   9/24/2023  Divide the Plugin class into two classes: Plugin which
                    encapsulates the Indigo device behavior and
                    VirtualGarageDoor which encapsulates the detailed door
                    behavior.  The VirtualGarageDoor class has instances for
                    each VGD plugin device.
v1.2.8   5/18/2024  Fix the logDoorStateTracks "key not found" error after the
                    first time initialization of the plugin.
v1.3.1   6/21/2024  (1) Add LOCKED door state as part of a larger VGD security
                    update.
                    (2) Modify the DOOR_STATE_TRANSITIONS tuple/dictionary to
                    include three new events (lk-on, lk-off, and reverse) that
                    permit the state transitions to be totally table driven.
                    The lk-on and lk-off events trigger transitions to/from the
                    locked door state and the reverse event triggers a
                    transition from REVERSING to OPENING.  Enforce state
                    transition rules by including only allowed transitions in
                    the table.
v1.3.2   7/12/2024  Set the door state image to a green lock if the door is in
                    the LOCKED state.
v1.3.3   7/17/2024  Set the priorDoorState when updating door states.
v1.3.4   8/18/2024  (1) Eliminate the LOCKED state from the door state
                    enumeration and the _DOOR_STATE_TRANSITIONS
                    tuple/dictionary.
                    (2) Remove code to update the priorDoorState in the
                    _updateDoorStatesOnServer method,
                    (3) Use the lock device state in the update method to warn
                    the user about state transitions while the door is locked.
v1.3.5   8/24/2024  Fix a message formatting bug in the update method.
v1.3.6    9/4/2024  Update comments and wiki figures/tables.
v1.3.7   9/13/2024  Update comments and wiki figures/tables.
v1.4.0  11/28/2024  (1) Recover gracefully from missing lock devices and
                    timer devices.
                    (2) Return the new door state to the plugin for valid state
                    changes.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '1.4.0'
__date__ = 'December 3, 2024'

import indigo

from datetime import datetime
from logging import getLogger

L = getLogger('Plugin')  # Standard Plugin logger.


###############################################################################
#                                                                             #
#                          CLASS VirtualGarageDoor                            #
#                                                                             #
###############################################################################

class VirtualGarageDoor:
    """
    The VirtualGarageDoor class is a collection of class data structures and
    methods that model door state transitions from one state to another as the
    door moves through its operational cycle.  It documents the transitions in
    the form of virtual door state tracks and updates the door states in real
    time on the Indigo server.  It has four methods as follows:

    __init__(self, plugin, dev, doorState)
        Initializes instance attributes including the door state track.  Sets
        the initial door states on the Indigo server using the doorState
        argument.  It is called by the Plugin deviceStartComm method for each
        new instance (one for each opener device).

    _updateDoorStatesOnServer(self, dev, doorState)
        Updates the door state, the door status, the on/off state, and the
        state image on the Indigo server.

    _timerAction(self, action)
        Executes the requested action for the travel timer associated with the
        opener device.

    update(self, event)
        Updates the door states and the door state track in response to a new
        event.  It is called by the Plugin deviceUpdated method.  It is also
        called recursively within the update method.
    """

    # Class constants:

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

    # The door state transitions table is a compound tuple/dictionary used by
    # the update method to select a new door state after the occurrence of an
    # event.  The transition entries in the table define the door state
    # tracking logic for the plugin.  Door state and event combinations that
    # are not listed in the table are rejected.  Transition numbers in the
    # comments reference the state transition diagram (Figure 5) in the wiki.
    # Text comments indicate the function of each transition.

    # newDoorState = DOOR_STATE_TRANSITIONS[doorState][event]

    DOOR_STATE_TRANSITIONS = (

        # Transitions from the OPEN state (doorState == 0):

        {'ar-on':      CLOSING,    # 1      normal closing
         'os-off':     CLOSING,    # 2      normal closing
         'vs-on':      CLOSING,    # 3      normal closing
         'cs-on':      CLOSED},    # 4      out-of-sync recovery

        # Transitions from the CLOSED state (doorState == 1):

        {'ar-on':      OPENING,    # 5      normal opening
         'cs-off':     OPENING,    # 6      normal opening
         'vs-on':      OPENING,    # 7      normal opening
         'os-on':      OPEN},      # 8      out-of-sync recovery

        # Transitions from the OPENING state (doorState == 2):

        {'os-on':      OPEN,       # 9      normal open
         'tt-exp&!os': OPEN,       # 10     normal open if no os
         'ar-on':      STOPPED,    # 11     interrupted opening
         'tt-exp':     STOPPED,    # 12     interrupted opening
         'cs-off':     OPENING,    # 12     redundant event
         'vs-on':      OPENING,    # 14     redundant event
         'cs-on':      CLOSED},    # 15     out-of-sync recovery

        # Transitions from the CLOSING state (doorState == 3):

        {'cs-on':      CLOSED,     # 16     normal closed
         'tt-exp&!cs': CLOSED,     # 17     normal closed if no cs
         'tt-exp':     REVERSING,  # 18     interrupted closing
         'os-off':     CLOSING,    # 19     redundant event
         'vs-on':      CLOSING,    # 20     redundant event
         'os-on':      OPEN},      # 21     out-of-sync recovery

        # Transitions from the STOPPED state (doorState == 4):

        {'ar-on':     CLOSING,     # 22     normal closing from stopped
         'vs-on':     CLOSING,     # 23     normal closing from stopped
         'cs-on':     CLOSED,      # 24     out-of-sync recovery
         'os-on':     OPEN},       # 25     out-of-sync recovery

        # Transition from the REVERSING state (doorState == 5):

        {'reverse':   OPENING})    # 26     normal opening from auto-reverse

    # Timer action constants:

    TIMER_PLUGIN_ID = 'com.perceptiveautomation.indigoplugin.timersandpesters'
    TIMER = indigo.server.getPlugin(TIMER_PLUGIN_ID)

    def __init__(self, plugin, dev, doorState):
        """
        Initialize local instance attributes including the starting door state
        track.  Set the initial door states on the Indigo server.

        The door state track is a time sequence of transitions from state to
        state as the door moves through its operational cycle. Each transition
        is a string of the form:

        [timeSinceLastEvent event newDoorState], and tracks look like:
        initialState [transition 1] [transition2]...
        """

        # Initialize local instance attributes.

        self._plugin = plugin
        self._dev = dev
        self._priorEvent = None
        self._priorEventTime = datetime.now()

        # Initialize the door state track and set the initial door states.

        self._doorStateTrack = self.DOOR_STATES[doorState]
        self._updateDoorStatesOnServer(doorState)

    def _updateDoorStatesOnServer(self, doorState):
        """
        Update the door states on the Indigo server for use by the Home window,
        scripts, action groups, control pages, triggers, and other plugins.

        The door states include the doorState, the doorStatus and the
        onOffState. The doorState can be OPEN, CLOSED, OPENING, CLOSING,
        STOPPED, and REVERSING (see enumeration in the class constants).  The
        doorStatus is a lower case string representation of the doorState, and
        the onOffState is on if the doorState is CLOSED and off otherwise.

        Also, set the state image on the Indigo Home window based on the value
        of the doorState.  Select a green dot if the doorState is CLOSED
        (onOffState is on) and a red dot otherwise.
        """
        L.threaddebug('_updateDoorStatesOnServer called "%s"', self._dev.name)

        # Compute and update door states.

        self._dev.updateStateOnServer('doorState', doorState)

        doorStatus = self.DOOR_STATUS[doorState]
        self._dev.updateStateOnServer('doorStatus', doorStatus)

        onOffState = doorState is self.CLOSED
        self._dev.updateStateOnServer('onOffState', onOffState,
                                      uiValue=doorStatus)
        L.info('"%s" update to %s',
               self._dev.name, self.DOOR_STATES[doorState])

        # Compute and update state image.

        image = (indigo.kStateImageSel.SensorOn if onOffState else
                 indigo.kStateImageSel.SensorTripped)
        self._dev.updateStateImageOnServer(image)

    def _timerAction(self, action):
        """
        Execute the requested timer action for the travel timer associated with
        the opener device.  Ignore the action if there is no timer available.
        """
        L.threaddebug('_timerAction called "%s"', self._dev.name)

        ttDevId = self._dev.pluginProps.get('ttDevId')
        if ttDevId:  # Timer is available.
            self.TIMER.executeAction(action, deviceId=int(ttDevId))

    def update(self, event):
        """
        Update the door states and the door track in response to the event
        provided in the argument.

        Check for a valid event and add event qualifiers for travel timer
        events that are dependent on the door state.  Look up the new door
        state in the DOOR_STATE_TRANSITIONS dictionary.  Update the door state
        track with a new transition including the time since the last event,
        the event, and the new door state. Warn the user if the new state
        transition occurred while the door was locked.  This can happen if
        monitored device sensors malfunction or if the door is manually moved
        after locking.

        If the new door state is different from the current door state, update
        the door states on the server.

        Perform new state processing functions.  If the new door state is a
        stationary state (CLOSED, OPEN, or STOPPED), log the door state track,
        stop the travel timer, and reset the vibration sensor (if present).
        Lock the door if the new door state is CLOSED and the user has
        requested that the door be locked after closing.

        If the new door state is moving (OPENING or CLOSING), restart the
        travel timer.  If the new door state is REVERSING, force a transition
        to the OPENING state using a recursive call to the update method with a
        'reverse' event.
        """

        # Ignore events that can't affect the door state.

        if event in ('ar-off', 'vs-off', 'tt-on', 'tt-off'):
            return

        # Compute the time since the last event.

        eventTime = datetime.now()
        dt = eventTime - self._priorEventTime
        timeSinceLastEvent = dt.total_seconds()
        self._priorEventTime = eventTime

        # Check for a duplicate event within a 1-second interval.

        if event == self._priorEvent and timeSinceLastEvent < 1.0:
            L.warning('"%s" duplicate event %s reported within 1 second',
                      self._dev.name, event)
            return
        self._priorEvent = event

        # Add qualifiers for travel timer expired events that have different
        # meanings during OPENING and CLOSING.

        doorState = self._dev.states['doorState']
        if event == 'tt-exp':

            if doorState is self.OPENING:
                os = self._dev.pluginProps.get('os')
                event += '&!os' if not os else ''

            elif doorState is self.CLOSING:
                cs = self._dev.pluginProps.get('cs')
                event += '&!cs' if not cs else ''

        # Get the new door state from the DOOR_STATE_TRANSITIONS dictionary as
        # a function of the current door state and the event.

        try:
            newDoorState = self.DOOR_STATE_TRANSITIONS[doorState][event]

        except KeyError:  # Event is not in the dictionary for the door state.
            L.warning('"%s" event %s is not in the dictionary for the door '
                      'state %s; event ignored', self._dev.name, event,
                      self.DOOR_STATES[doorState])
            return

        # Valid new door state.  Format a transition string in the form of
        # [time event doorState] and append it to the door state track.

        if timeSinceLastEvent >= 60.0:
            timeText = '%im' % int(round(timeSinceLastEvent / 60.0))
        else:
            timeText = '%.2fs' % timeSinceLastEvent
        transition = ' [%s %s %s]' % (timeText, event,
                                      self.DOOR_STATES[newDoorState])
        self._doorStateTrack += transition

        # Warn the user if the door was locked during the door state
        # transition.

        if self._plugin.getLockState(self._dev):  # Door was locked.
            closeIt = ' close it and' if newDoorState != self.CLOSED else ''
            L.warning('"%s" door LOCKED during transition%s;%s unlock it',
                      self._dev.name, transition, closeIt)

        # Update the door states if there has been a state change.

        if newDoorState == doorState:  # No change.
            return
        self._updateDoorStatesOnServer(newDoorState)

        # Perform new state actions.

        if newDoorState in self.STATIONARY_STATES:

            # Log the existing door state track if requested.

            if self._plugin.pluginPrefs.get('logDoorStateTracks'):
                L.info('"%s" config: %s| track: %s',
                       self._dev.name, self._dev.pluginProps['mDevConfig'],
                       self._doorStateTrack)

            # Initialize a new door state track and stop the timer.

            self._doorStateTrack = self.DOOR_STATES[newDoorState]
            self._timerAction('stopTimer')

            # Reset the vibration sensor if present.

            vsDevId = self._dev.pluginProps['vsDevId']
            if vsDevId:  # Vibration sensor is active.
                vsResetDelay = int(round(float(
                    self._dev.pluginProps['vsResetDelay'])))
                indigo.device.turnOff(int(vsDevId), delay=vsResetDelay)

            # Lock the door after closing if requested.

            if (newDoorState == self.CLOSED
                    and self._dev.pluginProps.get('lockAfterClosing')):
                class pluginAction:
                    deviceId = self._dev.id
                self._plugin.lockGarageDoor(pluginAction)

        else:  # Door is moving; restart the timer.
            self._timerAction('restartTimer')

            # If the door state is REVERSING, immediately declare a reverse
            # event and perform a recursive update to force a new transition to
            # the OPENING state.

            if newDoorState is self.REVERSING:
                self.update('reverse')
