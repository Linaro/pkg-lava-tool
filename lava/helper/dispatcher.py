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

"""Classes and functions to interact with the lava-dispatcher."""

import random
import string
import os

from lava.tool.errors import CommandError

# Default devices path, has to be joined with the dispatcher path.
DEFAULT_DEVICES_PATH = "devices"


def get_dispatcher_paths():
    """Tries to get the dispatcher paths from lava-dispatcher.

    :return A list of paths.
    """
    try:
        from lava_dispatcher.config import write_path
        return write_path()
    except ImportError:
        raise CommandError("Cannot find lava-dispatcher installation.")


def get_devices():
    """Gets the devices list from the dispatcher.

    :return A list of DeviceConfig.
    """
    try:
        from lava_dispatcher.config import get_devices
        return get_devices()
    except ImportError:
        raise CommandError("Cannot find lava-dispatcher installation.")


def get_device_file(file_name):
    """Retrieves the config file name specified, if it exists.

    :param file_name: The config file name to search.
    :return The path to the file, or None if it does not exist.
    """
    try:
        from lava_dispatcher.config import get_config_file
        return get_config_file(os.path.join(DEFAULT_DEVICES_PATH,
                                            file_name))
    except ImportError:
        raise CommandError("Cannot find lava-dispatcher installation.")


def choose_devices_path(paths):
    """Picks the first path that is writable by the user.

    :param paths: A list of paths.
    :return The first path where it is possible to write.
    """
    valid_path = None
    for path in paths:
        path = os.path.join(path, DEFAULT_DEVICES_PATH)
        if os.path.exists(path):
            name = "".join(random.choice(string.ascii_letters)
                           for x in range(6))
            test_file = os.path.join(path, name)
            try:
                fp = open(test_file, 'a')
                fp.close()
            except IOError:
                # Cannot write here.
                continue
            else:
                valid_path = path
                if os.path.isfile(test_file):
                    os.unlink(test_file)
                break
        else:
            try:
                os.makedirs(path)
            except OSError:
                # Cannot write here either.
                continue
            else:
                valid_path = path
                break
    else:
        raise CommandError("Insufficient permissions to create new "
                           "devices.")
    return valid_path


def get_devices_path():
    """Gets the path to the devices in the LAVA dispatcher."""
    return choose_devices_path(get_dispatcher_paths())
