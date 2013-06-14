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

from lava.job.templates import Parameter


class Job:
    def __init__(self, template):
        self.data = deepcopy(template)

    def fill_in(self, config):

        def insert_data(data):
            if isinstance(data, dict):
                keys = data.keys()
            elif isinstance(data, list):
                keys = range(len(data))
            else:
                return
            for key in keys:
                entry = data[key]
                if isinstance(entry, Parameter):
                    data[key] = config.get(entry)
                else:
                    insert_data(entry)
        insert_data(self.data)

    def write(self, stream):
        stream.write(json.dumps(self.data, indent=4))
