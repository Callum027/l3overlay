#
# IPsec overlay network manager (l3overlay)
# tests/base/overlay.py - base class for overlay-related unit tests
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


import copy

import l3overlay.overlay

import l3overlay.overlay.static_interface

from l3overlay import util

from tests.base import BaseTest


class OverlayBaseTest(object):
    class Class(BaseTest.Class):
        '''
        Base class for overlay-related unit tests.
        '''

        name = "test_overlay_base"


        #
        ##
        #


        def setUp(self):
            '''
            Set up the unit test runtime state.
            '''

            super().setUp()

            self.overlay_conf = {
                "overlay": {
                    "name": "test-overlay-base",
                    "enabled": False,
                    "asn": 65000,
                    "linknet-pool": "198.51.100.0/31",
                    "this-node": "test-1",
                    "node-0": "test-1 192.0.2.1",
                    "node-1": "test-2 192.0.2.2",
                },
            }


        #
        ##
        #


        def config_get(self, *args, conf=None):
            '''
            '''

            oc = copy.deepcopy(conf) if conf else copy.deepcopy(self.overlay_conf)

            # Section is optional. If specified,
            # add the key-value pair to the section
            # of the overlay config.
            if section:
                if section not in oc:
                    oc[section] = {}
                if value is None and key in oc[section]:
                    del oc[section][key]
                elif value is not None:
                    oc[section][key] = value

            # Otherwise, directly add the key-value pair
            # to the top level of the overlay config.
            elif key:
                if key not in oc:
                    oc[key] = {}
                if value is None and key in oc:
                    del oc[key]
                elif value is not None:
                    oc[key] = value

            # Need either at least key specified!
            else:
                raise RuntimeError("key not specified")

            return oc


        def object_get(self, conf=self.overlay_conf):
            '''
            Create an object instance, use assertIsInstance to ensure
            it is of the correct type, and return it.
            '''

            overlay = l3overlay.overlay.read(
                self.global_conf["log"],
                self.global_conf["log_level"],
                config=conf,
            )
            self.assertIsInstance(overlay, l3overlay.overlay.Overlay)

            return overlay


        def value_get(self, *args, obj=None, internal_key=None):
            '''
            Get a value from the given object, using the supplied
            key-value pair (and internal key if used).
            '''

            section = args[0]
            key = internal_key if internal_key else args[1]

            key = k.replace("-", "_")

            if section == "overlay":
                return vars(obj)[key]
            elif section.startswith("static"):
                name = util.section_name_get(section)
                for si in obj.static_interfaces:
                    if name == si.name:
                        return vars(si)[key]
            else:
                raise RuntimeError("unknown section type '%s'" % section)


        def assert_success(self, *args,
                           object_key=None,
                           value=None, expected_value=None,
                           conf=None):
            '''
            Test that an object is successfully created using the given arguments,
            and passes assertions which check the value in the object
            is what is expected.
            '''




        def assert_fail(self, *args,
                        value=None,
                        exception=None, exceptions=[],
                        conf=None):
            '''
            Test that creating an object with the given arguments raises
            a specific exception, or one of a list of exceptions.
            '''


        def assert_default(self, *args, expected_value=None):
            '''
            Test that the default value works properly when reprocessed.
            The point is to test that the default value is valid input.       
            '''

        #
        ##
        #

        def _overlay_config_get(self, section, key, value, conf=None):
            '''
            Create an instance of the overlay config, based off either the
            class variable or a given config dict, optionally specifying
            a given key to override its value with.
            '''


        #
        ##
        #


        def value_get(self, overlay, section, k):
            '''
            Get the value from the given section and key on the overlay.
            '''

            key = k.replace("-", "_")

            if section == "overlay":
                return vars(overlay)[key]
            elif section.startswith("static"):
                name = util.section_name_get(section)
                for si in overlay.static_interfaces:
                    if name == si.name:
                        return vars(si)[key]
            else:
                raise RuntimeError("unknown section type '%s'" % section)


        @staticmethod
        def _overlay_conf_copy(overlay_conf, section, key, value):
            '''
            Make a deep copy of the overlay configuration dictionary,
            update the copy's values, and return the copy.
            '''

            oc = copy.deepcopy(overlay_conf)

            # Section is optional. If specified,
            # add the key-value pair to the section
            # of the overlay config.
            if section:
                if section not in oc:
                    oc[section] = {}
                if value is None and key in oc[section]:
                    del oc[section][key]
                elif value is not None:
                    oc[section][key] = value

            # Otherwise, directly add the key-value pair
            # to the top level of the overlay config.
            elif key:
                if key not in oc:
                    oc[key] = {}
                if value is None and key in oc:
                    del oc[key]
                elif value is not None:
                    oc[key] = value

            # Need either at least key specified!
            else:
                raise RuntimeError("key not specified")

            return oc


        @staticmethod
        def _overlay_read(overlay_conf, section, key, value):
            '''
            '''

            oc = OverlayBaseTest._overlay_conf_copy(overlay_conf, section, key, value)

            return l3overlay.overlay.read(
                self.global_conf["log"],
                self.global_conf["log_level"],
                config=oc,
            )


        def _assert_success(self, overlay):
            '''
            '''

            self.assertIsInstance(overlay, l3overlay.overlay.Overlay)


        def _assert_value(self, overlay, section, key, value):
            '''
            '''

            k = expected_key if expected_key else key

            # Overlay static interface config value checking.
            if l3overlay.overlay.static_interface.section_type_is_static_interface(section):
                for si in overlay.static_interfaces:
                    if si.name == util.section_name_get(section):
                        self.assertEqual(value, vars(si)[k.replace("-", "_")])
                        break

            # Overlay config value checking.
            else:
                self.assertEqual(value, vars(overlay)[k.replace("-", "_")])


        def assert_success(self, section, key, value,
                expected_value=None, expected_key=None):
            '''
            Try and read an l3overlay daemon using the given arguments.
            Assumes it will succeed, and will run an assertion test to make
            sure a Daemon is returned.
            '''

            overlay = OverlayBaseTest._overlay_read(
                self.overlay_conf,
                section,
                key,
                value,
            )

            self._assert_success(overlay)
            self._assert_value(
                overlay,
                section,
                expected_key if expected_key else key,
                expected_value if expected_value else value,
            )


        def assert_fail(self, section, key, value, *exceptions):
            '''
            Try and read an l3overlay daemon using the given arguments.
            Assumes it will fail, and raises a RuntimeError if it doesn't.
            '''

            if not exceptions:
                raise RuntimeError("no exceptions to test for")

            try:
                OverlayBaseTest._overlay_read(
                    self.overlay_conf,
                    section,
                    key,
                    value,
                )
                raise RuntimeError('''l3overlay.overlay.read unexpectedly returned successfully
    Expected exception types: %s
    Arguments: %s''' % (str.join(", ", (e.__name__ for e in exceptions)), oc))

            except exceptions:
                pass


        def assert_default(self, section, key, expected_value):
            '''
            Try and read an l3overlay daemon using the given arguments.
            Assumes it will succeed, and will check to make sure the given
            key is, by default, the expected value.
            '''

            overlay = OverlayBaseTest._overlay_read(oc, section, key, None)

            self._assert_success(overlay)
            self._assert_value(
                overlay,
                section,
                key,
                expected_value,
            )
