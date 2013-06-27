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
Tests for the lava.testdef commands.
"""

from lava.helper.tests.helper_test import HelperTest
from lava.testdef.commands import (
    new,
)


class NewCommandTest(HelperTest):

    def test_register_arguments(self):
        # Make sure that the parser add_argument is called and we have the
        # correct argument.
        new_command = new(self.parser, self.args)
        new_command.register_arguments(self.parser)

        # Make sure we do not forget about this test.
        self.assertEqual(2, len(self.parser.method_calls))

        name, args, kwargs = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        name, args, kwargs = self.parser.method_calls[1]
        self.assertIn("FILE", args)
