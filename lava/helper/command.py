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
import sys
import xmlrpclib

from lava.config import InteractiveConfig
from lava.helper.dispatcher import get_devices
from lava.parameter import (
    Parameter,
    SingleChoiceParameter,
)
from lava.tool.command import Command
from lava.tool.errors import CommandError
from lava_tool.authtoken import (
    AuthenticatingServerProxy,
    KeyringAuthBackend
)
from lava_tool.utils import (
    has_command,
    verify_and_create_url,
    create_tar,
    base64_encode,
)
from lava.job import Job
from lava.job.templates import (
    LAVA_TEST_SHELL_TAR_REPO,
    LAVA_TEST_SHELL_TAR_REPO_KEY,
    LAVA_TEST_SHELL_TESDEF_KEY,
)

from lava.testdef import TestDefinition
from lava.testdef.templates import (
    TESTDEF_TEMPLATE,
)
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
        server_name_parameter = Parameter("server")
        rpc_endpoint_parameter = Parameter("rpc_endpoint",
                                           depends=server_name_parameter)

        server_url = self.config.get(server_name_parameter)
        endpoint = self.config.get(rpc_endpoint_parameter)

        rpc_url = verify_and_create_url(server_url, endpoint)
        server = AuthenticatingServerProxy(rpc_url,
                                           auth_backend=KeyringAuthBackend())
        return server

    def submit(self, job_file):
        """Submits a job file to a LAVA server.

        :param job_file: The job file to submit.
        :return The job ID on success.
        """
        if os.path.isfile(job_file):
            try:
                jobdata = open(job_file, 'rb').read()
                server = self.authenticated_server()

                job_id = server.scheduler.submit_job(jobdata)
                print >> sys.stdout, ("Job submitted with job "
                                      "ID {0}.".format(job_id))

                return job_id
            except xmlrpclib.Fault, exc:
                raise CommandError(str(exc))
        else:
            raise CommandError("Job file '{0}' does not exists, or is not "
                               "a file.".format(job_file))

    def run(self, job_file):
        """Runs a job file on the local LAVA dispatcher.

        :param job_file: The job file to run.
        """
        if os.path.isfile(job_file):
            if has_command("lava-dispatch"):
                devices = get_devices()
                if devices:
                    if len(devices) > 1:
                        device_names = [device.hostname for device in devices]
                        device_param = SingleChoiceParameter("device",
                                                             device_names)
                        device = device_param.prompt("Device to use: ")
                    else:
                        device = devices[0].hostname
                    self.execute(
                        ["lava-dispatch", "--target", device, job_file])
            else:
                raise CommandError("Cannot find lava-dispatcher installation.")
        else:
            raise CommandError("Job file '{0}' does not exists, or it is not "
                               "a file.".format(job_file))

    def status(self, job_id):
        """Retrieves the status of a LAVA job.

        :param job_id: The ID of the job to look up.
        """
        job_id = str(job_id)

        try:
            server = self.authenticated_server()
            job_status = server.scheduler.job_status(job_id)

            status = job_status["job_status"].lower()
            bundle = job_status["bundle_sha1"]

            print >> sys.stdout, "\nJob id: {0}".format(job_id)
            print >> sys.stdout, ("Status: {0}".format(status))
            print >> sys.stdout, ("Bundle: {0}".format(bundle))
        except xmlrpclib.Fault, exc:
            raise CommandError(str(exc))

    def create_tar_repo_job(self, job_file, testdef_file, tar_content):
        """Creates a job file based on the tar-repo template.

        The tar repo is not kept on the file system.

        :param job_file: The path of the job file to create.
        :param testdef_file: The path of the test definition file.
        :param tar_content: What should go into the tarball repository.
        :return The path of the job file created.
        """
        try:
            tar_repo = create_tar(tar_content)

            job_instance = Job(LAVA_TEST_SHELL_TAR_REPO, job_file)
            job_instance.update(self.config)

            job_instance.set(LAVA_TEST_SHELL_TAR_REPO_KEY,
                             base64_encode(tar_repo))
            job_instance.set(LAVA_TEST_SHELL_TESDEF_KEY,
                             os.path.basename(testdef_file))

            job_instance.write()

            return job_instance.file_name
        finally:
            if os.path.isfile(tar_repo):
                os.unlink(tar_repo)

    def create_test_definition(self, testdef_file, template=TESTDEF_TEMPLATE):
        """Creates a test definition YAML file.

        :param testdef_file: The file to create.
        :return The path of the file created.
        """
        testdef = TestDefinition(template, testdef_file)
        testdef.update(self.config)
        testdef.write()

        print >> sys.stdout, ("Create test definition "
                              "'{0}'.".format(testdef.file_name))

        return testdef.file_name
