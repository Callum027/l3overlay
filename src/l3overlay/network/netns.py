#
# IPsec overlay network manager (l3overlay)
# l3overlay/network/netns.py - network namespace functions
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


import pyroute2
import subprocess

import pyroute2.netns

import pyroute2.netns.process.proxy

from l3overlay import util

from l3overlay.network import interface

from l3overlay.util.exception import L3overlayError

from l3overlay.util.worker import Worker
from l3overlay.util.worker import NotYetStartedError


class UnableToCreateNetnsError(L3overlayError):
    def __init__(self, netns, message):
        super().__init("unable to create network namespace '%s': %s" % (netns.name, message))


class NetNS(Worker):
    '''
    Wrapper around pyroute2 network interface, to provide
    convenient functions.
    '''

    def __init__(self, dry_run, logger, name):
        '''
        Set up network namespace internal fields.
        '''

        super().__init__(use_remove=True)

        self.dry_run = dry_run

        self.logger = logger
        self.name = name
        self.description = "network namespace '%s'" % self.name

        self.netns = None
        self.ipdb = None


    def start(self):
        '''
        Start the network namespace object, and create the network
        namespace if it doesn't exist.
        '''

        self.set_starting()

        self.logger.debug("starting network namespace '%s'" % self.name)

        if not self.dry_run:
            if self.name not in pyroute2.netns.listnetns():
                try:
                    pyroute2.netns.create(self.name)
                except FileExistsError:
                    # Network namespace already exists
                    pass
                except e:
                    raise UnableToCreateNetnsError(self, e.message)

            self.netns = pyroute2.NetNS(self.name)
            self.ipdb = pyroute2.IPDB(nl=self.netns)

        self.set_started()


    def stop(self):
        '''
        Stop the network namespace object.
        '''

        self.set_stopping()

        self.logger.debug("stopping network namespace '%s'" % self.name)

        if not self.dry_run:
            self.ipdb.release()
            self.netns.close()

        self.set_stopped()


    def remove(self):
        '''
        Remove a network namespace from the system.
        '''

        self.set_removing()

        self.logger.debug("removing network namespace '%s'" % self.name)

        if not self.dry_run:
            pyroute2.netns.remove(self.name)

        self.set_removed()


    def interface_get(self, name):
        '''
        Get an interface of the given name from this namespace.
        '''

        return interface.get(self.dry_run, self.logger, name, netns=self)


    def Popen(self, *args, **kwargs):
        '''
        Start a process in this network namespace using the Popen interface.
        '''

        if not self.is_started():
            raise NotYetStartedError(self)

        if self.dry_run:
            # Create a dummy NSPopen object with a
            # stub release() method, to be API compatible
            # with the real deal.
            class NSPopen(subprocess.Popen):
                def release(self):
                    pass

            return NSPopen(
                [util.command_path("true")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            return pyroute2.netns.process.proxy.NSPopen(self.name, *args, **kwargs)

Worker.register(NetNS)


def get(dry_run, logger, name):
    '''
    Get the network namespace runtime state for the given name, creating it
    if it doesn't exist.
    '''

    return NetNS(dry_run, logger, name)
