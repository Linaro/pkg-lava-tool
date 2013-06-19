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
Commands class unit tests.
"""

import os
import shutil
import sys
import tempfile

from mock import MagicMock
from unittest import TestCase

from lava.device.commands import (
    BaseCommand,
    add,
    config,
    remove,
)

from lava.tool.errors import CommandError


class CommandsTest(TestCase):
    def setUp(self):
        # Fake the stdout.
        self.original_stdout = sys.stdout
        sys.stdout = open("/dev/null", "w")
        self.original_stderr = sys.stderr
        sys.stderr = open("/dev/null", "w")
        self.original_stdin = sys.stdin

        self.device = "a_fake_panda02"

        self.tempdir = tempfile.mkdtemp()
        self.parser = MagicMock()
        self.args = MagicMock()
        self.args.interactive = MagicMock(return_value=False)
        self.args.DEVICE = self.device

        self.config = MagicMock()
        self.config.get = MagicMock(return_value=self.tempdir)

    def tearDown(self):
        sys.stdin = self.original_stdin
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        shutil.rmtree(self.tempdir)

    def test_get_devices_path_0(self):
        # Tests that the correct devices path is returned and created.
        base_command = BaseCommand(self.parser, self.args)
        base_command.config = self.config
        BaseCommand._get_dispatcher_paths = MagicMock(return_value=[
            self.tempdir])
        obtained = base_command._get_devices_path()
        expected_path = os.path.join(self.tempdir, "devices")
        self.assertEqual(expected_path, obtained)
        self.assertTrue(os.path.isdir(expected_path))

    def test_get_devices_path_1(self):
        # Tests that when passing a path that is not writable, CommandError
        # is raised.
        base_command = BaseCommand(self.parser, self.args)
        base_command.config = self.config
        BaseCommand._get_dispatcher_paths = MagicMock(
            return_value=["/", "/root", "/root/tmpdir"])
        self.assertRaises(CommandError, base_command._get_devices_path)

    def test_choose_devices_path(self):
        # Tests that when passing more than one path, the first writable one
        # is returned.
        base_command = BaseCommand(self.parser, self.args)
        base_command.config = self.config
        obtained = base_command._choose_devices_path(
            ["/", "/root", self.tempdir, os.path.expanduser("~")])
        expected = os.path.join(self.tempdir, "devices")
        self.assertEqual(expected, obtained)

    def test_add_invoke(self):
        # Tests invocation of the add command. Verifies that the conf file is
        # written to disk.
        add_command = add(self.parser, self.args)
        add_command.edit_config_file = MagicMock()
        add_command._get_device_file = MagicMock(return_value=None)
        add_command._get_devices_path = MagicMock(return_value=self.tempdir)
        add_command.invoke()

        expected_path = os.path.join(self.tempdir,
                                     ".".join([self.device, "conf"]))
        self.assertTrue(os.path.isfile(expected_path))

    def test_remove_invoke(self):
        # Tests invocation of the remove command. Verifies that the conf file
        # has been correctly removed.
        # First we add a new conf file, then we remove it.
        add_command = add(self.parser, self.args)
        add_command.edit_config_file = MagicMock()
        add_command._get_device_file = MagicMock(return_value=None)
        add_command._get_devices_path = MagicMock(return_value=self.tempdir)
        add_command.invoke()

        expected_path = os.path.join(self.tempdir,
                                     ".".join([self.device, "conf"]))

        remove_command = remove(self.parser, self.args)
        remove_command._get_device_file = MagicMock(return_value=expected_path)
        remove_command._get_devices_path = MagicMock(return_value=self.tempdir)
        remove_command.invoke()

        self.assertFalse(os.path.isfile(expected_path))

    def test_remove_invoke_raises(self):
        # Tests invocation of the remove command, with a non existent device
        # configuration file.
        remove_command = remove(self.parser, self.args)
        remove_command._get_device_file = MagicMock(return_value="/root")

        self.assertRaises(CommandError, remove_command.invoke)

    def test_config_invoke_raises_0(self):
        # Tests invocation of the config command, with a non existent device
        # configuration file.
        config_command = config(self.parser, self.args)
        config_command._get_device_file = MagicMock(return_value=None)

        self.assertRaises(CommandError, config_command.invoke)

    def test_config_invoke_raises_1(self):
        # Tests invocation of the config command, with a non writable file.
        # Hopefully tests are not run as root.
        config_command = config(self.parser, self.args)
        config_command._get_device_file = MagicMock(return_value="/etc/passwd")

        self.assertRaises(CommandError, config_command.invoke)

    def test_can_edit_file(self):
        # Tests the can_edit_file method of the config command.
        # This is to make sure the device config file is not erased when
        # checking if it is possible to open it.
        expected = ("hostname = a_fake_panda02\nconnection_command = \n"
                    "device_type = panda\n")

        config_command = config(self.parser, self.args)
        try:
            conf_file = tempfile.NamedTemporaryFile(delete=False)

            with open(conf_file.name, "w") as f:
                f.write(expected)

            self.assertTrue(config_command.can_edit_file(conf_file.name))
            obtained = ""
            with open(conf_file.name) as f:
                obtained = f.read()

            self.assertEqual(expected, obtained)
        finally:
            os.unlink(conf_file.name)
