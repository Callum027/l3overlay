#
# IPsec overlay network manager (l3overlay)
# tests/base/__init__.py - unit test base class
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


class BaseTest(object):
    class Class(unittest.TestCase):
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
                "dry_run": True,
                "no_dry_run": True,

                "log_level": "DEBUG",

                "use_ipsec": True,
                "no_use_ipsec": True,

                "ipsec_manage": True,
                "no_ipsec_manage": True,

                "lib_dir": os.path.join(self.tmp_dir, "lib"),

                "overlay_conf_dir": os.path.join(self.conf_dir, "overlays"),
                "fwbuilder_script_dir": None,
                "template_dir": os.path.join(ROOT_DIR, "templates"),

                "ipsec_conf": None,
                "ipsec_secrets": None,

                "log": os.path.join(self.log_dir, "l3overlay.log"),
                "pid": os.path.join(self.tmp_dir, "l3overlayd.pid"),

                "overlay_conf": [],
            }


        def tearDown(self):
            '''
            Tear down the unit test runtime state.
            '''

            util.directory_remove(self.tmp_dir)


        #
        ##
        #


        def object_get(self, *args, conf=None):
            '''
            '''

            raise NotImplementedError()


        def value_get(self, *args):
            '''
            Get the value from the given section and key on the object.
            '''

            raise NotImplementedError()


        def assert_success(self, *args, conf=None, value=None,
                expected_key=None, expected_value=None):
            '''
            -> section, key, value, expected_value, expected_key
            Assertion abstract method for success.
            Process:
            * Modify object config based on the given
              section, key and value:
                - if value is not None, modify existing
                  value or add it to the object config
                - if value is None, remove from the
                  object config if it is there
            * Create an object
            * Run assertions to check for:
                - successful object creation
                - object's output value matches either the
                  input value, or the given expected value/key
            '''

            raise NotImplementedError()


        def assert_fail(self, *args, conf=None, value=None, exception=None, exceptions=[]):
            '''
            -> section, key, value, *exceptions
            Assertion abstract method for failure.
            Process:
            * Modify object config based on the given
              section, key and value:
                - if value is not None, modify existing
                  value or add it to the object config
                - if value is None, remove from the
                  object config if it is there
            * Create an object
            * Raise a failure exception if it succeeded, or
              re-raise an unexpected exception if one was thrown
            '''

            raise NotImplementedError()


        def assert_default(self, *args):
            '''
            Test that the default value works properly when reprocessed.
            The point is to test that the default value is valid input.
            '''

            raise NotImplementedError()


        #
        ##
        #


        def assert_value(self, *args, value=None):
            '''
            Test that key is properly handled by the object.
            '''

            self.assert_success(*args, value=value)


        def assert_boolean(self, *args):
            '''
            Test that key, of type boolean, is properly handled by the object.
            '''

            # Test valid values.
            self.assert_success(*args, value=True, expected_value=True)
            self.assert_success(*args, value="true", expected_value=True)
            self.assert_success(*args, value=1, expected_value=True)
            self.assert_success(*args, value=2, expected_value=True)

            self.assert_success(*args, value=False, expected_value=False)
            self.assert_success(*args, value="false", expected_value=False)
            self.assert_success(*args, value=0, expected_value=False)
            self.assert_success(*args, value=-1, expected_value=False)

            # Test invalid values.
            self.assert_fail(*args, value="", exception=util.GetError)
            self.assert_fail(*args, value=util.random_string(6), exception=util.GetError)


        def assert_integer(self, *args, minval=None, maxval=None, test_default=False):
            '''
            Test that key, of type integer, is properly handled by the object.
            '''

            vvs = string.digits

            _minval = minval if minval is not None else -1
            _maxval = maxval if maxval is not None else max(_minval + 1, 11)

            # Test valid values.
            self.assert_success(*args, value=_minval, expected_value=_minval)
            self.assert_success(*args, value=_maxval, expected_value=_maxval)

            self.assert_success(*args, value=str(_minval), expected_value=_minval)

            # Test invalid values.
            self.assert_fail(*args, value="", util.GetError)
            self.assert_fail(*args, value="foo", util.GetError)

            if minval is not None:
                self.assert_fail(*args, value=_minval - 1, exception=util.GetError)

            if maxval is not None:
                self.assert_fail(*args, value=_maxval + 1, exception=util.GetError)


        def assert_name(self, *args, test_default=False):
            '''
            Test that key, of type name, is properly handled by the object.
            '''

            # Test valid values.
            self.assert_success(*args, value="name", expected_value="name")
            self.assert_success(*args, value="name_1", expected_value="name_1")
            self.assert_success(*args, value="name-2", expected_value="name-2")
            self.assert_success(*args, value="name.3", expected_value="name.3")
            self.assert_success(*args, value=" name-4", expected_value="name-4")
            self.assert_success(*args, value="name-5 ", expected_value="name-5")

            # Test invalid values.
            self.assert_fail(*args, value="", exception=util.GetError)
            self.assert_fail(*args, value=1, exception=util.GetError)
            self.assert_fail(*args, value="name 6", exception=util.GetError)


        def assert_hex_string(self, *args, min=None, max=None, test_default=False):
            '''
            Test that key, of type hex string, is properly handled by the object.
            Optionally checks if digit limits are properly handled, by specifying
            a miniumum and maximum digit size.
            '''

            vvs = string.hexdigits

            _min = min if min is not None else 1
            _max = max if max is not None else max(_min + 1, 16)

            # Test valid values.
            for v in vvs:
                hex_string = str.join("", [v for __ in range(0, _min)])
                self.assert_success(*args, value=hex_string, expected_value="0x%s" % hex_string)

            hex_string = str.join("", [vvs[i % len(vvs)] for i in range(0, _max)])
            self.assert_success(*args, value=hex_string, expected_value="0x%s" % hex_string)

            hex_string = "0x%s" % hex_string
            self.assert_success(*args, value=hex_string, expected_value=hex_string)

            # Test invalid values.
            self.assert_fail(*args, value="", exception=util.GetError)

            self.assert_fail(
                *args,
                value=str.join("", ["z" for __ in range(0, _min)]),
                exception=util.GetError,
            )

            if min is not None and _min > 1:
                self.assert_fail(
                    *args,
                    value=str.join("", [vvs[i % len(vvs)] for i in range(0, _min - 1)]),
                    exception=util.GetError,
                )

            if max is not None and _max > 1:
                self.assert_fail(
                    *args,
                    value=str.join("", [vvs[i % len(vvs)] for i in range(0, _max + 1)]),
                    exception=util.GetError,
                )


        def assert_ip_network(self, *args):
            '''
            Test that key, of type 'ip network', is properly handled by the object.
            '''

            # Test valid values.
            self.assert_success(
                *args,
                value=3325256704,
                expected_value=ipaddress.ip_network(3325256704),
            )
            self.assert_success(
                *args,
                value="198.51.100.0/24",
                expected_value=ipaddress.ip_network("198.51.100.0/24"),
            )
            self.assert_success(
                *args,
                value=ipaddress.ip_network("198.51.100.0/24"),
                expected_value=ipaddress.ip_network("198.51.100.0/24"),
            )

            self.assert_success(
                *args,
                value=42540766411282592856903984951653826560,
                expected_value=ipaddress.ip_network(42540766411282592856903984951653826560),
            )
            self.assert_success(
                *args,
                value="2001:db8::/32",
                expected_value=ipaddress.ip_network("2001:db8::/32"),
            )
            self.assert_success(
                *args,
                value=ipaddress.ip_network("2001:db8::/32"),
                expected_value=ipaddress.ip_network("2001:db8::/32"),
            )

            # Test invalid values.
            self.assert_fail(*args, value="", exception=util.GetError)
            self.assert_fail(*args, value=-1, exception=util.GetError)
            self.assert_fail(*args, value=util.random_string(32), exception=util.GetError)
            self.assert_fail(*args, value=ipaddress.ip_address("192.0.2.1"), exception=util.GetError)
            self.assert_fail(*args, value=ipaddress.ip_address("2001:db8::1"), exception=util.GetError)


        def assert_ip_address(self, *args):
            '''
            Test that key, of type 'ip address', is properly handled by the object.
            '''

            # Test valid values.
            self.assert_success(
                *args,
                value=3221225985,
                expected_value=ipaddress.ip_address(3221225985),
            )
            self.assert_success(
                *args,
                value="192.0.2.1",
                expected_value=ipaddress.ip_address("192.0.2.1"),
            )
            self.assert_success(
                *args,
                value=ipaddress.ip_address("192.0.2.1"),
                expected_value=ipaddress.ip_address("192.0.2.1"),
            )

            self.assert_success(
                *args,
                value=42540766411282592856903984951653826561,
                expected_value=ipaddress.ip_address(42540766411282592856903984951653826561),
            )
            self.assert_success(
                *args,
                value="2001:db8::1",
                expected_value=ipaddress.ip_address("2001:db8::1"),
            )
            self.assert_success(
                *args,
                value=ipaddress.ip_address("2001:db8::1"),
                expected_value=ipaddress.ip_address("2001:db8::1"),
            )

            # Test invalid values.
            self.assert_fail(*args, value="", exception=util.GetError)
            self.assert_fail(*args, value=-1, exception=util.GetError)
            self.assert_fail(*args, value=util.random_string(32), exception=util.GetError)
            self.assert_fail(*args, value=ipaddress.ip_network("198.51.100.0/24"), exception=util.GetError)
            self.assert_fail(*args, value=ipaddress.ip_network("2001:db8::/32"), exception=util.GetError)


        def assert_netmask(self, *args, is_ipv6=False):
            '''
            Test that key, of type 'netmask', is properly handled by the object.
            '''

            # Test valid values.
            self.assert_success(*args, value="8", expected_value=8)
            self.assert_success(*args, value=8, expected_value=8)
            self.assert_success(*args, value="16", expected_value=16)
            self.assert_success(*args, value=16, expected_value=16)
            self.assert_success(*args, value="24", expected_value=24)
            self.assert_success(*args, value=24, expected_value=24)
            self.assert_success(*args, value="32", expected_value=32)
            self.assert_success(*args, value=32, expected_value=32)

            if is_ipv6:
                self.assert_success(*args, value="64", expected_value=64)
                self.assert_success(*args, value=64, expected_value=64)
                self.assert_success(*args, value="128", expected_value=128)
                self.assert_success(*args, value=128, expected_value=128)
            else:
                self.assert_success(*args, value="255.0.0.0", expected_value=8)
                self.assert_success(*args, value="255.255.0.0", expected_value=16)
                self.assert_success(*args, value="255.255.255.0", expected_value=24)
                self.assert_success(*args, value="255.255.255.255", expected_value=32)

            # Test invalid values.
            self.assert_fail(*args, value=-1, exception=util.GetError)
            self.assert_fail(*args, value="", exception=util.GetError)

            if is_ipv6:
                self.assert_fail(*args, value="255.255.255.255", exception=util.GetError)
                self.assert_fail(*args, value="129", exception=util.GetError)
                self.assert_fail(*args, value=129, exception=util.GetError)
            else:
                self.assert_fail(*args, value="300.400.500.600", exception=util.GetError)
                self.assert_fail(*args, value="33", exception=util.GetError)
                self.assert_fail(*args, value=33, exception=util.GetError)
                self.assert_fail(*args, value="128", exception=util.GetError)
                self.assert_fail(*args, value=128, exception=util.GetError)


        def assert_enum(self, *args, enum=None):
            '''
            Test that key, of type enum, is properly handled by the object.
            '''

            # Test valid values.
            for e in enum:
                self.assert_success(*args, value=e.upper(), expected_value=e)
                self.assert_success(*args, value=e.lower(), expected_value=e)

            # Test invalid values.
            self.assert_fail(*args, value="", exception=util.GetError)
            self.assert_fail(*args, value=util.random_string(16), exception=util.GetError)
            self.assert_fail(*args, value=1, exception=util.GetError)


        def assert_path(self, *args, assert_absolute=True, assert_relative=True):
            '''
            Test that key, of type path, is properly handled by the object.
            '''

            # Test valid values.
            if absolute:
                path = os.path.join(self.tmp_dir, "assert_path.txt")
                self.assert_success(section, key, path, expected_value=path)

            if relative:
                self.assert_success(section, key, "../assert_path.txt")

            # Test invalid values.
            if not absolute:
                self.assert_fail(
                    section,
                    key,
                    os.path.join(self.tmp_dir, "assert_path.txt"),
                    util.GetError,
                )

            if not relative:
                self.assert_fail(
                    section,
                    key,
                    os.path.join("..", "assert_path.txt"),
                    util.GetError,
                )

            self.assert_fail(section, key, "", util.GetError)
            self.assert_fail(section, key, 1, util.GetError)