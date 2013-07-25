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

"""Scripts handling class."""

import os
import stat

from lava_tool.utils import write_file


DEFAULT_MOD = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
DEFAULT_TESTDEF_SCRIPT_CONTENT = """#!/bin/sh
# Automatic generated content by lava-tool.
# Please add your own instructions.
#
# You can use all the avialable Bash commands.
#
# For the available LAVA commands, see:
#    http://lava.readthedocs.org/
#
"""
DEFAULT_TESTDEF_SCRIPT = "mytest.sh"


class ShellScript(object):

    """Creates a shell script on the file system with some content."""

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self):
        write_file(self.file_name, DEFAULT_TESTDEF_SCRIPT_CONTENT)
        # Make sure the script is executable.
        os.chmod(self.file_name, DEFAULT_MOD)
