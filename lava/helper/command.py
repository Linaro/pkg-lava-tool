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

import os
import subprocess
import sys
import types

from lava.config import InteractiveConfig
from lava.tool.command import Command
from lava.tool.errors import CommandError
from lava_tool.utils import has_command

CONFIG = InteractiveConfig()


class BaseCommand(Command):

    """Base command class for all lava commands."""

    def __init__(self, parser, args):
        super(BaseCommand, self).__init__(parser, args)
        self.config = CONFIG
        self.config.force_interactive = self.args.non_interactive

    @classmethod
    def register_arguments(cls, parser):
        super(BaseCommand, cls).register_arguments(parser)
        parser.add_argument("--non-interactive",
                            action='store_false',
                            help=("Do not ask for input parameters."))

    @classmethod
    def can_edit_file(cls, conf_file):
        """Checks if a file can be opend in write mode.

        :param conf_file: The path to the file.
        :return True if it is possible to write on the file, False otherwise.
        """
        can_edit = True
        try:
            fp = open(conf_file, "a")
            fp.close()
        except IOError:
            can_edit = False
        return can_edit

    @classmethod
    def edit_file(cls, file_to_edit):
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

    @classmethod
    def run(cls, cmd_args):
        """Runs the supplied command args.

        :param cmd_args: The command, and its optional arguments, to run.
        :return The command execution return code.
        """
        if isinstance(cmd_args, types.StringTypes):
            cmd_args = [cmd_args]
        else:
            cmd_args = list(cmd_args)
        try:
            return subprocess.check_call(cmd_args)
        except subprocess.CalledProcessError:
            raise CommandError("Error running the following command: "
                               "{0}".format(" ".join(cmd_args)))
