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

from copy import copy

from lava.parameter import Parameter

# The hostname parameter is always in the DEFAULT config section.
HOSTNAME_PARAMETER = Parameter("hostname")
DEVICE_TYPE_PARAMETER = Parameter("device_type", depends=HOSTNAME_PARAMETER)
CONNECTION_COMMAND_PARMAETER = Parameter("connection_command",
                                         depends=DEVICE_TYPE_PARAMETER)

DEFAULT_TEMPLATE = {
    'hostname': HOSTNAME_PARAMETER,
    'device_type': DEVICE_TYPE_PARAMETER,
    'connection_command': CONNECTION_COMMAND_PARMAETER,
}

# Specialized copies of the parameters.
# We need this or we might end up asking the user twice the same parameter due
# to different object references when one Parameter depends on a "specialized"
# one, different from the defaults.
PANDA_DEVICE_TYPE = copy(DEVICE_TYPE_PARAMETER)
PANDA_DEVICE_TYPE.value = "panda"
PANDA_DEVICE_TYPE.asked = True

PANDA_CONNECTION_COMMAND = copy(CONNECTION_COMMAND_PARMAETER)
PANDA_CONNECTION_COMMAND.depends = PANDA_DEVICE_TYPE

VEXPRESS_DEVICE_TYPE = copy(DEVICE_TYPE_PARAMETER)
VEXPRESS_DEVICE_TYPE.value = "vexpress"
VEXPRESS_DEVICE_TYPE.asked = True

VEXPRESS_CONNECTION_COMMAND = copy(CONNECTION_COMMAND_PARMAETER)
VEXPRESS_CONNECTION_COMMAND.depends = VEXPRESS_DEVICE_TYPE

QEMU_DEVICE_TYPE = copy(DEVICE_TYPE_PARAMETER)
QEMU_DEVICE_TYPE.value = "qemu"
QEMU_DEVICE_TYPE.asked = True

QEMU_CONNECTION_COMMAND = copy(CONNECTION_COMMAND_PARMAETER)
QEMU_CONNECTION_COMMAND.depends = QEMU_DEVICE_TYPE

# Dictionary with templates of known devices.
KNOWN_TEMPLATES = {
    'panda': {
        'hostname': HOSTNAME_PARAMETER,
        'device_type': PANDA_DEVICE_TYPE,
        'connection_command': PANDA_CONNECTION_COMMAND,
    },
    'vexpress': {
        'hostname': HOSTNAME_PARAMETER,
        'device_type': VEXPRESS_DEVICE_TYPE,
        'connection_command': VEXPRESS_CONNECTION_COMMAND,
    },
    'qemu': {
        'hostname': HOSTNAME_PARAMETER,
        'device_type': QEMU_DEVICE_TYPE,
        'connection_command': QEMU_CONNECTION_COMMAND,
    }
}
