#
# IPsec overlay network manager (l3overlay)
# tests/l3overlayd/overlay/static_interface/test_static_tuntap.py - unit test for static tuntaps
#
# Copyright (c) 2017 Catalyst.net Ltd
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


'''
Unit tests for reading static tuntap interfaces.
'''


import os

from tests.l3overlayd.overlay.static_interface import StaticInterfaceBaseTest


class StaticTuntapTest(StaticInterfaceBaseTest):
    '''
    Unit test for reading static tuntap interfaces.
    '''

    name = "test_static_tuntap"
    conf_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), name)


    #
    ##
    #


    def setUp(self):
        '''
        Set up the unit test runtime state.
        '''

        super().setUp()

        self.overlay_conf[self.section] = {
            "mode": "tun",
            "address": "201.0.113.1",
            "netmask": "32",
        }


    #
    ##
    #


    def test_mode(self):
        '''
        Test that 'mode' is properly handled by the static tuntap interface.
        '''

        self.assert_enum(self.section, "mode", enum=["tun", "tap"])


    def test_address_netmask(self):
        '''
        Test that 'address' and 'netmask' are properly handled by the static tuntap interface.
        '''

        self.assert_address_netmask(self.section, "address", "netmask")


    def test_uid(self):
        '''
        Test that 'uid' is properly handled by the static tuntap interface.
        '''

        self.assert_integer(self.section, "uid", minval=0)


    def test_gid(self):
        '''
        Test that 'gid' is properly handled by the static tuntap interface.
        '''

        self.assert_integer(self.section, "gid", minval=0)
