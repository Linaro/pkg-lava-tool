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

from mock import patch

from lava.config import Config
from lava.device import (
    Device,
    get_known_device,
)
from lava.device.templates import (
    HOSTNAME_PARAMETER,
    PANDA_DEVICE_TYPE,
    PANDA_CONNECTION_COMMAND,
)
from lava.helper.tests.helper_test import HelperTest
from lava.parameter import Parameter


class DeviceTest(HelperTest):

    def test_get_known_device_panda_0(self):
        # User creates a new device with a guessable name for a device.
        instance = get_known_device('panda_new_01')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.data['device_type'].value, 'panda')

    def test_get_known_device_panda_1(self):
        # User creates a new device with a guessable name for a device.
        # Name passed has capital letters.
        instance = get_known_device('new_PanDa_02')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.data['device_type'].value, 'panda')

    def test_get_known_device_vexpress_0(self):
        # User creates a new device with a guessable name for a device.
        # Name passed has capital letters.
        instance = get_known_device('a_VexPress_Device')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.data['device_type'].value, 'vexpress')

    def test_get_known_device_vexpress_1(self):
        # User creates a new device with a guessable name for a device.
        instance = get_known_device('another-vexpress')
        self.assertIsInstance(instance, Device)
        self.assertIsInstance(instance.data['device_type'], Parameter)
        self.assertEqual(instance.data['device_type'].value, 'vexpress')

    @patch("lava.config.Config.save")
    def test_device_update_1(self, patched_save):
        # Tests that when calling update() on a Device, the template gets
        # updated with the correct values from a Config instance.
        hostname = "panda_device"

        config = Config()
        config._config_file = self.temp_file.name
        config.put_parameter(HOSTNAME_PARAMETER, hostname)
        config.put_parameter(PANDA_DEVICE_TYPE, "panda")
        config.put_parameter(PANDA_CONNECTION_COMMAND, "test")

        expected = {
            "hostname": hostname,
            "device_type": "panda",
            "connection_command": "test"
        }

        instance = get_known_device(hostname)
        instance.update(config)

        self.assertEqual(expected, instance.data)

    @patch("lava.config.Config.save")
    def test_device_write(self, mocked_save):
        # User tries to create a new panda device. The conf file is written
        # and contains the expected results.
        hostname = "panda_device"

        config = Config()
        config._config_file = self.temp_file.name
        config.put_parameter(HOSTNAME_PARAMETER, hostname)
        config.put_parameter(PANDA_DEVICE_TYPE, "panda")
        config.put_parameter(PANDA_CONNECTION_COMMAND, "test")

        expected = {
            "hostname": hostname,
            "device_type": "panda",
            "connection_command": "test"
        }

        instance = get_known_device(hostname)
        instance.update(config)
        instance.write(self.temp_file.name)

        expected = ("hostname = panda_device\nconnection_command = test\n"
                    "device_type = panda\n")

        obtained = ""
        with open(self.temp_file.name) as f:
            obtained = f.read()
        self.assertEqual(expected, obtained)
