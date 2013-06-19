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
lava.device.commands unit tests.
"""

import os

from mock import MagicMock, patch

from lava.device.commands import (
    add,
    config,
    remove,
)
from lava.helper.tests.helper_test import HelperTest
from lava.tool.errors import CommandError


class CommandsTest(HelperTest):

    @patch("lava.device.commands.get_device_file", new=MagicMock(return_value=None))
    @patch("lava.device.commands.get_devices_path")
    def test_add_invoke(self, get_devices_path_mock):
        # Tests invocation of the add command. Verifies that the conf file is
        # written to disk.
        get_devices_path_mock.return_value = self.temp_dir

        add_command = add(self.parser, self.args)
        add_command.edit_file = MagicMock()
        add_command.invoke()

        expected_path = os.path.join(self.temp_dir,
                                     ".".join([self.device, "conf"]))
        self.assertTrue(os.path.isfile(expected_path))

    @patch("lava.device.commands.get_device_file")
    @patch("lava.device.commands.get_devices_path")
    def test_remove_invoke(self, get_devices_path_mock, get_device_file_mock):
        # Tests invocation of the remove command. Verifies that the conf file
        # has been correctly removed.
        # First we add a new conf file, then we remove it.
        get_device_file_mock.return_value = None
        get_devices_path_mock.return_value = self.temp_dir

        add_command = add(self.parser, self.args)
        add_command.edit_file = MagicMock()
        add_command.invoke()

        expected_path = os.path.join(self.temp_dir,
                                     ".".join([self.device, "conf"]))

        # Set new values for the mocked function.
        get_device_file_mock.return_value = expected_path

        remove_command = remove(self.parser, self.args)
        remove_command.invoke()

        self.assertFalse(os.path.isfile(expected_path))

    @patch("lava.device.commands.get_device_file", new=MagicMock(return_value="/root"))
    def test_remove_invoke_raises(self):
        # Tests invocation of the remove command, with a non existent device
        # configuration file.
        remove_command = remove(self.parser, self.args)
        self.assertRaises(CommandError, remove_command.invoke)

    @patch("lava.device.commands.get_device_file", new=MagicMock(return_value=None))
    def test_config_invoke_raises_0(self):
        # Tests invocation of the config command, with a non existent device
        # configuration file.
        config_command = config(self.parser, self.args)
        self.assertRaises(CommandError, config_command.invoke)

    @patch("lava.device.commands.get_device_file", new=MagicMock(return_value="/etc/password"))
    def test_config_invoke_raises_1(self):
        # Tests invocation of the config command, with a non writable file.
        # Hopefully tests are not run as root.
        config_command = config(self.parser, self.args)
        self.assertRaises(CommandError, config_command.invoke)
