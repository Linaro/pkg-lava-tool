# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
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
Module with LavaDispatcher - the command dispatcher
"""

from lava.tool.dispatcher import Dispatcher
from lava.tool.main import LavaDispatcher as LavaNonLegacyDispatcher
from lava_tool.interface import LavaCommandError


class LavaDispatcher(Dispatcher):
    """
    Class implementing command line interface for launch control
    """

    toolname = None

    def __init__(self):
        super(LavaDispatcher, self).__init__()
        prefixes = ['lava_tool']
        if self.toolname is not None:
            prefixes.append(self.toolname)
        for prefix in prefixes:
            self.import_commands("%s.commands" % prefix)


def run_with_dispatcher_class(cls):
    raise cls.run()


def main():
    LavaDispatcher.run()
