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

import os
import subprocess

from lava.tool.errors import CommandError


def has_command(command):
    """Checks that the given command is available.

    :param command: The name of the command to check availability.
    """
    command_available = True
    try:
        subprocess.check_call(["which", command],
                              stdout=open(os.path.devnull, 'w'))
    except subprocess.CalledProcessError:
        command_available = False
    return command_available


def write_file(path, content):
    """Creates a file with the specified content.

    :param path: The path of the file to write.
    :param content: What to write in the file.
    """
    try:
        with open(path, "w") as to_write:
            to_write.write(content)
    except (OSError, IOError):
        raise CommandError("Error writing file '{0}'".format(path))


def verify_file_extension(path, default, supported):
    """Verifies if a file has a supported extensions.

    If the file does not have one, it will add the default extension
    provided.

    :param path: The path of a file to verify.
    :param default: The default extension to use.
    :param supported: A list of supported extensions to check against.
    :return The path of the file.
    """
    full_path, file_name = os.path.split(path)
    name, extension = os.path.splitext(file_name)
    if not extension:
        path = ".".join([path, default])
    elif extension[1:].lower() not in supported:
        path = os.path.join(full_path, ".".join([name, default]))
    return path


def verify_path_existance(path):
    """Verifies if a given path exists or not on the file system.

    Raises a CommandError in case it exists.

    :param path: The path to verify."""
    if os.path.exists(path):
        raise CommandError("{0} already exists.".format(path))


def retrieve_file(path, extensions):
    """Searches for a file that has one of the supported extensions.

    The path of the first file that matches one of the supported provided
    extensions will be returned. The files are examined in alphabetical
    order.

    :param path: Where to look for the file.
    :param extensions: A list of extensions the file to look for should
                       have.
    :return The full path of the file.
    """
    if os.path.isfile(path):
        if check_valid_extension(path, extensions):
            retrieved_path = path
        else:
            raise CommandError("The provided file '{0}' is not "
                               "valid: extension not supported.".format(path))
    else:
        dir_listing = os.listdir(path)
        dir_listing.sort()

        for element in dir_listing:
            if element.startswith("."):
                continue

            element_path = os.path.join(path, element)
            if os.path.isdir(element_path):
                continue
            elif os.path.isfile(element_path):
                if check_valid_extension(element_path, extensions):
                    retrieved_path = element_path
                    break
        else:
            raise CommandError("No suitable file found in '{0}'".format(path))

    return retrieved_path


def check_valid_extension(path, extensions):
    """Checks that a file has one of the supported extensions.

    :param path: The file to check.
    :param extensions: A list of supported extensions.
    """
    is_valid = False

    local_path, file_name = os.path.split(path)
    name, full_extension = os.path.splittext(file_name)

    if full_extension:
        extension = full_extension[1:].strip().lower()
        if extension in extensions:
            is_valid = True
    return is_valid
