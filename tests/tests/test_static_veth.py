#
# IPsec overlay network manager (l3overlay)
# tests/test_static_veth.py - unit test for reading static veth interfaces
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


import os
import unittest

from l3overlay import overlay
from l3overlay import util

from l3overlay.overlay.interface.base import ReadError

from tests.base.static_interface import StaticInterfaceBaseTest


class StaticVETHTest(StaticInterfaceBaseTest.Class):
    '''
    Unit test for reading static veth interfaces.
    '''

    name = "test_static_veth"

    #
    ##
    #


    def setUp(self):
        '''
        Set up the unit test runtime state.
        '''

        super().setUp()

        self.overlay_conf[self.section] = {
            "netmask": "32",
        }


    #
    ##
    #


    def test_inner_outer_address(self):
        '''
        Test that 'inner-address' and 'outer-address' at the same time are properly
        handled by the static veth interface.
        '''

        # Test that both inner-address and outer-address cannot be defined
        # at the same time, without outer-interface-bridged being set to true.
        self.overlay_conf[self.section]["inner-address"] = "201.0.113.1"
        self.assert_fail(self.section, "outer-address", "201.0.113.2", ReadError)

        self.overlay_conf[self.section]["outer-interface-bridged"] = "true"
        self.assert_success(self.section, "outer-address", "201.0.113.2")

        # Test that IPv4 and IPv6 inner and outer addresses cannot be mixed.
        self.assert_fail(self.section, "outer-address", "2001:db8::2", ReadError)


    def test_inner_address_netmask(self):
        '''
        Test that 'inner-address' and 'netmask' are properly handled by the static veth interface.
        '''

        self.assert_address_netmask(self.section, "inner-address", "netmask")


    def test_outer_address_netmask(self):
        '''
        Test that 'outer-address' and 'netmask' are properly handled by the static veth interface.
        '''

        self.assert_address_netmask(self.section, "outer-address", "netmask")


    def test_inner_namespace(self):
        '''
        Test that 'inner-namespace' is properly handled by the static veth interface.
        '''

        self.assert_name(self.section, "inner-namespace")


    def test_outer_interface_bridged(self):
        '''
        Test that 'outer-interface-bridged' is properly handled by the static veth interface.
        '''

        self.assert_boolean(self.section, "outer-interface-bridged", test_default=True)


if __name__ == "__main__":
    unittest.main()
