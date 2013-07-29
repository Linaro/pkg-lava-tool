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
import sys

from lava.device import get_known_device
from lava.helper.command import (
    BaseCommand,
)
from lava.helper.dispatcher import (
    get_device_file,
    get_devices_path,
)
from lava.tool.command import CommandGroup
from lava.tool.errors import CommandError
from lava_tool.utils import (
    can_edit_file,
    edit_file,
)

DEVICE_FILE_SUFFIX = "conf"


class device(CommandGroup):
    """LAVA devices handling."""

    namespace = "lava.device.commands"


class add(BaseCommand):
    """Adds a new device."""

    @classmethod
    def register_arguments(cls, parser):
        super(add, cls).register_arguments(parser)
        parser.add_argument("DEVICE", help="The name of the device to add.")

    def invoke(self):
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])

        if get_device_file(real_file_name) is not None:
            print >> sys.stdout, ("A device configuration file named '{0}' "
                                  "already exists.".format(real_file_name))
            print >> sys.stdout, ("Use 'lava device config {0}' to edit "
                                  "it.".format(self.args.DEVICE))
            sys.exit(-1)

        devices_path = get_devices_path()
        device_conf_file = os.path.abspath(os.path.join(devices_path,
                                                        real_file_name))

        device = get_known_device(self.args.DEVICE)
        device.update(self.config)
        device.write(device_conf_file)

        print >> sys.stdout, ("Created device file '{0}' in: {1}".format(
            real_file_name, devices_path))
        edit_file(device_conf_file)


class remove(BaseCommand):
    """Removes the specified device."""

    @classmethod
    def register_arguments(cls, parser):
        super(remove, cls).register_arguments(parser)
        parser.add_argument("DEVICE",
                            help="The name of the device to remove.")

    def invoke(self):
        real_file_name = ".".join([self.args.DEVICE, DEVICE_FILE_SUFFIX])
        device_conf = get_device_file(real_file_name)

        if device_conf:
            try:
                os.remove(device_conf)
                print >> sys.stdout, ("Device configuration file '{0}' "
                                      "removed.".format(real_file_name))
            except OSError:
                raise CommandError("Cannot remove file '{0}' at: {1}.".format(
                    real_file_name, os.path.dirname(device_conf)))
        else:
            print >> sys.stdout, ("No device configuration file '{0}' "
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
        device_conf = get_device_file(real_file_name)

        if device_conf and can_edit_file(device_conf):
            edit_file(device_conf)
        else:
            raise CommandError("Cannot edit file '{0}'".format(real_file_name))
