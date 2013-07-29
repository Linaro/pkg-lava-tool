# Copyright (C) 2013 Linaro Limited
#
# Author: Antonio Terceiro <antonio.terceiro@linaro.org>
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
Unit tests for the commands classes
"""

import json
import os

from mock import patch

from lava.config import Config
from lava.helper.tests.helper_test import HelperTest
from lava.job.commands import (
    new,
    run,
    submit,
    status,
)
from lava.parameter import Parameter
from lava.tool.errors import CommandError


class CommandTest(HelperTest):

    def setUp(self):
        super(CommandTest, self).setUp()
        self.args.FILE = self.temp_file.name
        self.args.type = "boot-test"

        self.device_type = Parameter('device_type')
        self.prebuilt_image = Parameter('prebuilt_image',
                                        depends=self.device_type)
        self.config = Config()
        self.config.put_parameter(self.device_type, 'foo')
        self.config.put_parameter(self.prebuilt_image, 'bar')


class JobNewTest(CommandTest):

    def setUp(self):
        super(JobNewTest, self).setUp()
        self.args.FILE = self.tmp("new_file.json")
        self.new_command = new(self.parser, self.args)
        self.new_command.config = self.config

    def tearDown(self):
        super(JobNewTest, self).tearDown()
        if os.path.exists(self.args.FILE):
            os.unlink(self.args.FILE)

    def test_register_arguments(self):
        new_cmd = new(self.parser, self.args)
        new_cmd.register_arguments(self.parser)

        # Make sure we do not forget about this test.
        self.assertEqual(3, len(self.parser.method_calls))

        _, args, _ = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        _, args, _ = self.parser.method_calls[1]
        self.assertIn("FILE", args)

        _, args, _ = self.parser.method_calls[2]
        self.assertIn("--type", args)

    def test_create_new_file(self):
        self.new_command.invoke()
        self.assertTrue(os.path.exists(self.args.FILE))

    def test_fills_in_template_parameters(self):
        self.new_command.invoke()

        data = json.loads(open(self.args.FILE).read())
        self.assertEqual(data['device_type'], 'foo')

    def test_wont_overwrite_existing_file(self):
        with open(self.args.FILE, 'w') as f:
            f.write("CONTENTS")

        self.assertRaises(CommandError, self.new_command.invoke)
        self.assertEqual("CONTENTS", open(self.args.FILE).read())


class JobSubmitTest(CommandTest):

    def test_receives_job_file_in_cmdline(self):
        command = submit(self.parser, self.args)
        command.register_arguments(self.parser)
        name, args, kwargs = self.parser.method_calls[1]
        self.assertIn("FILE", args)


class JobRunTest(CommandTest):

    def test_register_arguments(self):
        run_cmd = run(self.parser, self.args)
        run_cmd.register_arguments(self.parser)

        # Make sure we do not forget about this test.
        self.assertEqual(2, len(self.parser.method_calls))

        _, args, _ = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        _, args, _ = self.parser.method_calls[1]
        self.assertIn("FILE", args)

    def test_invoke_raises_0(self):
        # Users passes a non existing job file to the run command.
        self.args.FILE = self.tmp("test_invoke_raises_0.json")
        command = run(self.parser, self.args)
        self.assertRaises(CommandError, command.invoke)

    @patch("lava.helper.command.has_command", create=True)
    def test_invoke_raises_1(self, mocked_has_command):
        # User passes a valid file to the run command, but she does not have
        # the dispatcher installed.
        mocked_has_command.return_value = False
        command = run(self.parser, self.args)
        self.assertRaises(CommandError, command.invoke)


class TestsStatusCommand(CommandTest):

    def test_register_arguments(self):
        self.args.JOB_ID = "1"
        status_cmd = status(self.parser, self.args)
        status_cmd.register_arguments(self.parser)

        # Make sure we do not forget about this test.
        self.assertEqual(2, len(self.parser.method_calls))

        _, args, _ = self.parser.method_calls[0]
        self.assertIn("--non-interactive", args)

        _, args, _ = self.parser.method_calls[1]
        self.assertIn("JOB_ID", args)
