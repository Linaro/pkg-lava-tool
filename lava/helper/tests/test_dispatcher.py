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

"""lava.helper.dispatcher tests."""

from lava.helper.tests.helper_test import HelperTest


class DispatcherTests(HelperTest):

    def test_choose_devices_path(self):
        # Tests that when passing more than one path, the first writable one
        # is returned.
        base_command = BaseCommand(self.parser, self.args)
        base_command.config = self.config
        obtained = base_command._choose_devices_path(
            ["/", "/root", self.tempdir, os.path.expanduser("~")])
        expected = os.path.join(self.tempdir, "devices")
        self.assertEqual(expected, obtained)

    def test_get_devices_path_1(self):
        # Tests that when passing a path that is not writable, CommandError
        # is raised.
        base_command = BaseCommand(self.parser, self.args)
        base_command.config = self.config
        BaseCommand._get_dispatcher_paths = MagicMock(
            return_value=["/", "/root", "/root/tmpdir"])
        self.assertRaises(CommandError, base_command._get_devices_path)

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
