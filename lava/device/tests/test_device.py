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
Device class unit tests.
"""

import os
import sys
import tempfile

from StringIO import StringIO
from unittest import TestCase

from lava.device import (
    Device,
    PandaDevice,
    get_known_device,
)
from lava.tool.errors import CommandError


class DeviceTest(TestCase):

    def setUp(self):
        # Fake the stdin and the stdout
        self.original_stdout = sys.stdout
        sys.stdout = StringIO("/dev/null")
        self.original_stdin = sys.stdin
        sys.stdin = StringIO()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        sys.stdout = self.original_stdout
        sys.stdin = self.original_stdin
        os.unlink(self.temp_file.name)

    def test_get_known_device_panda(self):
        # User creates a new device with a guessable name for a panda device.
        instance = get_known_device('panda_new_01')
        self.assertIsInstance(instance, PandaDevice)

    def test_get_known_device_unknown(self):
        # User tries to create a new device with an unknown device type. She
        # is asked to insert the device type and types 'a_fake_device'.
        sys.stdin = StringIO('a_fake_device')
        instance = get_known_device('a_fake_device')
        self.assertIsInstance(instance, Device)
        self.assertEqual(instance.device_type, 'a_fake_device')

    def test_get_known_device_raises(self):
        # User tries to create a new device, but in some way nothing is passed
        # on the command line when asked.
        self.assertRaises(CommandError, get_known_device, 'a_fake_device')

    def test_device_write(self):
        # User tries to create a new panda device. The conf file is written
        # and containes the expexted results.
        expected = ("hostname = panda02\nconnection_command = None\n"
                    "device_type = panda\n")
        instance = get_known_device("panda02")
        instance.write(self.temp_file.name)
        obtained = ""
        with open(self.temp_file.name) as f:
            obtained = f.read()
        self.assertEqual(expected, obtained)
