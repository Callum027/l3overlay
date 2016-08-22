#
# IPsec overlay network manager (l3overlay)
# l3overlay/overlay/process/firewall.py - firewall process
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

import subprocess

from l3overlay import util

from l3overlay.util.worker import Worker


class Process(Worker):

    def __init__(self, overlay):
        '''
        Set internal fields for the firewall process.
        '''

        super().__init__()

        self.name = overlay.name
        self.description = "firewall process for overlay '%s'" % self.name

        self.logger = overlay.logger
        self.fwbuilder_script = overlay.fwbuilder_script


    def start(self):
        '''
        Start the firewall process.
        '''

        self.set_starting()

        if self.fwbuilder_script:
            self.logger.debug("starting firewall")

            fwbuilder = self.netns.Popen([self.fwbuilder_script], stderr=subprocess.STDOUT)
            fwbuilder.wait()
            fwbuilder.release()

            self.logger.debug("finished starting firewall")

        self.set_started()


    def stop(self):
        '''
        Stop the firewall process.
        '''

        self.set_stopping()
        self.set_stopped()

Worker.register(Process)


def create(overlay):
    '''
    Create a firewall process.
    '''

    return Process(overlay)
