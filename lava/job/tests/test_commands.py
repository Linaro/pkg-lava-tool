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
import shutil
import sys
import tempfile
import argparse

from mock import MagicMock, patch
from unittest import TestCase

from lava.config import NonInteractiveConfig, Parameter

from lava.job.commands import (
    new,
    run,
)

from lava.tool.errors import CommandError


def make_command(command, *args):
    parser = argparse.ArgumentParser(description="fake argument parser")
    command.register_arguments(parser)
    the_args = parser.parse_args(*args)
    cmd = command(parser, the_args)
    cmd.config = NonInteractiveConfig({ 'device_type': 'foo', 'prebuilt_image': 'bar' })
    return cmd


class CommandTest(TestCase):

    def setUp(self):
        # Fake the stdout.
        self.original_stdout = sys.stdout
        sys.stdout = open("/dev/null", "w")
        self.original_stderr = sys.stderr
        sys.stderr = open("/dev/null", "w")
        self.original_stdin = sys.stdin

        self.device = "panda02"

        self.tmpdir = tempfile.mkdtemp()
        self.tmpfile = tempfile.NamedTemporaryFile(delete=False)
        self.parser = MagicMock()
        self.args = MagicMock()
        self.args.interactive = MagicMock(return_value=False)
        self.args.FILE = self.tmpfile.name

        self.device_type = Parameter('device_type')
        self.prebuilt_image = Parameter('prebuilt_image',
                                        depends=self.device_type)
        self.config = NonInteractiveConfig(
            {'device_type': 'foo', 'prebuilt_image': 'bar'})
        # self.config.put_parameter(self.device_type, 'foo')
        # self.config.put_parameter(self.prebuilt_image, 'bar')

    def tearDown(self):
        sys.stdin = self.original_stdin
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        os.unlink(self.tmpfile.name)
        shutil.rmtree(self.tmpdir)

    def tmp(self, filename):
        return os.path.join(self.tmpdir, filename)


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
        cmd = make_command(new, ['FOO.json'])
        self.assertEqual('FOO.json', cmd.args.FILE)


class JobRunTest(CommandTest):

    def test_invoke_raises_0(self):
        # Users passes a non existen job file to the run command.
        self.args.FILE = self.tmp("test_invoke_raises_0.json")
        command = run(self.parser, self.args)
        self.assertRaises(CommandError, command.invoke)

    @patch("lava.job.commands.has_command", new=MagicMock(return_value=False))
    def test_invoke_raises_1(self):
        # Users passes a valid file to the run command, but she does not have
        # the dispatcher installed.
        command = run(self.parser, self.args)
        self.assertRaises(CommandError, command.invoke)
