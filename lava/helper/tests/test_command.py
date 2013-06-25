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

"""lava.herlp.command module tests."""

from lava.helper.command import BaseCommand
from lava.helper.tests.helper_test import HelperTest


class BaseCommandTests(HelperTest):

    def test_register_argument(self):
        # Make sure that the parser add_argument is called and we have the
        # correct argument.
        command = BaseCommand(self.parser, self.args)
        command.register_arguments(self.parser)
        name, args, kwargs = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

    def test_can_edit_file(self):
        # Tests the can_edit_file method of the config command.
        # This is to make sure the device config file is not erased when
        # checking if it is possible to open it.
        expected = ("hostname = a_fake_panda02\nconnection_command = \n"
                    "device_type = panda\n")

        command = BaseCommand(self.parser, self.args)
        conf_file = self.temp_file

        with open(conf_file.name, "w") as f:
            f.write(expected)

        self.assertTrue(command.can_edit_file(conf_file.name))
        obtained = ""
        with open(conf_file.name) as f:
            obtained = f.read()

        self.assertEqual(expected, obtained)
