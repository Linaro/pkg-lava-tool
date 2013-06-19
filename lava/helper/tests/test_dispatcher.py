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

import os
from lava.tool.errors import CommandError

from lava.helper.tests.helper_test import HelperTest

from lava.helper.dispatcher import (
    choose_devices_path,
)


class DispatcherTests(HelperTest):

    def test_choose_devices_path_0(self):
        # Tests that when passing more than one path, the first writable one
        # is returned.
        obtained = choose_devices_path(
            ["/", "/root", self.temp_dir, os.path.expanduser("~")])
        expected = os.path.join(self.temp_dir, "devices")
        self.assertEqual(expected, obtained)

    def test_choose_devices_path_1(self):
        # Tests that when passing a path that is not writable, CommandError
        # is raised.
        self.assertRaises(CommandError, choose_devices_path, ["/", "/root", "/root/tmpdir"])

    def test_choose_devices_path_2(self):
        # Tests that the correct path for devices is created on the filesystem.
        expected_path = os.path.join(self.temp_dir, "devices")
        obtained = choose_devices_path([self.temp_dir])
        self.assertEqual(expected_path, obtained)
        self.assertTrue(os.path.isdir(expected_path))
