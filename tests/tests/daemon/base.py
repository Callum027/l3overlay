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


class DaemonBaseTest(object):
    class Class(BaseTest.Class):
        '''
        l3overlay unit test for reading Daemon objects.
        '''

        name = "test_daemon_base"


        #
        ##
        #


        def assert_success(self, *args,
                           object_key=None,
                           value=None, expected_value=None,
                           conf=None):
            '''
            Test that an object is successfully created using the given arguments,
            and passes assertions which check the value in the object
            is what is expected.
            '''

            key = args[0]

            daemon = l3overlay.daemon.read(self._global_config_get(key, value, conf))
            self.assertIsInstance(daemon, l3overlay.daemon.Daemon)

            if expected_value is not None:
                self.assertEqual(
                    expected_value,
                    vars(daemon)[object_key if object_key else key],
                )


        def assert_fail(self, *args,
                        value=None,
                        exception=None, exceptions=[],
                        conf=None):
            '''
            Test that creating an object with the given arguments raises
            a specific exception, or one of a list of exceptions.
            '''

            key = args[0]
            excs = tuple(exceptions) if exceptions else (exception,)

            gc = self._global_config_get(key, value, conf)

            try:
                l3overlay.daemon.read(gc)
                raise RuntimeError('''l3overlay.daemon.read unexpectedly returned successfully
    Expected exception types: %s
    Arguments: %s''' % (str.join(", ", (e.__name__ for e in excs)), gc))

            except excs:
                pass


        def assert_default(self, *args, expected_value=None):
            '''
            Test that the default value works properly when reprocessed.
            The point is to test that the default value is valid input.       
            '''

            key = args[0]

            daemon = l3overlay.daemon.read(self.global_conf)
            actual_value = vars(daemon)[key]

            if expected_value:
                self.assertEqual(actual_value, expected_value)

            # Feed the default value as an explicit value into the creation
            # of an object, to make sure it can be processed correctly.
            self.assert_success(key, value=actual_value, expected_value=actual_value)


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

        def _global_config_get(self, key, value, conf=None):
            '''
            Create an instance of the global config, based off either the
            class variable or a given config dict, optionally specifying
            a given key to override its value with.
            '''

            gc = conf.copy() if conf else self.global_conf.copy()

            if value is not None:
                gc[key] = value

            return gc
