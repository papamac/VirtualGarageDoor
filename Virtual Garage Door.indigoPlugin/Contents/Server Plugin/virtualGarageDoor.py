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
                    transition from LOCKED to OPENING.  Enforce state
                    transition rules by including only allowed transitions in
                    the table.
v1.3.2   7/12/2024  Set the door state image to a green lock if the door is in
                    the LOCKED state.
v1.3.3   7/17/2024  Set the priorDoorState when updating door states.
v1.3.4   8/18/2024  (1) Eliminate the LOCKED state from the door state
                    enumeration and the _DOOR_STATE_TRANSITIONS
                    tuple/dictionary.
                    (2) Remove code to update the priorDoorState in the
                    _updateOpenerStatesOnServer method,
                    (3) Use the lock device state in the update method to warn
                    the user about state transitions while the door is LOCKED.
v1.3.5   8/24/2024  Fix a message formatting bug in the update method.
v1.3.6    9/4/2024  Update comments and wiki figures/tables.
v1.3.7   9/13/2024  Update comments and wiki figures/tables.
v1.4.0  11/28/2024  (1) Recover gracefully from missing lock devices and
                    timer devices.
                    (2) Return the new door state to the plugin for valid state
                    changes.
v1.5.0    8/4/2025  (1) Replace the opener device STOPPED and REVERSING states
                    with a new OBSTRUCTED state.
                    (2) Change the nomenclature for the VGD lock device to the
                    virtual lock device.  Change lock references from lk,
                    lkDevId, and lkDev to vl, vlDevId, and vlDev.
                    (3) Change the update method to optionally call a unique
                    transition method after processing each event.
                    (4) Add common transition functions to perform needed
                    actions for stationary/moving states, normal/anomalous
                    locking, and the lock after closing option.
                    (5) Add a new door status of 'closed-lk' to indicate a
                    CLOSED door state when the linked virtual lock device is
                    LOCKED.  Use the upper case version ot this status,
                    'CLOSED-LK', to represent a pseudo state that is used
                    internally in VGD, but is not passed to HKLS as the door
                    state.
                    (6) Index the DOOR_STATE_TRANSITIONS data structure using
                    door status instead of the door state.  This allows
                    transitions to the new CLOSED-LK pseudo state.  Change the
                    updateDoorStatesOnServer to set the states based on the
                    value of the door status instead of the door state.
                    (7) Optionally log door state changes and door state tracks
                    based on new checkbox fields in the opener device ConfigUI.
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
    instance methods that model door state transitions as the door moves
    through its operational cycle.  It documents the transitions in the form of
    virtual door state tracks and updates all door states in real time on the
    Indigo server.  It has four primary instance methods as follows:

    __init__(self, plugin, dev, doorStatus)
        Initializes instance attributes including the door state track.  Sets
        the initial door states on the Indigo server using the doorStatus
        argument.  It is called by the Plugin deviceStartComm method for each
        new instance (one for each opener device).

    _updateOpenerStatesOnServer(self, dev, doorStatus)
        Updates the door state, the door status, the on/off state, and the
        state image on the Indigo server.

    _timerAction(self, action)
        Executes the requested action for the travel timer associated with the
        opener device.

    update(self, event)
        Updates the door states and the door state track in response to a new
        event.  It is called by the Plugin deviceUpdated method.  update
        implements a state machine model of the garage door using the
        DOOR_STATE_TRANSITIONS class data structure that includes a new door
        status and transition functions for each transition.

    The VirtualGarageDoor class is segmented into three major parts for
    readability:

    I   CLASS CONSTANTS,
    II  INITIALIZATION AND SUPPORT METHODS,
    III UPDATE METHOD
    """

    ###########################################################################
    #                                                                         #
    #                         CLASS VirtualGarageDoor                         #
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

    # Door states, door status, and door status transitions:

    # The opener device door state is an integer state variable with values
    # defined by the following enumeration:

    OPEN, CLOSED, OPENING, CLOSING, OBSTRUCTED = range(5)

    # The door state is used by the HomiKitLink Siri plugin (HKLS) as the
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
    # CLOSED position and sometimes reloading the VGD plugin.

    # The opener device door status is a lower case text state variable with
    # values of 'open', 'closed', 'opening', 'closing', 'obstructed', and
    # 'closed-lk'.  It is used as the uiValue for the State in the device list
    # of the Indigo home window.  It is also used to key the
    # DOOR_STATE_TRANSITIONS data structure (see below) and to provide the
    # door state in logged messages.

    # The first five door status values correspond to the five door states.
    # A sixth 'closed-lk' status indicates that the door state is CLOSED and
    # the state of the linked virtual lock device (if any) is LOCKED.  The
    # DOOR_STATES dictionary gives the integer door state keyed by the text
    # door status.  Note thet both the 'closed' and 'closed-lk' status values
    # have the same door state (CLOSED).

    DOOR_STATES = {'open':       OPEN,
                   'closed':     CLOSED,
                   'opening':    OPENING,
                   'closing':    CLOSING,
                   'obstructed': OBSTRUCTED,
                   'closed-lk':  CLOSED}

    # The DOOR_STATE_TRANSITIONS data structure is a compound dictionary/tuple
    # used by the update method to implement the state machine model of the
    # garage door.  It is keyed by a current door status and an event that
    # defines an allowed transition to a new door status.  Its value is a tuple
    # containing the new door status and an embedded tuple of transition
    # function names.  Transition functions are defined and called in the
    # update method.  Usage is as follows:

    # newDoorStatus = DOOR_STATE_TRANSITIONS[doorStatus][event][0]
    # transitionFunctions = DOOR_STATE_TRANSITIONS[doorStatus][event][1]
    # for transitionFunction in transitionFunctions:
    #     locals()[transitionFunction]()

    # The transition entries in the DOOR_STATE_TRANSITIONS data structure
    # define the door state tracking logic for the plugin (see the Design wiki,
    # Section 3.4.1).  Door status and event combinations that are not included
    # in the data structure are rejected.  Text comments indicate the use case
    # for each transition.

    DOOR_STATE_TRANSITIONS = {

        'open':  # Transitions from the 'open' door status (door state is OPEN):

            {'ar-on':          ('closing',    ('_start',)),                       # normal closing
             'os-off':         ('closing',    ('_start',)),                       # normal closing
             'vs-on':          ('closing',    ('_start',)),                       # normal closing
             'cs-on':          ('closed',     ('_log', '_stop')),                 # out-of-sync recovery
             'ls-off':         ('obstructed', ('_warn_ls',)),                     # anomalous disconnect
             'ps-off':         ('obstructed', ('_warn_ps',)),                     # anomalous power off
             'ml-on':          ('obstructed', ('_unlock_ml',)),                   # anomalous locking
             'ls-on':          ('open',       ()),                                # tracking only
             'ps-on':          ('open',       ()),                                # tracking only
             'ml-off':         ('open',       ())},                               # tracking only

        'closed':  # Transitions from the 'closed' door status (door state is CLOSED):

            {'ar-on':          ('opening',    ('_start',)),                       # normal opening
             'cs-off':         ('opening',    ('_start',)),                       # normal opening
             'vs-on':          ('opening',    ('_start',)),                       # normal opening
             'os-on':          ('open',       ('_log', '_stop')),                 # out-of-sync recovery
             'vl-on':          ('closed-lk',  ('_log',)),                         # normal locking
             'ls-off':         ('closed',     ('_lock',)),                        # normal locking
             'ps-off':         ('closed',     ('_lock',)),                        # normal locking
             'ml-on':          ('closed',     ('_lock',)),                        # normal locking
             'ls-on':          ('closed',     ()),                                # tracking only
             'ps-on':          ('closed',     ()),                                # tracking only
             'ml-off':         ('closed',     ())},                               # tracking only

        'opening':  # Transitions from the 'opening' door status (door state is OPENING):

            {'os-on':          ('open',       ('_log', '_stop')),                 # normal open
             'tt-exp&os-none': ('open',       ('_log', '_stop')),                 # normal open if no os
             'ar-on':          ('obstructed', ('_log', '_stop', '_rev')),         # interrupted opening
             'tt-exp':         ('obstructed', ('_log', '_stop', '_rev')),         # interrupted opening
             'cs-off':         ('opening',    ()),                                # redundant event
             'vs-on':          ('opening',    ()),                                # redundant event
             'cs-on':          ('closed',     ('_log', '_stop')),                 # out-of-sync recovery
             'ls-off':         ('obstructed', ('_warn_ls',)),                     # anomalous disconnect
             'ps-off':         ('obstructed', ('_warn_ps',)),                     # anomalous power off
             'ml-on':          ('obstructed', ('_unlock_ml',)),                   # anomalous locking
             'ls-on':          ('opening',    ()),                                # tracking only
             'ps-on':          ('opening',    ()),                                # tracking only
             'ml-off':         ('opening',    ())},                               # tracking only

        'closing':  # Transitions from the 'closing' door status (door state is CLOSING):

            {'cs-on':          ('closed',     ('_log', '_stop', '_lock_ac')),     # normal closed
             'tt-exp&cs-none': ('closed',     ('_log', '_stop', '_lock_ac')),     # normal closed if no cs
             'ar-on':          ('obstructed', ('_start', '_rev')),                # interrupted closing
             'tt-exp':         ('obstructed', ('_start', '_rev')),                # interrupted closing
             'os-off':         ('closing',    ()),                                # redundant event
             'vs-on':          ('closing',    ()),                                # redundant event
             'os-on':          ('open',       ('_log', '_stop',)),                # out-of-sync recovery
             'ls-off':         ('obstructed', ('_warn_ls',)),                     # anomalous disconnect
             'ps-off':         ('obstructed', ('_warn_ps',)),                     # anomalous power off
             'ml-on':          ('obstructed', ('_unlock_ml',)),                   # anomalous locking
             'ls-on':          ('closing',    ()),                                # tracking only
             'ps-on':          ('closing',    ()),                                # tracking only
             'ml-off':         ('closing',    ())},                               # tracking only

    'obstructed':  # Transitions from the 'obstructed' door status (door state is OBSTRUCTED):

            {'ar-on':          ('closing',    ('_start',)),                       # recovery activation
             'vs-on':          ('closing',    ('_start',)),                       # recovery activation
             'cs-on':          ('closed',     ('_log', '_stop', '_lock_ac')),     # obstruction cleared
             'tt-exp&cs-none': ('closed',     ('_log', '_stop', '_lock_ac')),     # obstruction cleared if no cs
             'os-on':          ('open',       ('_log', '_stop',)),                # obstruction cleared
             'tt-exp&os-none': ('open',       ('_log', '_stop')),                 # obstruction cleared if no os
             'cs-off':         ('obstructed', ()),                                # redundant event
             'os-off':         ('obstructed', ()),                                # redundant event
             'ls-off':         ('obstructed', ('_warn_ls',)),                     # anomalous disconnect
             'ps-off':         ('obstructed', ('_warn_ps',)),                     # anomalous power off
             'ml-on':          ('obstructed', ('_unlock_ml',)),                   # anomalous locking
             'ls-on':          ('obstructed', ()),                                # tracking only
             'ps-on':          ('obstructed', ()),                                # tracking only
             'ml-off':         ('obstructed', ())},                               # tracking only

        'closed-lk':  # Transitions from the 'closed-lk' door status (door state is CLOSED):

            {'vl-off':         ('closed',    ('_log',)),                         # normal unlocking
             'ls-off':         ('closed-lk', ()),                                # redundant event
             'ps-off':         ('closed-lk', ()),                                # redundant event
             'ml-on':          ('closed-lk', ()),                                # redundant event
             'ls-on':          ('closed-lk', ()),                                # tracking only
             'ps-on':          ('closed-lk', ()),                                # tracking only
             'ml-off':         ('closed-lk', ())}}                               # tracking only

    # Monitored device events that can't affect the door state.

    IGNORED_EVENTS = ('ar-off', 'vs-off', 'tt-on', 'tt-off')

    # Timer constants:

    TIMER_PLUGIN_ID = 'com.perceptiveautomation.indigoplugin.timersandpesters'
    TIMER = indigo.server.getPlugin(TIMER_PLUGIN_ID)

    ###########################################################################
    #                                                                         #
    #                         CLASS VirtualGarageDoor                         #
    #                                   PART                                  #
    #                                                                         #
    #                                III   III                                #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                III   III                                #
    #                                                                         #
    #                   INITIALIZATION AND SUPPORT METHODS                    #
    #                                                                         #
    #  def __init__(self, plugin, dev, doorStatus)                            #
    #  def _updateOpenerStatesOnServer(self, doorStatus)                      #
    #  def _timerAction(self, action)                                         #
    #                                                                         #
    ###########################################################################

    def __init__(self, dev, startupDoorStatus):
        """
        Initialize local instance attributes including the starting door state
        track.  Set the initial door states on the Indigo server.

        The door state track is a time sequence of transitions as the door
        moves through its operational cycle. Each transition is a string of the
        form:

        ' -> timeSinceLastEvent event -> newDoorStatus',

        and tracks look like:

        'initialStatus -> timeSinceLastEvent event1 -> newDoorStatus1 -> timeSinceEvent1 event2 -> newDoorStatus2...'
        """

        # Initialize local instance attributes.

        self._dev = dev
        self._openerDirection = 0  # 0 --> opening, 1 --> closing.
        self._priorEvent = None
        self._priorEventTime = datetime.now()

        # Set the startup opener states and initialize the door state track.

        self._updateOpenerStatesOnServer(startupDoorStatus)
        self._doorStateTrack = startupDoorStatus.upper()

    def _updateOpenerStatesOnServer(self, newDoorStatus):
        """
        Update and optionally log the opener device states on the Indigo server
        if they have changed.  The states include the doorState, the doorStatus
        and the onOffState.  The doorState and doorStatus values are defined in
        the class constants of Part I.  The onOffState is on if the door state
        is CLOSED and off otherwise.

        Also, set the state image on the Indigo Home window based on the value
        of the newDoorStatus.  Select a green dot if the newDoorStatus is
        'closed', a green lock if the newDoorStatus is 'closed-lk', and a red
        dot otherwise.
        """

        # Proceed only if the newDoorStatus has changed from the current door
        # status.

        doorStatus = self._dev.states['doorStatus']
        if newDoorStatus == doorStatus: return

        # Compute, update, and optionally log the new opener states.

        doorState = self.DOOR_STATES[newDoorStatus]
        self._dev.updateStateOnServer('doorState', doorState)

        self._dev.updateStateOnServer('doorStatus', newDoorStatus)

        onOffState = doorState is self.CLOSED
        self._dev.updateStateOnServer('onOffState', onOffState,
                                      uiValue=newDoorStatus)
        if self._dev.pluginProps['logDoorStateChanges']:
            L.info('"%s" update to %s',self._dev.name, newDoorStatus.upper())

        # Select and update the state image.

        if newDoorStatus == 'closed':  # The door is CLOSED, but not LOCKED.
            image = indigo.kStateImageSel.SensorOn  # Select a green dot.
        elif newDoorStatus == 'closed-lk':  # The door is CLOSED and LOCKED.
            image = indigo.kStateImageSel.Locked  # Select a green lock.
        else:  # The door is not CLOSED and not LOCKED.
            image = indigo.kStateImageSel.SensorTripped  # Select a red dot.
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

    ###########################################################################
    #                                                                         #
    #                         CLASS VirtualGarageDoor                         #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III   III                             #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                             III   III   III                             #
    #                                                                         #
    #                              UPDATE METHOD                              #
    #                                                                         #
    #  def update(self, event)                                                #
    #                                                                         #
    ###########################################################################

    def update(self, event):
        """
        Update the door states and the door state track in response to the
        event provided in the argument.

        Check for a valid event and add event qualifiers for travel timer
        events that are dependent on the door status.  Look up the new door
        status in the DOOR_STATE_TRANSITIONS dictionary and update the door
        states on the Indigo server. Update the door state track with a new
        transition including the time since the last event, the event, and the
        new door status.  Perform transition functions as specified in the
        DOOR_STATE_TRANSITIONS dictionary.
        """

        # The transition functions for use in the DOOR_STATE_TRANSITIONS data
        # structure are defined below.  All functions include the same
        # threaddebug log statement.

        def _lock():
            """
            The door status is 'closed' and a ls-off, ps-off or ml-on event
            occurred to intentionally lock it.  Execute a plugin action to lock
            the virtual lock.
            """
            L.threaddebug('_lock called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            vlDevId = self._dev.pluginProps['vlDevId']
            indigo.device.lock(int(vlDevId))

        def _lock_ac():
            """
            The door was CLOSED.  Check to see if the lock after closing option
            was requested.  If so, call the _lock function to lock the virtual
            lock.
            """
            L.threaddebug('_lock_ac called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            if self._dev.pluginProps.get('lockAfterClosing'):  # lac requested.
                _lock()

        def _log():
            """
            Log the current door state track if requested and start a new track
            beginning with the new door status.
            """
            L.threaddebug('_log called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            if self._dev.pluginProps['logDoorStateTracks']:
                L.info('"%s" %s', self._dev.name, self._doorStateTrack)
            self._doorStateTrack = newDoorStatus.upper()

        def _rev():
            """ The door was obstructed.  Reverse the opener direction. """
            L.threaddebug('_rev called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            self._openerDirection ^= 1  # Reverse the opener direction.

        def _start():
            """
            The door is moving.  Set the opener direction using the new door
            status and restart the travel timer.
            """
            L.threaddebug('_start called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            if newDoorStatus == 'opening': self._openerDirection = 0
            elif newDoorStatus == 'closing': self._openerDirection = 1

            self._timerAction('restartTimer')

        def _stop():
            """
            The door has reached a stationary state.  Stop the travel timer.
            Also, reset the vibration sensor if present.
            """
            L.threaddebug('_stop called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            self._timerAction('stopTimer')

            vsDevId = self._dev.pluginProps['vsDevId']
            if vsDevId:  # Vibration sensor is present.
                vsResetDelay = int(round(float(
                    self._dev.pluginProps['vsResetDelay'])))
                indigo.device.turnOff(int(vsDevId), delay=vsResetDelay)

        def _unlock_ml():
            """
            The door is not CLOSED and an anomalous ml-on event occurred
            putting it in the OBSTRUCTED state.  Immediately unlock the
            mechanical lock and log a warning message to inform the user and
            provide direction to close the door.
            """
            L.threaddebug('_unlock_ml called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            mlDevId = self._dev.pluginProps['mlDevId']
            indigo.device.turnOff(int(mlDevId))
            L.warning('"%s" the mechanical lock was LOCKED when the door was '
                      '%s and was then automatically UNLOCKED; manually '
                      'activate the door to close it.',
                      self._dev.name, doorStatus.upper())

        def _warn_ls():
            """
            The door is not CLOSED and an anomalous ls-off event occurred
            putting it in the OBSTRUCTED state.  Log a warning message to
            inform the user and provide direction to close the door.
            """
            L.threaddebug('_warn_ls called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            L.warning('"%s" the latch was disconnected when the door was %s; '
                      'move the door manually if needed and reconnect the '
                      'latch.', self._dev.name, doorStatus.upper())

        def _warn_ps():
            """
            The door is not CLOSED and an anomalous ps-off event occurred
            putting it in the OBSTRUCTED state.  Log a warning message to
            inform the user and provide direction to close the door.
            """
            L.threaddebug('_warn_ps called "%s" %s%s',
                          self._dev.name, doorStatus.upper(), transition)

            L.warning('"%s" the power switch was turned off when the door was '
                      '%s; turn on the switch and manually activate the door '
                      'to close it.', self._dev.name, doorStatus.upper())

        # Ignore events that can't affect the door state.

        if event in self.IGNORED_EVENTS: return

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
        # meanings based on the opener direction.

        if event == 'tt-exp':
            if not self._openerDirection:  # Direction is opening.
                osDevId = self._dev.pluginProps['osDevId']
                event += '&os-none' if not osDevId else ''
            else:  # Direction is closing.
                csDevId = self._dev.pluginProps['csDevId']
                event += '&cs-none' if not csDevId else ''

        # Get the new door state from the DOOR_STATE_TRANSITIONS dictionary as
        # a function of the current door status and the event.

        doorStatus = self._dev.states['doorStatus']

        try:
            newDoorStatus = self.DOOR_STATE_TRANSITIONS[doorStatus][event][0]

        except KeyError:  # Event is not in the dictionary for the door status.
            L.warning('"%s" event %s is not in the dictionary for the door '
                      'state %s; event ignored',
                      self._dev.name, event, doorStatus.upper())
            return

        # Valid new door status.  Update door states on server if the
        # door status has changed.

        self._updateOpenerStatesOnServer(newDoorStatus)

        # Format a transition string in the form of
        # -> timeSinceLastEvent event -> newDoorStatus and append it to the
        # door state track.

        if timeSinceLastEvent >= 60.0:
            timeText = '%im' % int(round(timeSinceLastEvent / 60.0))
        else:
            timeText = '%.2fs' % timeSinceLastEvent
        transition = ' -> %s %s -> %s' % (timeText, event,
                                          newDoorStatus.upper())
        self._doorStateTrack += transition

        # Execute transition functions.

        transitionFunctions = self.DOOR_STATE_TRANSITIONS[doorStatus][event][1]
        for transitionFunction in transitionFunctions:
            locals()[transitionFunction]()

