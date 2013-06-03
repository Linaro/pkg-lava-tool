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

from os.path import exists

from lava.config import InteractiveConfig
from lava.job import Job
from lava.job.templates import *
from lava.tool.command import Command, CommandGroup
from lava.tool.errors import CommandError

from lava_tool.authtoken import AuthenticatingServerProxy, KeyringAuthBackend
import xmlrpclib

class job(CommandGroup):
    """
    LAVA job file handling
    """

    namespace = 'lava.job.commands'

class BaseCommand(Command):

    def __init__(self, parser, args):
        super(BaseCommand, self).__init__(parser, args)
        self.config = InteractiveConfig(force_interactive=self.args.interactive)

    @classmethod
    def register_arguments(cls, parser):
        super(BaseCommand, cls).register_arguments(parser)
        parser.add_argument(
            "-i", "--interactive",
            action='store_true',
            help=("Forces asking for input parameters even if we already "
                  "have them cached."))

class new(BaseCommand):

    @classmethod
    def register_arguments(cls, parser):
        super(new, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("Job file to be created."))

    def invoke(self):
        if exists(self.args.FILE):
            raise CommandError('%s already exists' % self.args.FILE)

        with open(self.args.FILE, 'w') as f:
            job = Job(BOOT_TEST)
            job.fill_in(self.config)
            job.write(f)


class submit(BaseCommand):
    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("The job file to submit"))

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
            print "Job submitted with job ID %d" % job_id
        except xmlrpclib.Fault, e:
            raise CommandError(str(e))

class run(BaseCommand):
    def invoke(self):
        print("hello world")
