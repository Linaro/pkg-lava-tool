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
This is just a place where to store a template like dictionary that
will be used to serialize a Device object.
"""

from lava.config import Config
from lava.parameter import Parameter

# The hostname parameter is always in the DEFAULT config section.
HOSTNAME_PARAMETER = Parameter("hostname")
DEVICE_TYPE_PARAMETER = Parameter("device_type", depends=HOSTNAME_PARAMETER)
CONNECTION_COMMAND_PARMETER = Parameter("connection_command",
                                        depends=DEVICE_TYPE_PARAMETER)

DEFAULT_TEMPLATE = {
    'hostname': HOSTNAME_PARAMETER,
    'device_type': DEVICE_TYPE_PARAMETER,
    'connection_command': CONNECTION_COMMAND_PARMETER,
}

# Dictionary with templates of known devices.
KNOWN_TEMPLATES = {
    'panda': {
        'hostname': HOSTNAME_PARAMETER,
        'device_type': Parameter("device_type", depends=HOSTNAME_PARAMETER,
                                 value="panda"),
        'connection_command': CONNECTION_COMMAND_PARMETER,
    },
    'vexpress': {
        'hostname': HOSTNAME_PARAMETER,
        'device_type': Parameter("device_type", depends=HOSTNAME_PARAMETER,
                                 value="vexpress"),
        'connection_command': CONNECTION_COMMAND_PARMETER,
    },
}


def update_template(template, config):
    """Updates a template based on the values from the provided config.

    :param template: A template to be updated.
    :param config: A Config instance where values should be taken.
    """

    # Really make sure.
    assert isinstance(config, Config)

    def update(data):
        """Internal recursive function."""
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
                update(entry)

    update(template)
