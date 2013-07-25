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
import urlparse

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
        parser.add_argument("--non-interactive", "-n",
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

        server_url = self.config.get(server_name_parameter)
        endpoint = self.config.get(rpc_endpoint_parameter)

        rpc_url = self.verify_and_create_url(server_url, endpoint)
        server = AuthenticatingServerProxy(rpc_url,
                                           auth_backend=KeyringAuthBackend())
        return server

    @classmethod
    def verify_and_create_url(cls, server, endpoint=""):
        """Checks that the provided values make a correct URL.

        If the server address does not contain a scheme, by default it will use
        HTTPS.
        The endpoint is then added at the URL.
        """
        scheme, netloc, path, params, query, fragment = \
            urlparse.urlparse(server)
        if not scheme:
            scheme = "https"
        if not netloc:
            netloc, path = path, ""

        if endpoint:
            if not netloc[-1:] == "/" and not endpoint[0] == "/":
                netloc += "/"
            if not endpoint[-1:] == "/":
                endpoint += "/"
            netloc += endpoint

        return urlparse.urlunparse(
            (scheme, netloc, path, params, query, fragment))

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
            job_file = path
        else:
            dir_listing = os.listdir(path)
            dir_listing.sort()

            for element in dir_listing:
                element_path = os.path.join(path, element)
                if os.path.isdir(element_path):
                    continue
                elif os.path.isfile(element_path):
                    job_file = os.path.split(element)[1]
                    # Extension here contains also the leading dot.
                    full_extension = os.path.splitext(job_file)[1]

                    if full_extension:
                        # Make sure that we have a supported extension.
                        extension = full_extension[1:].strip().lower()
                        if extension in extensions:
                            job_file = element_path
                            break
            else:
                raise CommandError("No job file found in: '{0}'".format(path))

        return job_file

    @classmethod
    def verify_file_extension(cls, path, default, supported):
        """Verifies if a file has a supported extensions.

        If the file does not have one, it will add the default extension
        provided.

        :param path: The path of a file to verify.
        :param default: The default extension to use.
        :param supported: A list of supported extension to check the file one
                          against.
        :return The path of the file.
        """
        full_path, file_name = os.path.split(path)
        name, extension = os.path.splitext(file_name)
        if not extension:
            path = ".".join([path, default])
        elif extension[1:].lower() not in supported:
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
