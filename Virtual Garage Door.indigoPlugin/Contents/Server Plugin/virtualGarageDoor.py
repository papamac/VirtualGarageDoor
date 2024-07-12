# coding=utf-8
###############################################################################
#                                                                             #
#                     Virtual Garage Door Indigo Plugin                       #
#                        MODULE virtualGarageDoor.py                          #
#                                                                             #
###############################################################################
"""
  BUNDLE:  Monitoring and control of conventional garage door openers in Indigo
           (Virtual Garage Door.indigoPlugin)
  MODULE:  virtualGarageDoor.py
   TITLE:  Virtual state transition modeling and tracking
FUNCTION:  Receives and checks monitored device events from plugin.py.
           Uses the events to update door states and tracks.
   USAGE:  virtualGarageDoor.py is included in a standard Indigo plugin bundle.
  AUTHOR:  papamac
 VERSION:  1.3.1
    DATE:  June 21, 2024


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
action groups, control pages, triggers, and other plugins. The VGD plugin also
provides actions to open, close and toggle the garage door.

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

The plugin will work only with conventional garage door openers that auto-
reverses during an obstructed closing cycle.  It will not accurately track door
state transitions in this cycle for a non-auto-reversing door.

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
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '1.3.1'
__date__ = 'June 21, 2024'

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
    time on the Indigo Server.  It has three methods as follows:

    __init__                   Initializes instance attributes including the
                               door state and door state track.  It is called
                               by the Plugin deviceStartComm method for each
                               new instance (one for each Indigo door device).
    _updateDoorStatesOnServer  Updates all Indigo device states based on the
                               internal door state.  It is called by the update
                               method.
    update                     Updates the door state and door state track in
                               response to a new monitored device event.  It is
                               called by the Plugin deviceUpdated method.
    """

    # Class constants:

    # Door state enumeration, stationary state group, door status, and text
    # door states.

    # The first five door states are the same as those defined in the
    # HMCharacteristicValueDoorState enumeration in the Apple developer HomeKit website:
    # https://developer.apple.com/documentation/homekit/hmcharacteristicvaluedoorstate

    OPEN, CLOSED, OPENING, CLOSING, STOPPED, REVERSING, LOCKED = range(7)
    STATIONARY_STATES = (OPEN, CLOSED, STOPPED, LOCKED)
    DOOR_STATUS = ('open', 'closed', 'opening', 'closing', 'stopped',
                   'reversing', 'locked')
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
         'os-on':      OPEN,       # 8      out-of-sync recovery
         'lk-on':      LOCKED},    # 9      normal locking

        # Transitions from the OPENING state (doorState == 2):

        {'os-on':      OPEN,       # 10     normal open
         'tt-exp&!os': OPEN,       # 11     normal open if no os
         'ar-on':      STOPPED,    # 12     interrupted opening
         'tt-exp':     STOPPED,    # 13     interrupted opening
         'cs-off':     OPENING,    # 14     redundant event
         'vs-on':      OPENING,    # 15     redundant event
         'cs-on':      CLOSED},    # 16     out-of-sync recovery

        # Transitions from the CLOSING state (doorState == 3):

        {'cs-on':      CLOSED,     # 17     normal closed
         'tt-exp&!cs': CLOSED,     # 18     normal closed if no cs
         'tt-exp':     REVERSING,  # 19     interrupted closing
         'os-off':     CLOSING,    # 20     redundant event
         'vs-on':      CLOSING,    # 21     redundant event
         'os-on':      OPEN},      # 22     out-of-sync recovery

        # Transitions from the STOPPED state (doorState == 4):

        {'ar-on':     CLOSING,     # 23     normal closing from stopped
         'vs-on':     CLOSING,     # 24     normal closing from stopped
         'cs-on':     CLOSED,      # 25     out-of-sync recovery
         'os-on':     OPEN},       # 26     out-of-sync recovery

        # Transition from the REVERSING state (doorState == 5):

        {'reverse':   OPENING},    # 27     normal opening from auto-reverse

        # Transition from the LOCKED state (doorState == 6):

        {'lk-off':    CLOSED}      # 28     normal unlocking
    )

    def __init__(self, plugin, dev, mDevStates):
        """
        Initialize local instance attributes including the door state and the
        door state track.  The door state is an integer as defined in the class
        constants.  The (virtual) door state track is a time sequence of
        transitions from state to state as the door moves through its
        operational cycle. Each transition is a string of the form:

        [timeSinceLastEvent event newDoorState], and tracks look like:

        initialState [transition 1] [transition2]...
        """
        self._plugin = plugin
        self._dev = dev
        self._priorEvent = None
        self._priorEventTime = datetime.now()

        # Initialize the opener device state and door state track.  Assume that
        # door is not in motion and that it is closed unless the closedSensor
        # is off and openSensor is on.

        csState = mDevStates.get('cs')
        osState = mDevStates.get('os')
        self._doorState = self.OPEN if not csState and osState else self.CLOSED
        self._doorStateTrack = self.DOOR_STATES[self._doorState]
        self._updateDoorStatesOnServer()

    def _updateDoorStatesOnServer(self):
        """
        Update the door states on the Indigo server for use by the Home window,
        scripts, action groups, control pages, triggers, and other plugins.

        The door states include the doorState, doorStatus and the onOffState.
        The doorState can be OPEN, CLOSED, OPENING, CLOSING, STOPPED, and
        REVERSING (see enumeration in the class constants).  The doorStatus is
        a lower case string representation of the doorState, and the onOffState
        is on if the doorState is CLOSED or LOCKED and off otherwise.

        Also, set the state image on the Indigo Home window based on the value
        of the doorState.  Select a green dot if the doorState is CLOSED,
        a green lock if it is LOCKED, and a red dot otherwise.
        """
        onOffState = self._doorState in (self.CLOSED, self.LOCKED)
        doorStatus = self.DOOR_STATUS[self._doorState]
        self._dev.updateStateOnServer('onOffState', onOffState,
                                      uiValue=doorStatus)

        if self._doorState is self.CLOSED:
            image = indigo.kStateImageSel.SensorOn
        elif self._doorState is self.LOCKED:
            image = indigo.kStateImageSel.Locked
        else:
            image = indigo.kStateImageSel.SensorTripped
        self._dev.updateStateImageOnServer(image)

        self._dev.updateStateOnServer('doorStatus', doorStatus)
        self._dev.updateStateOnServer('doorState', self._doorState)

        L.info('"%s" update to %s',
               self._dev.name, self.DOOR_STATES[self._doorState])

    def update(self, event):
        """
        Update the door state and the door track in response to the monitored
        device event provided in the event argument.

        Check for a valid monitored device event and add event qualifiers for
        travel timer events that are dependent on the door state.  Look up the
        new door state in the DOOR_STATE_TRANSITIONS dictionary.  Update the
        door state track with the transition including the time since the last
        event, the event, and the new door state. Update the door states on the
        Indigo server.

        If the new door state is REVERSING, force a second transition to
        OPENING to reflect the auto-reversing behavior of the door.  Update the
        door state track and the door states on the Indigo Server.

        Perform new state processing functions.  If the new door state is a
        stationary state (CLOSED, OPEN, or STOPPED), log the door state track,
        stop the travel timer, and reset the vibration sensor (if present).  If
        the new door state os moving (OPENING or CLOSING), restart the travel
        timer.
        """

        # Ignore events that can't affect the door state.

        if event in ('ar-off', 'vs-off', 'tt-on', 'tt-off'):
            return

        # Compute the time since the last event.

        eventTime = datetime.now()
        dt = eventTime - self._priorEventTime
        timeSinceLastEvent = dt.total_seconds()
        self._priorEventTime = eventTime

        # Check for a duplicate event within a 1 second interval.

        if event == self._priorEvent and timeSinceLastEvent < 1.0:
            L.warning('"%s" duplicate event %s reported within 1 second',
                      self._dev.name, event)
            return
        self._priorEvent = event

        # Add qualifiers for travel timer expired events that have different
        # meanings during OPENING and CLOSING.

        if event == 'tt-exp':
            if self._doorState is self.OPENING:
                os = self._dev.pluginProps.get('os')
                event += '&!os' if not os else ''
            elif self._doorState is self.CLOSING:
                cs = self._dev.pluginProps.get('cs')
                event += '&!cs' if not cs else ''
            L.debug('"%s" %s', self._dev.name, event)

        # Get the new door state from the DOOR_STATE_TRANSITIONS dictionary as
        # a function of the current door state and the monitored device event.

        try:
            newDoorState = self.DOOR_STATE_TRANSITIONS[self._doorState][event]
        except KeyError:  # Ignore event if no legal transition.
            if self._doorState == self.LOCKED:
                message = ('"%s" %s event detected while the door is %s; '
                           'return the door to the CLOSED state before '
                           'unlocking')
            else:
                message = ('"%s" event %s is inconsistent with door state %s; '
                           'transition ignored')
            L.warning(message, self._dev.name, event,
                      self.DOOR_STATES[self._doorState])
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

        # Update the door states if there has been a state change.

        if newDoorState == self._doorState:  # No change.
            return
        self._doorState = newDoorState
        self._updateDoorStatesOnServer()

        # Perform new state actions.

        ttDevId = int(self._dev.pluginProps['ttDevId'])
        if self._doorState in self.STATIONARY_STATES:

            # Log the existing door state track if requested,
            # initialize a new door state track, stop the timer,
            # and reset the vibration sensor if present.

            if self._plugin.pluginPrefs.get('logDoorStateTracks'):
                L.info('"%s" config: %s| track: %s',
                       self._dev.name, self._dev.pluginProps['mDevConfig'],
                       self._doorStateTrack)

            self._doorStateTrack = self.DOOR_STATES[self._doorState]

            self._plugin.TIMER.executeAction('stopTimer', deviceId=ttDevId)

            vsDevIdStr = self._dev.pluginProps['vsDevId']
            if vsDevIdStr:  # Vibration sensor is active.
                vsDevId = int(vsDevIdStr)
                vsResetDelay = int(round(float(
                    self._dev.pluginProps['vsResetDelay'])))
                indigo.device.turnOff(vsDevId, delay=vsResetDelay)

        else:  # Door is moving; restart the timer.
            self._plugin.TIMER.executeAction('restartTimer', deviceId=ttDevId)

        # If the door state is REVERSING, immediately declare a reverse event
        # and perform a recursive update to force a new transition.

        if self._doorState is self.REVERSING:
            self.update('reverse')
