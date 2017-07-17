#
# IPsec overlay network manager (l3overlay)
# tests/test_daemon.py - unit test for reading Daemon objects
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


import l3overlay
import os
import unittest

from l3overlay import util

import l3overlay.daemon

from tests.base import BaseTest


class DaemonTest(BaseTest.Class):
    '''
    l3overlay unit test for reading Daemon objects.
    '''

    name = "test_daemon"


    #
    ##
    #


    def object_get(*args, conf=None):
        '''
        '''

        key = args[0] if args else None
        value = args[1] if len(args) > 1 else None

        gc = global_conf.copy()

        if value:
            gc[key] = value

        return l3overlay.daemon.read(gc)


    def value_get(self, *args):
        '''
        Get the value from the given section and key on the daemon.
        '''

        daemon = args[0]
        key = args[1]
        value = args[2]

        return vars(daemon)[section][key] if section else vars(daemon)[key]


    def assert_success(self, *args, conf=self.global_conf, value=None,
                expected_key=None, expected_value=None):
        '''
        Try and read an l3overlay daemon, using using the given arguments.
        Assumes it will succeed, and will run an assertion test to make
        sure a Daemon is returned.
        '''

        key = args[0]

        daemon = self.object_get(key, value, conf=conf)
        self.assertIsInstance(daemon, l3overlay.daemon.Daemon)

        if expected_value is not None:
            self.assertEqual(expected_value, vars(daemon)[expected_key if expected_key else key])

        return daemon


    def assert_fail(self, *args, value=None, exception=None, exceptions=[]):
        '''
        Try and read an l3overlay daemon using the given arguments.
        Assumes it will fail, and raises a RuntimeError if it doesn't.
        '''

        key = args[0]

        try:
            self.daemon_get(key, value)
            raise RuntimeError('''l3overlay.daemon.read unexpectedly returned successfully
Expected exception types: %s
Arguments: %s''' % (str.join(", ", (e.__name__ for e in exceptions)), gc))

        except exceptions:
            pass


    def assert_default(self, *args):
        '''
        Create an l3overlay daemon object, using the default global
        config, in order to test that the specified key contains a
        default value that can be successfully processed as if it
        was a specified one.
        Optionally, also test if it matches a specified expected value.        
        '''

        key = args[0]
        expected_value = args[1] if len(args) > 1 else None

        daemon = self.daemon_get()
        actual_value = vars(daemon)[key]

        if expected_value:
            self.assertEqual(actual_value, expected_value)

        # Feed the default value as an explicit value into the creation
        # of an object, to make sure it can be processed correctly.
        self.assert_success(key, actual_value)

    #
    ##
    #

    def assert_boolean(self, *args):
        '''
        Test that key, of type boolean, is properly handled by the object.
        '''

        key = args[0]
        no_key = "no_%s" % key

        default = self.global_conf.pop(key)
        no_default = self.global_conf.pop(no_key)

        # Test default value, if specified.
        if test_default:
            gc = self.global_conf.copy()
            gc[key] = False
            gc[no_key] = True

            obj = self.object_get(*args)
            obj = self.assert_success(key, value=False)
            value = self.value_get(obj, section, key)
            self.assert_success(section, key, value, expected_value=value)
            self.global_conf[key] = default
            self.global_conf[no_key] = no_default

        # Test valid values.
        gc = self.global_conf.copy()
        gc.pop(key)
        gc[no_key] = True
        self.assert_success(key, True, conf=gc, expected_value=True)
        self.assert_success(key, "true", conf=gc, expected_value=True)
        self.assert_success(key, 1, conf=gc, expected_value=True)
        self.assert_success(key, 2, conf=gc, expected_value=True)

        gc = self.global_conf.copy()
        gc[key] = False
        gc.pop(no_key)
        self.assert_success(no_key, False, expected_key=key, expected_value=False)
        self.assert_success(no_key, "false", expected_key=key, expected_value=False)
        self.assert_success(no_key, 0, expected_key=key, expected_value=False)
        self.assert_success(no_key, -1, expected_key=key, expected_value=False)

        # Test invalid values.
        self.assert_fail(key, "", util.GetError)
        self.assert_fail(key, util.random_string(6), util.GetError)


    #
    ##
    #


    def test_log_level(self):
        '''
        Test that 'log_level' is properly handled by the daemon.
        '''

        self.assert_enum(
            None,
            "log_level",
            ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            test_default = True,
        )


    def test_use_ipsec(self):
        '''
        Test that 'use_ipsec' is properly handled by the daemon.
        '''

        self.assert_boolean(None, "use_ipsec", test_default=True)


    def test_ipsec_manage(self):
        '''
        Test that 'ipsec_manage' is properly handled by the daemon.
        '''

        self.assert_boolean(None, "ipsec_manage", test_default=True)


    def test_ipsec_psk(self):
        '''
        Test that 'ipsec_psk' is properly handled by the daemon.
        '''

        self.assert_hex_string(None, "ipsec_psk", min=6, max=64)


    def test_lib_dir(self):
        '''
        Test that 'lib_dir' is properly handled by the daemon.
        '''

        self.assert_path(None, "lib_dir", test_default=True)


    def test_fwbuilder_script_dir(self):
        '''
        Test that 'fwbuilder_script_dir' is properly handled by the daemon.
        '''

        self.assert_path(None, "fwbuilder_script_dir")


    def test_overlay_conf_dir(self):
        '''
        Test that 'overlay_conf_dir' is properly handled by the daemon.
        '''

        self.assert_path(None, "overlay_conf_dir", test_default=True)


    def test_template_dir(self):
        '''
        Test that 'template_dir' is properly handled by the daemon.
        '''

        self.assert_path(None, "template_dir", test_default=True)


    def test_pid(self):
        '''
        Test that 'pid' is properly handled by the daemon.
        '''

        self.assert_path(None, "pid", test_default=True)


    def test_ipsec_conf(self):
        '''
        Test that 'ipsec_conf' is properly handled by the daemon.
        '''

        self.assert_path(None, "ipsec_conf", test_default=True)


    def test_ipsec_secrets(self):
        '''
        Test that 'ipsec_secrets' is properly handled by the daemon.
        '''

        self.assert_path(None, "ipsec_secrets", test_default=True)


    def test_overlay_conf(self):
        '''
        Test that 'overlay_conf' is properly handled by the daemon.
        '''

        overlay_conf_dir = self.global_conf["overlay_conf_dir"]
        self.global_conf["overlay_conf_dir"] = None

        # Test absolute paths.
        self.assert_success(
            None,
            "overlay_conf",
            [os.path.join(overlay_conf_dir, f) for f in os.listdir(overlay_conf_dir)],
        )

        # Test relative paths.
        self.assert_success(
            None,
            "overlay_conf",
            [os.path.relpath(os.path.join(overlay_conf_dir, f)) for f in os.listdir(overlay_conf_dir)],
        )

        # Test non-existent paths.
        self.assert_fail(None, "overlay_conf", [util.random_string(16)], FileNotFoundError)

        # Test invalid values.
        self.assert_fail(None, "overlay_conf", "", util.GetError)
        self.assert_fail(None, "overlay_conf", 1, l3overlay.daemon.ReadError)
        self.assert_fail(None, "overlay_conf", [""], util.GetError)
        self.assert_fail(None, "overlay_conf", [1], util.GetError)


if __name__ == "__main__":
    unittest.main()
