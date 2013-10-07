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

import StringIO
import base64
import os
import tarfile
import tempfile
import types
import subprocess
import sys
import urlparse

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


def to_list(value):
    """Return a list from the passed value.

    :param value: The parameter to turn into a list.
    """
    return_value = []
    if isinstance(value, types.StringType):
        return_value = [value]
    else:
        return_value = list(value)
    return return_value


def create_tar(paths):
    """Creates a temporary tar file with the provided paths.

    The tar file is not deleted at the end, it has to be delete by who calls
    this function.

    If just a directory is passed, it will be flattened out: its contents will
    be added, but not the directory itself.

    :param paths: List of paths to be included in the tar archive.
    :type list
    :return The path to the temporary tar file.
    """
    paths = to_list(paths)
    try:
        temp_tar_file = tempfile.NamedTemporaryFile(suffix=".tar",
                                                    delete=False)
        with tarfile.open(temp_tar_file.name, "w") as tar_file:
            for path in paths:
                full_path = os.path.abspath(path)
                if os.path.isfile(full_path):
                    arcname = os.path.basename(full_path)
                    tar_file.add(full_path, arcname=arcname)
                elif os.path.isdir(full_path):
                    # If we pass a directory, flatten it out.
                    # List its contents, and add them as they are.
                    for element in os.listdir(full_path):
                        arcname = element
                        tar_file.add(os.path.join(full_path, element),
                                     arcname=arcname)
        return temp_tar_file.name
    except tarfile.TarError:
        raise CommandError("Error creating the temporary tar archive.")


def base64_encode(path):
    """Encode in base64 the provided file.

    :param path: The path to a file.
    :return The file content encoded in base64.
    """
    if os.path.isfile(path):
        encoded_content = StringIO.StringIO()

        try:
            with open(path) as read_file:
                base64.encode(read_file, encoded_content)

            return encoded_content.getvalue().strip()
        except IOError:
            raise CommandError("Cannot read file "
                               "'{0}'.".format(path))
    else:
        raise CommandError("Provided path does not exists or is not a file: "
                           "{0}.".format(path))


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
    name, full_extension = os.path.splitext(file_name)

    if full_extension:
        extension = full_extension[1:].strip().lower()
        if extension in extensions:
            is_valid = True
    return is_valid


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
    """Verifies if a given path exists on the file system.

    Raises a CommandError in case it exists.

    :param path: The path to verify.
    """
    if os.path.exists(path):
        raise CommandError("{0} already exists.".format(path))


def verify_path_non_existance(path):
    """Verifies if a given path does not exist on the file system.

    Raises a CommandError in case it does not exist.

    :param path: The path to verify.
    """
    if not os.path.exists(path):
        raise CommandError("{0} does not exists.".format(path))


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


def execute(cmd_args):
    """Executes the supplied command args.

    :param cmd_args: The command, and its optional arguments, to run.
    :return The command execution return code.
    """
    cmd_args = to_list(cmd_args)
    try:
        return subprocess.check_call(cmd_args)
    except subprocess.CalledProcessError:
        raise CommandError("Error running the following command: "
                           "{0}".format(" ".join(cmd_args)))


def can_edit_file(path):
    """Checks if a file can be opend in write mode.

    :param path: The path to the file.
    :return True if it is possible to write on the file, False otherwise.
    """
    can_edit = True
    try:
        fp = open(path, "a")
        fp.close()
    except IOError:
        can_edit = False
    return can_edit


def edit_file(file_to_edit):
    """Opens the specified file with the default file editor.

    :param file_to_edit: The file to edit.
    """
    editor = os.environ.get("EDITOR", None)
    if editor is None:
        if has_command("sensible-editor"):
            editor = "sensible-editor"
        elif has_command("xdg-open"):
            editor = "xdg-open"
        else:
            # We really do not know how to open a file.
            print >> sys.stdout, ("Cannot find an editor to open the "
                                  "file '{0}'.".format(file_to_edit))
            print >> sys.stdout, ("Either set the 'EDITOR' environment "
                                  "variable, or install 'sensible-editor' "
                                  "or 'xdg-open'.")
            sys.exit(-1)
    try:
        subprocess.Popen([editor, file_to_edit]).wait()
    except Exception:
        raise CommandError("Error opening the file '{0}' with the "
                           "following editor: {1}.".format(file_to_edit,
                                                           editor))


def verify_and_create_url(endpoint):
    """Checks that the provided values make a correct URL.

    If the server address does not contain a scheme, by default it will use
    HTTPS.
    The endpoint is then added at the URL.

    :param server: A server URL to verify.
    :return A URL.
    """
    url = ""
    if endpoint:
        scheme, netloc, path, params, query, fragment = \
            urlparse.urlparse(endpoint)
        if not scheme:
            scheme = "https"
        if not netloc:
            netloc, path = path, ""

        url = urlparse.urlunparse(
            (scheme, netloc, path, params, query, fragment))

        if url[-1:] != "/":
            url += "/"

    return url


def create_dir(path, dir_name=None):
    """Checks if a directory does not exists, and creates it.

    :param path: The path where the directory should be created.
    :param dir_name: An optional name for a directory to be created at
                     path (dir_name will be joined with path).
    :return The path of the created directory."""
    created_dir = path
    if dir_name:
        created_dir = os.path.join(path, dir_name)

    if not os.path.isdir(created_dir):
        try:
            os.makedirs(created_dir)
        except OSError:
            raise CommandError("Cannot create directory "
                               "'{0}'.".format(created_dir))
    return created_dir
