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

"""lava_tool.utils tests."""

import subprocess

from unittest import TestCase
from mock import patch

from lava_tool.utils import has_command


class UtilTests(TestCase):

    @patch("lava_tool.utils.subprocess.check_call")
    def test_has_command_0(self, mocked_check_call):
        # Make sure we raise an exception when the subprocess is called.
        mocked_check_call.side_effect = subprocess.CalledProcessError(0, "")
        self.assertFalse(has_command(""))

    @patch("lava_tool.utils.subprocess.check_call")
    def test_has_command_1(self, mocked_check_call):
        # Check that a "command" exists. The call to subprocess is mocked.
        mocked_check_call.return_value = 0
        self.assertTrue(has_command(""))
