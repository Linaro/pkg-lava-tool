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
from lava.parameter import Parameter
from lava.tool.command import Command
from lava.tool.errors import CommandError
from lava_tool.authtoken import (
    AuthenticatingServerProxy,
    KeyringAuthBackend
)
from lava_tool.utils import has_command

# Name of the config value to store the job ids.
JOBS_ID = "jobs_id"
# Name of the config value to store the LAVA server URL.
SERVER = "server"
# Name of the config value to store the LAVA rpc_endpoint.
RPC_ENDPOINT = "rpc_endpoint"


class BaseCommand(Command):

    """Base command class for all lava commands."""

    def __init__(self, parser, args):
        super(BaseCommand, self).__init__(parser, args)
        self.config = InteractiveConfig(
            force_interactive=self.args.non_interactive)

    @classmethod
    def register_arguments(cls, parser):
        super(BaseCommand, cls).register_arguments(parser)
        parser.add_argument("--non-interactive",
                            action='store_false',
                            help=("Do not ask for input parameters."))

    def authenticated_server(self):
        """Returns a connection to a LAVA server.

        It will ask the user the necessary parameters to establish the
        connection.
        """
        server_name_parameter = Parameter(SERVER)
        rpc_endpoint_parameter = Parameter(RPC_ENDPOINT,
                                           depends=server_name_parameter)
        self.config.get(server_name_parameter)
        endpoint = self.config.get(rpc_endpoint_parameter)

        server = AuthenticatingServerProxy(endpoint,
                                           auth_backend=KeyringAuthBackend())
        return server

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
    def retrieve_file(cls, path, extensions):
        """Searches for a job file in the provided path.

        :return The job file full path.
        """
        if os.path.isfile(path):
            job_file = path
        else:
            for element in os.listdir(path):
                element_path = os.path.join(path, element)
                if os.path.isdir(element_path):
                    continue
                elif os.path.isfile(element_path):
                    job_file = os.path.split(element)[1]
                    # Extension here contains also the leading dot.
                    full_extension = os.path.splitext(job_file)[1]

                    if full_extension:
                        # Make sure that we have an extension and remove the
                        # dot.
                        extension = full_extension[1:].strip().lower()
                        if extension in extensions:
                            job_file = element_path
                            break
            else:
                raise CommandError("No job file found in: '{0}'".format(path))

        return job_file

    @classmethod
    def verify_file_extension(cls, path, default, supported):
        # Checks that the file we pass has an extension or a correct one.
        # If not, it adds the provided one.
        full_path, file_name = os.path.split(path)
        name, extension = os.path.splitext(file_name)
        if not extension:
            path = ".".join([path, default])
        elif extension[1:] not in supported:
            path = os.path.join(full_path, ".".join([name, default]))
        return path

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
