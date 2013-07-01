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
Test definition commands class.
"""

import os

from lava.helper.command import BaseCommand
from lava.testdef import TestDefinition
from lava.testdef.templates import TESTDEF_TEMPLATE
from lava.tool.command import CommandGroup
from lava.tool.errors import CommandError


class testdef(CommandGroup):
    """LAVA test definitions handling."""

    namespace = "lava.testdef.commands"


class new(BaseCommand):

    @classmethod
    def register_arguments(cls, parser):
        super(new, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Test definition file to be created.")

    def invoke(self):
        if os.path.exists(self.args.FILE):
            raise CommandError("Test definition file '{0}' already "
                               "exists.".format(self.args.FILE))
        try:
            testdef = TestDefinition(self.args.FILE, TESTDEF_TEMPLATE)
            testdef.update(self.config)
            testdef.write()
        except IOError:
            raise CommandError("Cannot write file '{0}': permission "
                               "denied".format(self.args.FILE))
