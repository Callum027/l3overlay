#
# IPsec overlay network manager (l3overlay)
# l3overlay/overlay/interface/base.py - static interface abstract base class
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

from l3overlay import util

from l3overlay.util.exception import L3overlayError


class ReadError(L3overlayError):
    pass

class WriteError(L3overlayError):
    pass


class Interface(metaclass=abc.ABCMeta):
    '''
    Abstract base class for an overlay static interface.
    '''

    def __init__(self, logger, name=None):
        '''
        Set internal fields for the static interface to use.
        '''

        self.logger = logger
        self.name = name


    def setup(self, daemon, overlay):
        '''
        Set static interface runtime state.
        '''

        self.daemon = daemon
        self.dry_run = self.daemon.dry_run
        self.root_ipdb = self.daemon.root_ipdb

        self.overlay = overlay
        self.netns = self.overlay.netns


    @abc.abstractmethod
    def is_ipv6(self):
        '''
        Returns True if this static interface has an IPv6 address
        assigned to it.
        '''

        raise NotImplementedError()


    @abc.abstractmethod
    def start(self):
        '''
        Required method to start a static interface.
        '''

        return


    @abc.abstractmethod
    def stop(self):
        '''
        Required method to stop a static interface.
        '''

        return


    def remove(self):
        '''
        Optional method to clean up a static interface runtime state.
        '''

        return
