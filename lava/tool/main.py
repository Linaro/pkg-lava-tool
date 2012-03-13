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
lava.tool.main
==============

Implementation of the `lava` shell command.
"""

from lava.tool.dispatcher import Dispatcher


class LavaDispatcher(Dispatcher):
    """
    Dispatcher implementing the `lava` shell command

    This dispatcher imports plugins from `lava.commands` pkg_resources
    namespace. Additional plugins can be registered as either
    :class:`lava.command.Command` or :class:`lava.command.SubCommand`
    sub-classes.
    """

    def __init__(self):
        super(LavaDispatcher, self).__init__()
        self.import_commands('lava.commands')
