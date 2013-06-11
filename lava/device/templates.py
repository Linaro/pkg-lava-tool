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

DEFAULT_TEMPLATE = {
    'device_type': None,
    'hostname': None,
    'connection_command': None,
}

PANDA_TEMPLATE = DEFAULT_TEMPLATE.copy()
PANDA_TEMPLATE.update(device_type='panda')

VEXPRESS_TEMPLATE = DEFAULT_TEMPLATE.copy()
VEXPRESS_TEMPLATE.update(device_type='vexpress')

# Dictionary with templates of known devices.
KNOWN_TEMPLATES = {
    'panda': PANDA_TEMPLATE,
    'vexpress': VEXPRESS_TEMPLATE,
}
