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

from argparse import ArgumentParser
import json
from os import (
    makedirs,
    removedirs,
)
from os.path import(
    exists,
    join,
)
from shutil import(
    rmtree,
)
from tempfile import mkdtemp
from unittest import TestCase

from lava.config import NonInteractiveConfig
from lava.job.commands import *
from lava.tool.errors import CommandError

def make_command(command, *args):
    parser = ArgumentParser(description="fake argument parser")
    command.register_arguments(parser)
    the_args = parser.parse_args(*args)
    cmd = command(parser, the_args)
    cmd.config = NonInteractiveConfig({ 'device_type': 'foo', 'prebuilt_image': 'bar' })
    return cmd

class CommandTest(TestCase):

    def setUp(self):
        self.tmpdir = mkdtemp()

    def tearDown(self):
        rmtree(self.tmpdir)

    def tmp(self, filename):
        return join(self.tmpdir, filename)

class JobNewTest(CommandTest):

    def test_create_new_file(self):
        f = self.tmp('file.json')
        command = make_command(new, [f])
        command.invoke()
        self.assertTrue(exists(f))

    def test_fills_in_template_parameters(self):
        f = self.tmp('myjob.json')
        command = make_command(new, [f])
        command.invoke()

        data = json.loads(open(f).read())
        self.assertEqual(data['device_type'], 'foo')

    def test_wont_overwriteexisting_file(self):
        existing = self.tmp('existing.json')
        with open(existing, 'w') as f:
            f.write("CONTENTS")
        command = make_command(new, [existing])
        with self.assertRaises(CommandError):
            command.invoke()
        self.assertEqual("CONTENTS", open(existing).read())

