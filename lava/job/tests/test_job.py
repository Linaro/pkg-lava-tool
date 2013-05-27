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
Unit tests for the Job class
"""

import json
from unittest import TestCase
from StringIO import StringIO

from lava.job.templates import *
from lava.job import Job

class JobTest(TestCase):

    def test_from_template(self):
        template = {}
        job = Job(template)
        self.assertEqual(job.data, template)
        self.assertIsNot(job.data, template)

    def test_fill_in_data(self):
        job = Job(BOOT_TEST)
        image = "/path/to/panda.img"
        job.fill_in(
            {
                "device_type": "panda",
                "prebuilt_image": image,
            }
        )

        self.assertEqual(job.data['device_type'], "panda")
        self.assertEqual(job.data['actions'][0]["parameters"]["image"], image)

    def test_write(self):
        orig_data = { "foo": "bar" }
        job = Job(orig_data)
        output = StringIO()
        job.write(output)

        data = json.loads(output.getvalue())
        self.assertEqual(data, orig_data)

    def test_writes_nicely_formatted_json(self):
        orig_data = { "foo": "bar" }
        job = Job(orig_data)
        output = StringIO()
        job.write(output)

        self.assertTrue(output.getvalue().startswith("{\n"))
