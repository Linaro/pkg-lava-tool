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

from lava.base_command import BaseCommand

from lava.config import Parameter
from lava.job import Job
from lava.job.templates import (
    BOOT_TEST,
)
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

        with open(self.args.FILE, 'w') as f:
            job_instance = Job(BOOT_TEST)
            job_instance.fill_in(self.config)
            job_instance.write(f)


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

    def invoke(self):
        if has_command("lava-dispatch"):
            devices = self.get_devices()
            if len(devices) > 1:
                pass
            else:
                print >> sys.stdout, "Invoking"
        else:
            raise CommandError("Cannot find lava-dispatcher installation.")
