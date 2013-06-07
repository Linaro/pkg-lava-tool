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

import subprocess


def has_command(command):
    """Checks that the given command is available.

    :param command: The name of the command to check availability.
    """
    command_available = True
    try:
        cmd_args = ["which", command]
        process = subprocess.Popen(cmd_args, stdout=open('/dev/null', 'w'))
        process.wait()
        if process.returncode != 0:
            command_available = False
    except subprocess.CalledProcessError:
        # TODO: logging infrastructure?
        command_available = False
    return command_available
