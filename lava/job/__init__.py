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

"""Job class."""

import json

from copy import deepcopy

from lava.helper.template import (
    expand_template,
    set_value,
)
from lava_tool.utils import (
    verify_file_extension,
    verify_path_existance,
    write_file
)

# A default name for job files.
DEFAULT_JOB_FILENAME = "lava-tool-job.json"
# Default job file extension.
DEFAULT_JOB_EXTENSION = "json"
# Possible extension for a job file.
JOB_FILE_EXTENSIONS = [DEFAULT_JOB_EXTENSION]


class Job(object):

    """A Job object.

    This class should be used to create new job files. The initialization
    enforces a default file name extension, and makes sure that the file is
    not already present on the file system.
    """

    def __init__(self, data, file_name):
        self.file_name = verify_file_extension(file_name,
                                               DEFAULT_JOB_EXTENSION,
                                               JOB_FILE_EXTENSIONS)
        verify_path_existance(self.file_name)
        self.data = deepcopy(data)

    def set(self, key, value):
        """Set key to the specified value.

        :param key: The key to look in the object data.
        :param value: The value to set.
        """
        set_value(self.data, key, value)

    def update(self, config):
        """Updates the Job object based on the provided config."""
        expand_template(self.data, config)

    def write(self):
        """Writes the Job object to file."""
        write_file(self.file_name, json.dumps(self.data, indent=4))
