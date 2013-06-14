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

"""Base command class common to lava commands series."""

from lava.config import InteractiveConfig
from lava.tool.command import Command
from lava.tool.errors import CommandError


class BaseCommand(Command):
    """Base command class for all lava commands."""
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
    def get_dispatcher_paths(cls):
        """Tries to get the dispatcher paths from lava-dispatcher.

        :return A list of paths.
        """
        try:
            from lava_dispatcher.config import write_path
            return write_path()
        except ImportError:
            raise CommandError("Cannot find lava-dispatcher installation.")

    @classmethod
    def get_devices(cls):
        """Gets the devices list from the dispatcher.

        :return A list of DeviceConfig.
        """
        try:
            from lava_dispatcher.config import get_devices
            return get_devices()
        except ImportError:
            raise CommandError("Cannot find lava-dispatcher installation.")
