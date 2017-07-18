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


    def config_get(self, key, value, conf=None):
        '''
        '''

        gc = conf.copy() if conf else self.global_conf.copy()

        if value:
            gc[key] = value

        return gc


    def assert_success(self, *args,
                       object_key=None,
                       value=None, expected_value=None,
                       conf=None):
        '''
        Try and read an l3overlay daemon, using using the given arguments.
        Assumes it will succeed, and will run an assertion test to make
        sure a Daemon is returned.
        '''

        key = args[0]

        daemon = l3overlay.daemon.read(self.config_get(key, value, conf))
        self.assertIsInstance(daemon, l3overlay.daemon.Daemon)

        if expected_value is not None:
            self.assertEqual(
                expected_value,
                vars(daemon)[object_key if object_key else key],
            )

        return daemon


    def assert_fail(self, *args,
                    value=None,
                    exception=None, exceptions=[],
                    conf=None):
        '''
        Try and read an l3overlay daemon using the given arguments.
        Assumes it will fail, and raises a RuntimeError if it doesn't.
        '''

        key = args[0]
        excs = tuple(exceptions) if exceptions else (exception,)

        gc = self.global_config_get(key, value, conf)

        try:
            l3overlay.daemon.read(gc)
            raise RuntimeError('''l3overlay.daemon.read unexpectedly returned successfully
Expected exception types: %s
Arguments: %s''' % (str.join(", ", (e.__name__ for e in excs)), gc))

        except excs:
            pass


    def assert_default(self, *args, expected_value=None):
        '''
        Create an l3overlay daemon object, using the default global
        config, in order to test that the specified key contains a
        default value that can be successfully processed as if it
        was a specified one.
        Optionally, also test if it matches a specified expected value.        
        '''

        key = args[0]

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


    def assert_boolean(self, *args, test_default=False):
        '''
        Test that key, of type boolean, is properly handled by the object.
        '''

        key = args[0]
        no_key = "no_%s" % key

        # Test default value.
        if test_default:
            gc = self.global_conf.copy()
            gc[key] = False
            gc[no_key] = True
            self.assert_success(key, conf=gc)

        # Test valid values.
        gc = self.global_conf.copy()
        gc.pop(key)
        gc[no_key] = True
        self.assert_success(key, value=True, expected_value=True, conf=gc)
        self.assert_success(key, value="true", expected_value=True, conf=gc)
        self.assert_success(key, value=1, expected_value=True, conf=gc)
        self.assert_success(key, value=2, expected_value=True, conf=gc)

        gc = self.global_conf.copy()
        gc[key] = False
        gc.pop(no_key)
        self.assert_success(no_key, object_key=key, value=False, expected_value=False, conf=gc)
        self.assert_success(no_key, object_key=key, value="false", expected_value=False, conf=gc)
        self.assert_success(no_key, object_key=key, value=0, expected_value=False, conf=gc)
        self.assert_success(no_key, object_key=key, value=-1, expected_value=False, conf=gc)

        # Test invalid values.
        self.assert_fail(key, value="", exception=util.GetError)
        self.assert_fail(key, value=util.random_string(6), exception=util.GetError)


    #
    ##
    #


    def test_log_level(self):
        '''
        Test that 'log_level' is properly handled by the daemon.
        '''

        self.assert_enum(
            "log_level",
            enum=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            test_default=True,
        )


    def test_use_ipsec(self):
        '''
        Test that 'use_ipsec' is properly handled by the daemon.
        '''

        self.assert_boolean("use_ipsec", test_default=True)


    def test_ipsec_manage(self):
        '''
        Test that 'ipsec_manage' is properly handled by the daemon.
        '''

        self.assert_boolean("ipsec_manage", test_default=True)


    def test_ipsec_psk(self):
        '''
        Test that 'ipsec_psk' is properly handled by the daemon.
        '''

        self.assert_hex_string("ipsec_psk", min=6, max=64)


    def test_lib_dir(self):
        '''
        Test that 'lib_dir' is properly handled by the daemon.
        '''

        self.assert_path("lib_dir", test_default=True)


    def test_fwbuilder_script_dir(self):
        '''
        Test that 'fwbuilder_script_dir' is properly handled by the daemon.
        '''

        self.assert_path("fwbuilder_script_dir")


    def test_overlay_conf_dir(self):
        '''
        Test that 'overlay_conf_dir' is properly handled by the daemon.
        '''

        self.assert_path("overlay_conf_dir", test_default=True)


    def test_template_dir(self):
        '''
        Test that 'template_dir' is properly handled by the daemon.
        '''

        self.assert_path("template_dir", test_default=True)


    def test_pid(self):
        '''
        Test that 'pid' is properly handled by the daemon.
        '''

        self.assert_path("pid", test_default=True)


    def test_ipsec_conf(self):
        '''
        Test that 'ipsec_conf' is properly handled by the daemon.
        '''

        self.assert_path("ipsec_conf", test_default=True)


    def test_ipsec_secrets(self):
        '''
        Test that 'ipsec_secrets' is properly handled by the daemon.
        '''

        self.assert_path("ipsec_secrets", test_default=True)


    def test_overlay_conf(self):
        '''
        Test that 'overlay_conf' is properly handled by the daemon.
        '''

        gc = self.global_conf.copy()
        gc["overlay_global_conf"] = None

        # Test absolute paths.
        value = [os.path.join(overlay_conf_dir, f) for f in os.listdir(overlay_conf_dir)]
        self.assert_success(
            "overlay_conf",
            value=value,
            conf=gc,
        )

        # Test relative paths.
        value = [os.path.relpath(os.path.join(overlay_conf_dir, f)) for f in os.listdir(overlay_conf_dir)]
        self.assert_success(
            "overlay_conf",
            value=value,
            conf=gc,
        )

        # Test non-existent paths.
        self.assert_fail(
            "overlay_conf",
            value=[util.random_string(16)],
            exception=FileNotFoundError,
            conf=gc,
        )

        # Test invalid values.
        self.assert_fail("overlay_conf", value="", exception=util.GetError, conf=gc)
        self.assert_fail("overlay_conf", value=1, exception=l3overlay.daemon.ReadError, conf=gc)
        self.assert_fail("overlay_conf", value=[""], exception=util.GetError, conf=gc)
        self.assert_fail("overlay_conf", value=[1], exception=util.GetError, conf=gc)


if __name__ == "__main__":
    unittest.main()
