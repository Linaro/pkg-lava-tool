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
Device specific commands class.
"""

import os
import subprocess
import sys
import random
import string

from lava.config import InteractiveConfig
from lava.device import get_known_device
from lava.tool.command import Command, CommandGroup
from lava.tool.errors import CommandError
from lava_tool.utils import has_command

# Default lava-dispatcher paths.
DEFAULT_DISPATCHER_PATH = os.path.join("etc", "lava-dispatcher")
USER_DISPATCHER_PATH = os.path.join(os.path.expanduser("~"), ".config",
                                    "lava-dispatcher")
# Default devices path, has to be joined with the dispatcher path.
DEFAULT_DEVICES_PATH = "devices"
DEVICE_FILE_SUFFIX = "conf"


class device(CommandGroup):
    """LAVA devices handling."""

    namespace = "lava.device.commands"


class BaseCommand(Command):
    """Base command for device commands."""
    def __init__(self, parser, args):
        super(BaseCommand, self).__init__(parser, args)
        self.config = InteractiveConfig(
            force_interactive=self.args.interactive)

    @classmethod
    def register_arguments(cls, parser):
        super(BaseCommand, cls).register_arguments(parser)
        parser.add_argument("-i", "--interactive",
                            action='store_true',
                            help=("Forces asking for input parameters even if "
                                  "we already have them cached."))

    @classmethod
    def _get_dispatcher_paths(cls):
        """Tries to get the dispatcher from lava-dispatcher."""
        try:
            from lava_dispatcher.config import search_path
            return search_path()
        except ImportError:
            raise CommandError("Cannot find lava_dispatcher installation.")

    @classmethod
    def _choose_devices_path(cls, paths):
        """Picks the first path that is writable by the user.

        :param paths: A list of paths.
        :return The first path where it is possible to write.
        """
        valid_path = None
        for path in paths:
            path = os.path.join(path, DEFAULT_DEVICES_PATH)
            if os.path.exists(path):
                try:
                    name = "".join(random.choice(string.ascii_letters)
                                   for x in range(6))
                    open(os.path.join(path, name))
                except IOError:
                    # Cannot write here.
                    continue
                else:
                    valid_path = path
                    os.unlink(name)
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

    @classmethod
    def _get_devices_path(cls):
        """Gets the path to the devices in the LAVA dispatcher."""
        dispatcher_paths = cls._get_dispatcher_paths()
        return cls._choose_devices_path(dispatcher_paths)

    @classmethod
    def edit_config_file(cls, config_file):
        """Opens the specified file with the default file editor.

        :param config_file: The file to edit.
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
                                      "file '{0}'.".format(config_file))
                print >> sys.stdout, ("Either set the 'EDITOR' environment "
                                      "variable, or install 'sensible-editor' "
                                      "or 'xdg-open'.")
                sys.exit(-1)

        try:
            subprocess.Popen([editor, config_file]).wait()
        except Exception:
            raise CommandError("Error opening the file '{0}' with the "
                               "following editor: {1}.".format(config_file,
                                                               editor))

    @classmethod
    def _get_device_file(cls, file_name):
        """Retrieves the config file name specified, if it exists.

        :param file_name: The config file name to search.
        :return The path to the file, or None if it does not exist.
        """
        try:
            from lava_dispatcher.config import get_config_file

            return get_config_file(os.path.join(DEFAULT_DEVICES_PATH,
                                                file_name))
        except ImportError:
            raise CommandError("Cannot find lava_dispatcher installation.")


class add(BaseCommand):
    """Adds a new device."""

    @classmethod
    def register_arguments(cls, parser):
        super(add, cls).register_arguments(parser)
        parser.add_argument("DEVICE", help="The name of the device to add.")

    def invoke(self):
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])

        if self._get_device_file(real_file_name):
            print >> sys.stdout, ("A device configuration file named '{0}' "
                                  "already exists.".format(real_file_name))
            print >> sys.stdout, "Use 'lava device config DEVICE' to edit it."
            sys.exit(-1)

        devices_path = self._get_devices_path()
        device_conf_file = os.path.abspath(os.path.join(devices_path,
                                                        real_file_name))

        device = get_known_device(self.args.DEVICE)
        device.write(device_conf_file)

        print >> sys.stdout, ("Created device file '{0}' in: {1}".format(
            self.args.DEVICE, devices_path))
        self.edit_config_file(device_conf_file)


class remove(BaseCommand):
    """Removes the specified device."""

    @classmethod
    def register_arguments(cls, parser):
        super(remove, cls).register_arguments(parser)
        parser.add_argument("DEVICE",
                            help="The name of the device to remove.")

    def invoke(self):
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])
        device_conf = self._get_device_file(real_file_name)

        if device_conf:
            try:
                os.remove(device_conf)
                print >> sys.stdout, ("Device configuration file '{0}'' "
                                      "removed.".format(real_file_name))
            except OSError:
                raise CommandError("Cannot remove file '{0}' at: {1}.".format(
                    real_file_name, os.path.dirname(device_conf)))
        else:
            print >> sys.stdout, ("No device configuration file '{0}'' "
                                  "found.".format(real_file_name))


class config(BaseCommand):
    """Opens the specified device config file."""
    @classmethod
    def register_arguments(cls, parser):
        super(config, cls).register_arguments(parser)
        parser.add_argument("DEVICE",
                            help="The name of the device to edit.")

    def invoke(self):
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])

        device_conf = self._get_device_file(real_file_name)
        if device_conf:
            self.edit_config_file(device_conf)
        else:
            raise CommandError("Cannot edit file '{0}' at: {1}. It does not "
                               "exist or it is not a "
                               "file.".format(real_file_name,
                                              os.path.dirname(device_conf)))
