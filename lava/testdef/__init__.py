# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
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

import yaml

from copy import deepcopy

from lava.helper.template import expand_template


class TestDefinition(object):

    def __init__(self, testdef_file, data):
        """Initialize the object.

        :param testdef_file: Where the test definition will be written.
        :type str
        :param data: The serializable data to be used, usually a template.
        :type dict
        """
        self.testdef_file = testdef_file
        self.data = deepcopy(data)

    def write(self):
        """Writes the test definition to file."""
        with open(self.testdef_file, 'w') as write_file:
            yaml.dump(self.data, write_file, default_flow_style=False,
                      indent=4)

    def update(self, config):
        """Updates the TestDefinition object based on the provided config."""
        expand_template(self.data, config)
