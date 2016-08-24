#
# IPsec overlay network manager (l3overlay)
# l3overlay/tests/tests/__init__.py - unit test constants, base class and helper functions
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


import ipaddress
import os
import string
import tempfile
import unittest

from l3overlay import util


MY_DIR   = util.path_my_dir()
ROOT_DIR = os.path.join(MY_DIR, "..", "..")
SRC_DIR  = os.path.join(ROOT_DIR, "src")

LOG_DIR = os.path.join(ROOT_DIR, ".tests")


class L3overlayTest(unittest.TestCase):
    '''
    Unit test base class.
    '''

    name = "test_l3overlay"


    #
    ##
    #


    def setUp(self):
        '''
        Set up the unit test runtime state.
        '''

        self.tmp_dir = tempfile.mkdtemp(prefix="l3overlay-%s-" % self.name)

        self.conf_dir = os.path.join(MY_DIR, self.name)
        self.log_dir = os.path.join(LOG_DIR, os.path.basename(self.tmp_dir))

        self.global_conf = {
            "dry_run": "true",

            "log_level": "DEBUG",

            "use_ipsec": "true",
            "ipsec_manage": "true",

            "lib_dir": os.path.join(self.tmp_dir, "lib"),

            "overlay_conf_dir": os.path.join(self.conf_dir, "overlays"),
            "template_dir": os.path.join(ROOT_DIR, "l3overlay", "templates"),


            "log": os.path.join(self.log_dir, "l3overlay.log"),
            "pid": os.path.join(self.tmp_dir, "l3overlayd.pid"),
        }


    def tearDown(self):
        '''
        Tear down the unit test runtime state.
        '''

        util.directory_remove(self.tmp_dir)


    #
    ##
    #


    def assert_success(self, section, key, value):
        '''
        Assertion abstract method for success.
        Process:
        * Take in an argument dictionary
        * Create an object
        * Run assertions
        * Return the object
        '''

        raise NotImplementedError()


    def assert_fail(self, section, key, value, *exceptions):
        '''
        Assertion abstract method for failure.
        Process:
        * Take in an argument dictionary and a
          list of exceptions that could be thrown
        * Create an object
        * Run assertions
        '''

        raise NotImplementedError()


    #
    ##
    #

    def assert_value(self, section, key, value, test_default=False):
        '''
        Test that key is properly handled by the object.
        '''

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assert_success(section, key, value)

        # Test value.
        self.assert_success(section, key, value)


    def assert_boolean(self, section, key, test_default=False):
        '''
        Test that key, of type boolean, is properly handled by the object.
        '''

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assert_success(section, key, value)

        # Test valid values.
        self.assert_success(section, key, True)
        self.assert_success(section, key, "true")
        self.assert_success(section, key, 1)
        self.assert_success(section, key, 2)

        self.assert_success(section, key, False)
        self.assert_success(section, key, "false")
        self.assert_success(section, key, 0)
        self.assert_success(section, key, -1)

        # Test invalid values.
        self.assert_fail(section, key, "", util.GetError)
        self.assert_fail(section, key, util.random_string(6), util.GetError)


    def assert_integer(self, section, key, minval=None, maxval=None, test_default=False):
        '''
        Test that key, of type integer, is properly handled by the object.
        '''

        vvs = string.digits

        _minval = minval if minval is not None else 0
        _maxval = maxval if maxval is not None else max(_minval + 1, 11)

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assert_success(section, key, value)

        # Test valid values.
        self.assert_success(section, key, _minval)
        self.assert_success(section, key, _maxval)

        self.assert_success(section, key, str(_minval))

        # Test invalid values.
        self.assert_fail(section, key, "", util.GetError)
        self.assert_fail(section, key, "foo", util.GetError)

        if minval is not None:
            self.assert_fail(section, key, _minval - 1, util.GetError)

        if maxval is not None:
            self.assert_fail(section, key, _maxval + 1, util.GetError)


    def assert_name(self, section, key, valid_value=None, invalid_exception=None, test_default=False):
        '''
        Test that key, of type name, is properly handled by the object.
        '''

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assert_success(section, key, value)

        # Test valid values.
        if valid_value:
            self.assert_success(section, key, valid_value)
            self.assert_success(section, key, " %s" % valid_value)
            self.assert_success(section, key, "%s " % valid_value)
        else:
            self.assert_success(section, key, "name")
            self.assert_success(section, key, "name_1")
            self.assert_success(section, key, "name-2")
            self.assert_success(section, key, "name.3")
            self.assert_success(section, key, " name-4")
            self.assert_success(section, key, "name-5 ")

        # Test invalid values.
        self.assert_fail(section, key, "", util.GetError)
        self.assert_fail(section, key, 1, util.GetError)
        self.assert_fail(section, key, "name 6", util.GetError)

        if invalid_exception:
            self.assert_fail(
                section,
                key,
                util.random_string(4),
                invalid_exception,
            )


    def assert_hex_string(self, section, key, min=None, max=None, test_default=False):
        '''
        Test that key, of type hex string, is properly handled by the object.
        Optionally checks if digit limits are properly handled, by specifying
        a miniumum and maximum digit size.
        '''

        vvs = string.hexdigits

        _min = min if min is not None else 1
        _max = max if max is not None else max(_min + 1, 16)

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assert_success(section, key, value)

        # Test valid values.
        for v in vvs:
            self.assert_success(section, key, str.join("", [v for __ in range(0, _min)]))

        self.assert_success(
            section,
            key,
            str.join("", [vvs[i % len(vvs)] for i in range(0, _max)]),
        )

        # Test invalid values.
        self.assert_fail(section, key, "", util.GetError)

        self.assert_fail(
            section,
            key,
            str.join("", ["z" for __ in range(0, _min)]),
            util.GetError,
        )

        if min is not None and _min > 1:
            self.assert_fail(
                section,
                key,
                str.join("", [vvs[i % len(vvs)] for i in range(0, _min - 1)]),
                util.GetError,
            )

        if max is not None and _max > 1:
            self.assert_fail(
                section,
                key,
                str.join("", [vvs[i % len(vvs)] for i in range(0, _max + 1)]),
                util.GetError,
            )


    def assert_ip_network(self, section, key, test_default=False):
        '''
        Test that key, of type 'ip network', is properly handled by the object.
        '''

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assert_success(section, key, value)

        # Test valid values.
        self.assert_success(section, key, 3325256704)
        self.assert_success(section, key, "198.51.100.0/24")
        self.assert_success(section, key, ipaddress.ip_network("198.51.100.0/24"))

        self.assert_success(section, key, 42540766411282592856903984951653826560)
        self.assert_success(section, key, "2001:db8::/32")
        self.assert_success(section, key, ipaddress.ip_network("2001:db8::/32"))

        # Test invalid values.
        self.assert_fail(section, key, "", util.GetError)
        self.assert_fail(section, key, -1, util.GetError)
        self.assert_fail(section, key, util.random_string(32), util.GetError)


    def assert_enum(self, section, key, enum, test_default=False):
        '''
        Test that key, of type enum, is properly handled by the object.
        '''

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assert_success(section, key, value)

        # Test valid values.
        for e in enum:
            self.assert_success(section, key, e.upper())
            self.assert_success(section, key, e.lower())

        # Test invalid values.
        self.assert_fail(section, key, "", util.GetError)
        self.assert_fail(section, key, util.random_string(16), util.GetError)
        self.assert_fail(section, key, 1, util.GetError)


    def assert_path(self, section, key, valid_path=None, test_default=False):
        '''
        Test that key, of type path, is properly handled by the object.
        '''

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]
            self.assertTrue(os.path.isabs(value))
            self.assert_success(section, key, value)

        # Test valid values.
        if valid_path:
            self.assert_success(section, key, valid_path)
        else:
            self.assert_success(section, key, os.path.join(self.tmp_dir, "assert_path"))

        # Test invalid values.
        self.assert_fail(section, key, "", util.GetError)
        self.assert_fail(section, key, util.random_string(16), util.GetError)
        self.assert_fail(section, key, 1, util.GetError)


    def assert_path_iterable(self, section, key, valid_paths=None, test_default=False):
        '''
        Test that key, of type path, is properly handled by the object.
        '''

        # Test default value, if specified.
        if test_default:
            obj = self.assert_success(section, key, None)
            value = vars(obj)[section][key] if section else vars(obj)[key]

            for f in value:
                self.assertTrue(os.path.isabs(f))

            self.assert_success(section, key, value)

        # Test valid values.
        if valid_paths:
            self.assert_success(section, key, valid_paths)
        else:
            self.assert_success(section, key, os.path.join(self.tmp_dir, "assert_path_iterable"))

        # Test invalid values.
        self.assert_fail(section, key, [""], util.GetError)
        self.assert_fail(section, key, [util.random_string(16)], util.GetError)
        self.assert_fail(section, key, [1], util.GetError)


def main():
    '''
    Unit test main routine.
    '''

    unittest.main()
