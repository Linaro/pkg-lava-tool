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
Unittests for the ShellScript class.
"""

import os
import stat

from lava.helper.tests.helper_test import HelperTest
from lava.script import ShellScript


class ShellScriptTests(HelperTest):

    """ShellScript tests."""

    def test_create_file(self):
        # Tests that a shell script is actually written.
        try:
            temp_file = self.tmp("a_shell_test")
            script = ShellScript(temp_file)
            script.write()

            self.assertTrue(os.path.isfile(temp_file))
        finally:
            os.unlink(temp_file)

    def test_assure_executable(self):
        # Tests that the shell script created is executable.
        try:
            temp_file = self.tmp("a_shell_test")
            script = ShellScript(temp_file)
            script.write()

            expected = (stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH |
                        stat.S_IXOTH)

            obtained = stat.S_IMODE(os.stat(temp_file).st_mode)
            self.assertEquals(expected, obtained)
        finally:
            os.unlink(temp_file)

    def test_shell_script_content(self):
        # Tests that the shell script created contains the exepcted content.
        try:
            temp_file = self.tmp("a_shell_test")
            script = ShellScript(temp_file)
            script.write()

            obtained = ""
            with open(temp_file) as read_file:
                obtained = read_file.read()

            expected = ("#!/bin/sh\n# Automatic generated "
                        "content by lava-tool.\n# Please add your own "
                        "instructions.\n#\n# You can use all the avialable "
                        "Bash commands.\n#\n# For the available LAVA "
                        "commands, see:\n#    http://lava.readthedocs.org/\n"
                        "#\n")

            self.assertEquals(expected, obtained)
        finally:
            os.unlink(temp_file)
