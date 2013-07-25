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

import os
import subprocess
import tempfile

from unittest import TestCase
from mock import patch

from lava_tool.utils import (
    has_command,
    verify_file_extension,
)


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

    def test_verify_file_extension_with_extension(self):
        extension = ".test"
        supported = [extension[1:]]
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=extension,
                                                    delete=False)
            obtained = verify_file_extension(
                temp_file.name, extension[1:], supported)
            self.assertEquals(temp_file.name, obtained)
        finally:
            if os.path.isfile(temp_file.name):
                os.unlink(temp_file.name)

    def test_verify_file_extension_without_extension(self):
        extension = "json"
        supported = [extension]
        expected = "/tmp/a_fake.json"
        obtained = verify_file_extension("/tmp/a_fake", extension, supported)
        self.assertEquals(expected, obtained)

    def test_verify_file_extension_with_unsupported_extension(self):
        extension = "json"
        supported = [extension]
        expected = "/tmp/a_fake.json"
        obtained = verify_file_extension(
            "/tmp/a_fake.extension", extension, supported)
        self.assertEquals(expected, obtained)
