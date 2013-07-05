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
Tests for lava.commands.
"""

import os
import tempfile

from mock import MagicMock

from lava.commands import (
    init,
)
from lava.config import Config
from lava.helper.tests.helper_test import HelperTest
from lava.tool.errors import CommandError


class InitCommandTests(HelperTest):

    def setUp(self):
        super(InitCommandTests, self).setUp()
        self.config_file = self.tmp("init_command_tests")
        self.config = Config(config_file=self.config_file)

    def tearDown(self):
        super(InitCommandTests, self).tearDown()
        self.config.__metaclass__._drop()
        if os.path.isfile(self.config_file):
            os.unlink(self.config_file)

    def test_register_arguments(self):
        self.args.DIR = os.path.join(tempfile.gettempdir(), "a_fake_dir")
        init_command = init(self.parser, self.args)
        init_command.register_arguments(self.parser)

        # Make sure we do not forget about this test.
        self.assertEqual(2, len(self.parser.method_calls))

        _, args, _ = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        _, args, _ = self.parser.method_calls[1]
        self.assertIn("DIR", args)

    def test_command_invoke_0(self):
        # Invoke the init command passing a path to a file. Should raise an
        # exception.
        self.args.DIR = self.temp_file.name
        init_command = init(self.parser, self.args)
        self.assertRaises(CommandError, init_command.invoke)

    def test_command_invoke_1(self):
        # Invoke the init command passing a path to a directory that does not
        # exist.
        try:
            self.args.DIR = self.tmp("a_temp_dir")
            init_command = init(self.parser, self.args)
            init_command._create_files = MagicMock()
            init_command._update_data = MagicMock()
            init_command.invoke()

            self.assertTrue(os.path.isdir(self.args.DIR))
        finally:
            if os.path.exists(self.args.DIR):
                os.removedirs(self.args.DIR)

    def test_command_invoke_2(self):
        # Invoke the init command passing a path where the user cannot write.
        try:
            self.args.DIR = "/root/a_temp_dir"
            init_command = init(self.parser, self.args)
            self.assertRaises(CommandError, init_command.invoke)
        finally:
            if os.path.exists(self.args.DIR):
                os.removedirs(self.args.DIR)

    def test_update_data(self):
        # Make sure the template is updated accordingly with the provided data.
        self.args.DIR = self.temp_file.name

        init_command = init(self.parser, self.args)
        init_command.config.get = MagicMock()
        init_command.config.save = MagicMock()
        init_command.config.get.side_effect = ["a_job.json", "a_test.yaml",
                                               self.temp_file.name]

        expected = {
            "jobfile": "a_job.json",
            "tests": "a_test.yaml",
            "dirname": self.temp_file.name,
        }

        obtained = init_command._update_data()
        self.assertEqual(expected, obtained)
