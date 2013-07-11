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

from copy import deepcopy
import json

from lava.helper.template import expand_template


class Job:
    def __init__(self, template):
        self.data = deepcopy(template)

    def __getitem__(self, key):

        def getelement(element, data):
            for key, value in data.iteritems():
                if key == element:
                    return value
                elif isinstance(value, dict):
                    return getelement(key, value)

        return getelement(key, self.data)

    def fill_in(self, config):
        expand_template(self.data, config)

    def write(self, stream):
        stream.write(json.dumps(self.data, indent=4))
