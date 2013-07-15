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

"""lava.herlp.command module tests."""

import os
import subprocess
import tempfile

from mock import (
    MagicMock,
    call,
    patch,
)

from lava.helper.command import BaseCommand
from lava.helper.tests.helper_test import HelperTest
from lava.tool.errors import CommandError


class BaseCommandTests(HelperTest):

    def test_register_argument(self):
        # Make sure that the parser add_argument is called and we have the
        # correct argument.
        command = BaseCommand(self.parser, self.args)
        command.register_arguments(self.parser)
        name, args, kwargs = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

    def test_can_edit_file(self):
        # Tests the can_edit_file method of the config command.
        # This is to make sure the device config file is not erased when
        # checking if it is possible to open it.
        expected = ("hostname = a_fake_panda02\nconnection_command = \n"
                    "device_type = panda\n")

        command = BaseCommand(self.parser, self.args)
        conf_file = self.temp_file

        with open(conf_file.name, "w") as f:
            f.write(expected)

        self.assertTrue(command.can_edit_file(conf_file.name))
        obtained = ""
        with open(conf_file.name) as f:
            obtained = f.read()

        self.assertEqual(expected, obtained)

    @patch("lava.helper.command.subprocess")
    def test_run_0(self, mocked_subprocess):
        mocked_subprocess.check_call = MagicMock()
        BaseCommand.run("foo")
        self.assertEqual(mocked_subprocess.check_call.call_args_list,
                         [call(["foo"])])
        self.assertTrue(mocked_subprocess.check_call.called)

    @patch("lava.helper.command.subprocess.check_call")
    def test_run_1(self, mocked_check_call):
        mocked_check_call.side_effect = subprocess.CalledProcessError(1, "foo")
        self.assertRaises(CommandError, BaseCommand.run, ["foo"])

    @patch("lava.helper.command.subprocess")
    @patch("lava.helper.command.has_command", return_value=False)
    @patch("lava.helper.command.os.environ.get", return_value=None)
    @patch("lava.helper.command.sys.exit")
    def test_edit_file_0(self, mocked_sys_exit, mocked_env_get,
                         mocked_has_command, mocked_subprocess):
        BaseCommand.edit_file(self.temp_file.name)
        self.assertTrue(mocked_sys_exit.called)

    @patch("lava.helper.command.subprocess")
    @patch("lava.helper.command.has_command", side_effect=[True, False])
    @patch("lava.helper.command.os.environ.get", return_value=None)
    def test_edit_file_1(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        BaseCommand.edit_file(self.temp_file.name)
        expected = [call(["sensible-editor", self.temp_file.name])]
        self.assertEqual(expected, mocked_subprocess.Popen.call_args_list)

    @patch("lava.helper.command.subprocess")
    @patch("lava.helper.command.has_command", side_effect=[False, True])
    @patch("lava.helper.command.os.environ.get", return_value=None)
    def test_edit_file_2(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        BaseCommand.edit_file(self.temp_file.name)
        expected = [call(["xdg-open", self.temp_file.name])]
        self.assertEqual(expected, mocked_subprocess.Popen.call_args_list)

    @patch("lava.helper.command.subprocess")
    @patch("lava.helper.command.has_command", return_value=False)
    @patch("lava.helper.command.os.environ.get", return_value="vim")
    def test_edit_file_3(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        BaseCommand.edit_file(self.temp_file.name)
        expected = [call(["vim", self.temp_file.name])]
        self.assertEqual(expected, mocked_subprocess.Popen.call_args_list)

    @patch("lava.helper.command.subprocess")
    @patch("lava.helper.command.has_command", return_value=False)
    @patch("lava.helper.command.os.environ.get", return_value="vim")
    def test_edit_file_4(self, mocked_env_get, mocked_has_command,
                         mocked_subprocess):
        mocked_subprocess.Popen = MagicMock()
        mocked_subprocess.Popen.side_effect = Exception()
        self.assertRaises(CommandError, BaseCommand.edit_file,
                          self.temp_file.name)

    def test_verify_file_extension_with_extension(self):
        extension = ".test"
        supported = [extension[1:]]
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=extension)
            obtained = BaseCommand.verify_file_extension(
                temp_file.name, extension[1:], supported)
            self.assertEquals(temp_file.name, obtained)
        finally:
            os.unlink(temp_file.name)

    def test_verify_file_extension_without_extension(self):
        extension = "json"
        supported = [extension]
        expected = "/tmp/a_fake.json"
        obtained = BaseCommand.verify_file_extension(
            "/tmp/a_fake", extension, supported)
        self.assertEquals(expected, obtained)

    def test_verify_file_extension_with_unsupported_extension(self):
        extension = "json"
        supported = [extension]
        expected = "/tmp/a_fake.json"
        obtained = BaseCommand.verify_file_extension(
            "/tmp/a_fake.extension", extension, supported)
        self.assertEquals(expected, obtained)
