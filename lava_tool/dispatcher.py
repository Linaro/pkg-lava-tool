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

import logging
import sys

from lava_tool.interface import LavaCommandError, BaseDispatcher 


class LavaDispatcher(BaseDispatcher):
    """
    Class implementing command line interface for lava-tool
    
    .. note::
    
        This class is the legacy dispatcher. It imports all commands in a flat namespace.
        Instead of using it in new tools please use the LavaNonLegacyDispatcher. It has
        support for sub-sub commands. Ideally we want all commands to be available as
        ``lava {command} [{subcommand}]``.
    """

    toolname = None

    def __init__(self):
        super(LavaDispatcher, self).__init__()
        prefixes = ['lava_tool']
        if self.toolname is not None:
            prefixes.append(self.toolname)
        for prefix in prefixes:
            self.import_commands("%s.commands" % prefix)


class LavaNonLegacyDispatcher(BaseDispatcher):
    """
    A dispatcher that wants to load only top-level commands,
    not everything-and-the-kitchen-sink into one flat namespace

    Available as `lava` command from shell
    """

    def __init__(self):
        super(LavaNonLegacyDispatcher, self).__init__()
        self.import_commands('lava.commands')


def run_with_dispatcher_class(cls):
    raise SystemExit(cls().dispatch())


def main():
    run_with_dispatcher_class(LavaDispatcher)


def main_nonlegacy():
    run_with_dispatcher_class(LavaNonLegacyDispatcher)
