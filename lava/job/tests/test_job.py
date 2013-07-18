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

from mock import patch
from StringIO import StringIO

from lava.helper.tests.helper_test import HelperTest
from lava.config import Config
from lava.job import Job
from lava.job.templates import BOOT_TEST
from lava.parameter import Parameter


class JobTest(HelperTest):

    @patch("lava.config.Config.save")
    def setUp(self, mocked_config):
        super(JobTest, self).setUp()
        self.config = Config(config_file=self.temp_file.name)

    def tearDown(self):
        super(JobTest, self).tearDown()
        self.config.__metaclass__._drop()

    def test_from_template(self):
        template = {}
        job = Job(template)
        self.assertEqual(job.data, template)
        self.assertIsNot(job.data, template)

    def test_fill_in_data(self):
        image = "/path/to/panda.img"
        param1 = Parameter("device_type")
        param2 = Parameter("image", depends=param1)
        self.config.put_parameter(param1, "panda")
        self.config.put_parameter(param2, image)

        job = Job(BOOT_TEST)
        job.fill_in(self.config)

        self.assertEqual(job.data['device_type'], "panda")
        self.assertEqual(job.data['actions'][0]["parameters"]["image"], image)

    def test_write(self):
        orig_data = {"foo": "bar"}
        job = Job(orig_data)
        output = StringIO()
        job.write(output)

        data = json.loads(output.getvalue())
        self.assertEqual(data, orig_data)

    def test_writes_nicely_formatted_json(self):
        orig_data = {"foo": "bar"}
        job = Job(orig_data)
        output = StringIO()
        job.write(output)

        self.assertTrue(output.getvalue().startswith("{\n"))
