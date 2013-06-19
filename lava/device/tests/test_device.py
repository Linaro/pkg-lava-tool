# Copyright (C) 2013 Linaro Limited
#
# Author: Milo Casagrande <milo.casagrande@linaro.org>
#
# This file is part of lava-tool.
#
# lava-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-tool.  If not, see <http://www.gnu.org/licenses/>.

"""
Device class unit tests.
"""

import sys

from StringIO import StringIO

from lava.device import (
    Device,
    get_known_device,
)
from lava.tool.errors import CommandError
from lava.helper.tests.helper_test import HelperTest


class DeviceTest(HelperTest):

    def test_get_known_device_panda_0(self):
        # User creates a new device with a guessable name for a device.
        instance = get_known_device('panda_new_01')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.template['device_type'], 'panda')
        self.assertIsNone(instance.device_type)

    def test_get_known_device_panda_1(self):
        # User creates a new device with a guessable name for a device.
        # Name passed has capital letters.
        instance = get_known_device('new_PanDa_02')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.template['device_type'], 'panda')
        self.assertIsNone(instance.device_type)

    def test_get_known_device_vexpress_0(self):
        # User creates a new device with a guessable name for a device.
        # Name passed has capital letters.
        instance = get_known_device('a_VexPress_Device')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.template['device_type'], 'vexpress')
        self.assertIsNone(instance.device_type)

    def test_get_known_device_vexpress_1(self):
        # User creates a new device with a guessable name for a device.
        instance = get_known_device('another-vexpress')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.template['device_type'], 'vexpress')
        self.assertIsNone(instance.device_type)

    def test_instance_update(self):
        # Tests that when calling the _update() function with an known device
        # it does not update the device_type instance attribute, and that the
        # template contains the correct name.
        instance = get_known_device('Another_PanDa_device')
        instance._update()
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.template['device_type'], 'panda')
        self.assertIsNone(instance.device_type)

    def test_get_known_device_unknown(self):
        # User tries to create a new device with an unknown device type. She
        # is asked to insert the device type and types 'a_fake_device'.
        sys.stdin = StringIO('a_fake_device')
        instance = get_known_device('a_fake_device')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.device_type, 'a_fake_device')

    def test_get_known_device_known(self):
        # User tries to create a new device with a not recognizable name.
        # She is asked to insert the device type and types 'panda'.
        sys.stdin = StringIO("panda")
        instance = get_known_device("another_fake_device")
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.template["device_type"], "panda")

    def test_get_known_device_raises(self):
        # User tries to create a new device, but in some way nothing is passed
        # on the command line when asked.
        self.assertRaises(CommandError, get_known_device, 'a_fake_device')

    def test_device_write(self):
        # User tries to create a new panda device. The conf file is written
        # and contains the expected results.
        expected = ("hostname = panda02\nconnection_command = \n"
                    "device_type = panda\n")
        instance = get_known_device("panda02")
        instance.write(self.temp_file.name)
        obtained = ""
        with open(self.temp_file.name) as f:
            obtained = f.read()
        self.assertEqual(expected, obtained)
