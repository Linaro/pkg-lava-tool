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

import yaml

from copy import deepcopy

from lava.helper.template import expand_template
from lava_tool.utils import (
    write_file,
    verify_path_existance,
    verify_file_extension
)

# Default test def file extension.
DEFAULT_TESTDEF_EXTENSION = "yaml"
# Possible extensions for a test def file.
TESTDEF_FILE_EXTENSIONS = [DEFAULT_TESTDEF_EXTENSION]


class TestDefinition(object):

    def __init__(self, data, file_name):
        """Initialize the object.

        :param data: The serializable data to be used, usually a template.
        :type dict
        :param file_name: Where the test definition will be written.
        :type str
        """
        self.file_name = verify_file_extension(file_name,
                                               DEFAULT_TESTDEF_EXTENSION,
                                               TESTDEF_FILE_EXTENSIONS)
        verify_path_existance(self.file_name)

        self.data = deepcopy(data)

    def write(self):
        """Writes the test definition to file."""
        content = yaml.dump(self.data, default_flow_style=False, indent=4)
        write_file(self.file_name, content)

    def update(self, config):
        """Updates the TestDefinition object based on the provided config."""
        expand_template(self.data, config)
