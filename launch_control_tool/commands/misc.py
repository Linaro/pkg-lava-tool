# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of launch-control-tool.
#
# launch-control-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# launch-control-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launch-control-tool.  If not, see <http://www.gnu.org/licenses/>.

"""
Module with miscellaneous commands (such as help and version)
"""

from launch_control_tool.interface import Command
from launch_control_tool import get_version

class help(Command):
    """
    Show a summary of all available commands
    """
    def invoke(self):
        self.parser.print_help()


class version(Command):
    """
    Show dashboard client version
    """
    def invoke(self):
        print "Dashboard client version: {version}".format(
                version = get_version())
