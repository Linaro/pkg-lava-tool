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

"""lava.helper.command module tests."""

from mock import MagicMock, patch


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

    @patch("lava.helper.command.AuthenticatingServerProxy", create=True)
    def test_authenticated_server(self, mocked_auth_server):
        command = BaseCommand(self.parser, self.args)
        command.config = MagicMock()
        command.config.get = MagicMock()
        command.config.get.side_effect = ["www.example.org", "RPC"]

        command.authenticated_server()

        self.assertTrue(mocked_auth_server.called)
