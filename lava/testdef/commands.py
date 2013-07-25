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


class testdef(CommandGroup):

    """LAVA test definitions handling."""

    namespace = "lava.testdef.commands"


class new(BaseCommand):

    """Creates a new test definition file."""

    @classmethod
    def register_arguments(cls, parser):
        super(new, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Test definition file to create.")

    def invoke(self, testdef_template=TESTDEF_TEMPLATE):
        full_path = os.path.abspath(self.args.FILE)

        testdef = TestDefinition(testdef_template, full_path)
        testdef.update(self.config)
        testdef.write()


class run(BaseCommand):

    """Runs the specified test definition on a local device."""

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Test definition file to run.")

    def invoke(self):
        pass


def submit(BaseCommand):
    """Submits the specified test definition to a remove LAVA server."""

    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Test definition file to send.")

    def invoke(self):
        pass
