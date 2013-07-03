# Copyright (C) 2013 Linaro Limited
#
# Author: Antonio Terceiro <antonio.terceiro@linaro.org>
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
LAVA job commands.
"""

import os
import sys
import xmlrpclib

from lava.helper.command import BaseCommand
from lava.helper.dispatcher import get_devices

from lava.job import Job
from lava.job.templates import (
    LAVA_TEST_SHELL,
)
from lava.parameter import Parameter
from lava.tool.command import CommandGroup
from lava.tool.errors import CommandError
from lava_tool.authtoken import AuthenticatingServerProxy, KeyringAuthBackend
from lava_tool.utils import has_command


class job(CommandGroup):
    """LAVA job file handling."""
    namespace = 'lava.job.commands'


class new(BaseCommand):
    """Creates a new job file."""

    @classmethod
    def register_arguments(cls, parser):
        super(new, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("Job file to be created."))

    def invoke(self):
        if os.path.exists(self.args.FILE):
            raise CommandError('{0} already exists.'.format(self.args.FILE))

        with open(self.args.FILE, 'w') as job_file:
            job_instance = Job(LAVA_TEST_SHELL)
            job_instance.fill_in(self.config)
            job_instance.write(job_file)


class submit(BaseCommand):
    """Submits the specified job file."""

    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("The job file to submit."))

    def invoke(self):
        jobfile = self.args.FILE
        jobdata = open(jobfile, 'rb').read()

        server_name = Parameter('server')
        rpc_endpoint = Parameter('rpc_endpoint', depends=server_name)
        self.config.get(server_name)
        endpoint = self.config.get(rpc_endpoint)

        server = AuthenticatingServerProxy(endpoint,
                                           auth_backend=KeyringAuthBackend())
        try:
            job_id = server.scheduler.submit_job(jobdata)
            print >> sys.stdout, "Job submitted with job ID {0}".format(job_id)
        except xmlrpclib.Fault, exc:
            raise CommandError(str(exc))


class run(BaseCommand):
    """Runs the specified job file on the local dispatcher."""

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("The job file to submit."))

    @classmethod
    def _choose_device(cls, devices):
        """Let the user choose the device to use.

        :param devices: The list of available devices.
        :return The selected device.
        """
        devices_len = len(devices)
        output_list = []
        for device, number in zip(devices, range(1, devices_len + 1)):
            output_list.append("\t{0}. {1}\n".format(number, device.hostname))

        print >> sys.stdout, ("More than one local device found. "
                              "Please choose one:\n")
        print >> sys.stdout, "".join(output_list)

        while True:
            try:
                user_input = raw_input("Device number to use: ").strip()

                if user_input in [str(x) for x in range(1, devices_len + 1)]:
                    return devices[int(user_input) - 1].hostname
                else:
                    continue
            except EOFError:
                user_input = None
            except KeyboardInterrupt:
                sys.exit(-1)

    def invoke(self):
        if os.path.isfile(self.args.FILE):
            if has_command("lava-dispatch"):
                devices = get_devices()
                if devices:
                    if len(devices) > 1:
                        device = self._choose_device(devices)
                    else:
                        device = devices[0].hostname
                    self.run(["lava-dispatch", "--target", device,
                              self.args.FILE])
            else:
                raise CommandError("Cannot find lava-dispatcher installation.")
        else:
            raise CommandError("The file '{0}' does not exists. or is not "
                               "a file.".format(self.args.FILE))
