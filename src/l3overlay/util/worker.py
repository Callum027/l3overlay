#
# IPsec overlay network manager (l3overlay)
# l3overlay/util/worker.py - worker abstract base class
#
# Copyright (c) 2016 Catalyst.net Ltd
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import abc


STATES = ("starting", "started", "stopping", "stopped", "removing", "removed")


class Worker(metaclass=abc.ABCMeta):
    '''
    Abstract base class for classes which use a 'start-stop' service
    operation style. Implements the internal fields and helper methods
    for this.
    '''

    def __init__(self):
        '''
        Set up worker internal fields.
        '''

        self._setup = False
        self._state = "stopped"


    def _assert_state(self):
        '''
        Check that the worker state is valid.
        '''

        if not isinstance(self._setup, bool):
            raise RuntimeError("invalid setup state '%s', expected True/False" % self._setup)

        if self._state not in STATES:
            raise RuntimeError("invalid worker state '%s', expected one of %s" % (self._state, STATES))


    def is_setup(self):
        '''
        Check if the worker has had 'setup()' called yet.
        '''

        self._assert_state()
        return self._setup


    def set_setup(self):
        '''
        Set the worker to be set up.
        '''

        self._setup = True


    def is_starting(self):
        '''
        Check if the worker is in the 'starting' state.
        '''

        self._assert_state()
        return self._state == "starting"


    def set_starting(self):
        '''
        Set the worker to 'starting' state.
        '''

        self._assert_state()
        self._state = "starting"


    def is_started(self):
        '''
        Check if the worker is in the 'started' state.
        '''

        self._assert_state()
        return self._state == "started"


    def set_started(self):
        '''
        Set the worker to 'started' state.
        '''

        self._assert_state()
        self._state = "started"


    def is_running(self):
        '''
        Check if the worker is in the 'started' state. Alias to is_started().
        '''

        return self.is_started()


    def set_running(self):
        '''
        Set the worker to 'started' state. Alias to set_started().
        '''

        self.set_started()


    def is_stopping(self):
        '''
        Check if the worker is in the 'stopping' state.
        '''

        self._assert_state()
        return self._state == "stopping"


    def set_stopping(self):
        '''
        Set the worker to 'stopping' state.
        '''

        self._assert_state()
        self._state = "stopping"


    def is_stopped(self):
        '''
        Check if the worker is in the 'stopped' state.
        '''

        self._assert_state()
        return self._state == "stopped"


    def set_stopped(self):
        '''
        Set the worker to 'stopped' state.
        '''

        self._assert_state()
        self._state = "stopped"


    def is_removing(self):
        '''
        Check if the worker is in the 'removing' state.
        '''

        self._assert_state()
        return self._state == "removing"


    def set_removing(self):
        '''
        Set the worker to 'removing' state.
        '''

        self._assert_state()
        self._state = "removing"


    def is_removed(self):
        '''
        Check if the worker is in the 'removed' state.
        '''

        self._assert_state()
        return self._state == "removed"


    def set_removed(self):
        '''
        Set the worker to 'removed' state.
        '''

        self._assert_state()
        self._state = "removed"


    def setup(self):
        '''
        Set up worker runtime state.
        '''

        pass


    @abc.abstractmethod
    def start(self):
        '''
        Start the worker.
        '''

        pass


    @abc.abstractmethod
    def stop(self):
        '''
        Stop the worker.
        '''

        pass


    def remove(self):
        '''
        Remove the worker runtime state. Optional abstract method.
        '''

        pass

