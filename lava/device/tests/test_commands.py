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

from mock import (
    MagicMock,
    call,
    patch,
)

from lava.device.commands import (
    add,
    config,
    remove,
)
from lava.helper.tests.helper_test import HelperTest
from lava.tool.errors import CommandError


class AddCommandTest(HelperTest):

    def test_register_argument(self):
        # Make sure that the parser add_argument is called and we have the
        # correct argument.
        add_command = add(self.parser, self.args)
        add_command.register_arguments(self.parser)
        name, args, kwargs = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        name, args, kwargs = self.parser.method_calls[1]
        self.assertIn("DEVICE", args)

    @patch("lava.device.commands.edit_file", create=True)
    @patch("lava.device.Device.__str__")
    @patch("lava.device.Device.update")
    @patch("lava.device.commands.get_device_file")
    @patch("lava.device.commands.get_devices_path")
    def test_add_invoke_0(self, mocked_get_devices_path,
                          mocked_get_device_file, mocked_update, mocked_str,
                          mocked_edit_file):
        # Tests invocation of the add command. Verifies that the conf file is
        # written to disk.
        mocked_get_devices_path.return_value = self.temp_dir
        mocked_get_device_file.return_value = None
        mocked_str.return_value = ""

        add_command = add(self.parser, self.args)
        add_command.invoke()

        expected_path = os.path.join(self.temp_dir,
                                     ".".join([self.device, "conf"]))
        self.assertTrue(os.path.isfile(expected_path))

    @patch("lava.device.commands.edit_file", create=True)
    @patch("lava.device.commands.get_known_device")
    @patch("lava.device.commands.get_devices_path")
    @patch("lava.device.commands.sys.exit")
    @patch("lava.device.commands.get_device_file")
    def test_add_invoke_1(self, mocked_get_device_file, mocked_sys_exit,
                          mocked_get_devices_path, mocked_get_known_device,
                          mocked_edit_file):
        mocked_get_devices_path.return_value = self.temp_dir
        mocked_get_device_file.return_value = self.temp_file.name

        add_command = add(self.parser, self.args)
        add_command.invoke()

        self.assertTrue(mocked_sys_exit.called)


class RemoveCommandTests(HelperTest):

    def test_register_argument(self):
        # Make sure that the parser add_argument is called and we have the
        # correct argument.
        command = remove(self.parser, self.args)
        command.register_arguments(self.parser)
        name, args, kwargs = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        name, args, kwargs = self.parser.method_calls[1]
        self.assertIn("DEVICE", args)

    @patch("lava.device.commands.edit_file", create=True)
    @patch("lava.device.Device.__str__", return_value="")
    @patch("lava.device.Device.update")
    @patch("lava.device.commands.get_device_file")
    @patch("lava.device.commands.get_devices_path")
    def test_remove_invoke(self, get_devices_path_mock, get_device_file_mock,
                           mocked_update, mocked_str, mocked_edit_file):
        # Tests invocation of the remove command. Verifies that the conf file
        # has been correctly removed.
        # First we add a new conf file, then we remove it.
        get_device_file_mock.return_value = None
        get_devices_path_mock.return_value = self.temp_dir

        add_command = add(self.parser, self.args)
        add_command.invoke()

        expected_path = os.path.join(self.temp_dir,
                                     ".".join([self.device, "conf"]))

        # Set new values for the mocked function.
        get_device_file_mock.return_value = expected_path

        remove_command = remove(self.parser, self.args)
        remove_command.invoke()

        self.assertFalse(os.path.isfile(expected_path))

    @patch("lava.device.commands.get_device_file",
           new=MagicMock(return_value="/root"))
    def test_remove_invoke_raises(self):
        # Tests invocation of the remove command, with a non existent device
        # configuration file.
        remove_command = remove(self.parser, self.args)
        self.assertRaises(CommandError, remove_command.invoke)


class ConfigCommanTests(HelperTest):

    def test_register_argument(self):
        # Make sure that the parser add_argument is called and we have the
        # correct argument.
        command = config(self.parser, self.args)
        command.register_arguments(self.parser)
        name, args, kwargs = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        name, args, kwargs = self.parser.method_calls[1]
        self.assertIn("DEVICE", args)

    @patch("lava.device.commands.can_edit_file", create=True)
    @patch("lava.device.commands.edit_file", create=True)
    @patch("lava.device.commands.get_device_file")
    def test_config_invoke_0(self, mocked_get_device_file, mocked_edit_file,
                             mocked_can_edit_file):
        command = config(self.parser, self.args)

        mocked_can_edit_file.return_value = True
        mocked_get_device_file.return_value = self.temp_file.name
        command.invoke()

        self.assertTrue(mocked_edit_file.called)
        self.assertEqual([call(self.temp_file.name)],
                         mocked_edit_file.call_args_list)

    @patch("lava.device.commands.get_device_file",
           new=MagicMock(return_value=None))
    def test_config_invoke_raises_0(self):
        # Tests invocation of the config command, with a non existent device
        # configuration file.
        config_command = config(self.parser, self.args)
        self.assertRaises(CommandError, config_command.invoke)

    @patch("lava.device.commands.get_device_file",
           new=MagicMock(return_value="/etc/password"))
    def test_config_invoke_raises_1(self):
        # Tests invocation of the config command, with a non writable file.
        # Hopefully tests are not run as root.
        config_command = config(self.parser, self.args)
        self.assertRaises(CommandError, config_command.invoke)
