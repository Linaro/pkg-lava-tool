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
        global_paths = []
        try:
            from lava_dispatcher.config import search_path

            global_paths += search_path()
        except ImportError:
            print >> sys.stderr, "Cannot import lava_dispatcher."
        return global_paths

    @classmethod
    def _choose_dispatcher_path(cls, paths):
        """Lets the user choose the path to use.

        :param paths: A list of paths.
        :return The path at the user selected index.
        """
        print >> sys.stdout, ("Multiple dispatcher paths found. Please "
                              "select one between:\n")
        out_list = []
        len_paths = range(1, len(paths) + 1)
        for index, dispatcher_path in zip(len_paths, paths):
            out_list.append("\t{0}. {1}\n".format(index, dispatcher_path))
        print >> sys.stdout, "".join(out_list)
        while True:
            try:
                choice = raw_input("Dispatcher path to use: ").strip()
                if choice in [str(x) for x in len_paths]:
                    return paths[int(choice) - 1]
                else:
                    continue
            except KeyboardInterrupt:
                sys.exit(-1)

    @classmethod
    def _get_devices_path(cls):
        """Gets the path to the devices in the LAVA dispatcher."""
        dispatcher_paths = cls._get_dispatcher_paths()
        # Can't get anything out of lava-dispatcher, guess something.
        if not dispatcher_paths:
            dispatcher_paths.append(USER_DISPATCHER_PATH)
            if "VIRTUAL_ENV" in os.environ:
                system_dispatcher_path = os.path.join(
                    os.environ["VIRTUAL_ENV"],
                    DEFAULT_DISPATCHER_PATH)
            else:
                system_dispatcher_path = os.path.join("/",
                                                      DEFAULT_DISPATCHER_PATH)
            dispatcher_paths.append(system_dispatcher_path)

        if len(dispatcher_paths) > 1:
            devices_path = os.path.join(
                cls._choose_dispatcher_path(dispatcher_paths),
                DEFAULT_DEVICES_PATH)
        else:
            devices_path = os.path.join(dispatcher_paths[0],
                                        DEFAULT_DEVICES_PATH)

        cls._create_devices_path(devices_path)

        return devices_path

    @classmethod
    def _create_devices_path(cls, devices_path):
        """Checks and creates the path on file system.

        :param devices_path: The path to check and create.
        """
        if not os.path.exists(devices_path):
            try:
                os.makedirs(devices_path)
            except OSError:
                raise CommandError("Cannot create path "
                                   "{0}.".format(devices_path))

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
                print ("Cannot find an editor to open the "
                       "file '{0}'.".format(config_file))
                print ("Either set the 'EDITOR' environment variable, or "
                       "install 'sensible-editor' or 'xdg-open'.")
                sys.exit(-1)

        try:
            cmd_args = [editor, config_file]
            subprocess.Popen(cmd_args).wait()
        except Exception:
            raise CommandError("Error opening the file '{0}' with the "
                               "following editor: {1}.".format(config_file,
                                                               editor))


class add(BaseCommand):
    """Adds a new device."""

    @classmethod
    def register_arguments(cls, parser):
        super(add, cls).register_arguments(parser)
        parser.add_argument("DEVICE", help="The name of the device to add.")

    def invoke(self):
        devices_path = self._get_devices_path()
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])
        device_conf_file = os.path.abspath(os.path.join(devices_path,
                                                        real_file_name))

        if os.path.exists(device_conf_file):
            print ("A device configuration file named '{0}' already "
                   "exists.".format(real_file_name))
            print "Use 'lava device config DEVICE' to edit it."
            sys.exit(-1)

        device = get_known_device(self.args.DEVICE)
        device.write(device_conf_file)

        print ("Created device file '{0}' in: {1}".format(self.args.DEVICE,
                                                          devices_path))
        self.edit_config_file(device_conf_file)


class remove(BaseCommand):
    """Removes the specified device."""

    @classmethod
    def register_arguments(cls, parser):
        super(remove, cls).register_arguments(parser)
        parser.add_argument("DEVICE",
                            help="The name of the device to remove.")

    def invoke(self):
        devices_path = self._get_devices_path()
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])
        device_conf = os.path.join(devices_path, real_file_name)
        if os.path.isfile(device_conf):
            os.remove(device_conf)
            print ("Device configuration file {0} "
                   "removed.".format(self.args.DEVICE))
        else:
            raise CommandError("Cannot remove file '{0}' at: {1}. It does not "
                               "exist or it is not a "
                               "file.".format(real_file_name, devices_path))


class config(BaseCommand):
    """Opens the specified device config file."""
    @classmethod
    def register_arguments(cls, parser):
        super(config, cls).register_arguments(parser)
        parser.add_argument("DEVICE",
                            help="The name of the device to edit.")

    def invoke(self):
        devices_path = self._get_devices_path()
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])
        device_conf = os.path.join(devices_path, real_file_name)
        if os.path.isfile(device_conf):
            self.edit_config_file(device_conf)
        else:
            raise CommandError("Cannot edit file '{0}' at: {1}. It does not "
                               "exist or it is not a "
                               "file.".format(real_file_name, devices_path))
