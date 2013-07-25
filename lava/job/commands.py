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
    BOOT_TEST_KEY,
    JOB_TYPES,
)
from lava.parameter import (
    SingleChoiceParameter,
)
from lava.tool.command import CommandGroup
from lava.tool.errors import CommandError
from lava_tool.utils import (
    has_command,
)


class job(CommandGroup):
    """LAVA job file handling."""
    namespace = 'lava.job.commands'


class new(BaseCommand):
    """Creates a new job file."""

    @classmethod
    def register_arguments(cls, parser):
        super(new, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("Job file to be created."))
        parser.add_argument("--type",
                            help="The type of job to create.",
                            choices=JOB_TYPES.keys(),
                            default=BOOT_TEST_KEY)

    def invoke(self, job_template=None):
        if not job_template:
            job_template = JOB_TYPES.get(self.args.type)

        full_path = os.path.abspath(self.args.FILE)

        job_instance = Job(job_template, full_path)
        job_instance.update(self.config)
        job_instance.write()


class submit(BaseCommand):
    """Submits the specified job file."""

    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("The job file to submit."))

    def invoke(self):
        try:
            jobfile = self.args.FILE
            jobdata = open(jobfile, 'rb').read()

            server = self.authenticated_server()

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
        if os.path.isfile(self.args.FILE):
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
                    self.run(["lava-dispatch", "--target", device,
                              self.args.FILE])
            else:
                raise CommandError("Cannot find lava-dispatcher installation.")
        else:
            raise CommandError("The file '{0}' does not exists, or it is not "
                               "a file.".format(self.args.FILE))


class status(BaseCommand):

    """Retrieves the status of a job."""

    @classmethod
    def register_arguments(cls, parser):
        super(status, cls).register_arguments(parser)
        parser.add_argument("JOB_ID",
                            help=("Prints status information about the "
                                  "provided job id."),
                            nargs="?",
                            default="-1")

    def invoke(self):
        job_id = str(self.args.JOB_ID)

        try:
            server = self.authenticated_server()
            job_status = server.scheduler.job_status(job_id)

            status = job_status["job_status"].lower()
            bundle = job_status["bundle_sha1"]

            print >> sys.stdout, "\nJob id: {0}".format(job_id)
            print >> sys.stdout, "Status: {0}".format(status)
            print >> sys.stdout, "Bundle: {0}".format(bundle)
        except xmlrpclib.Fault, exc:
            raise CommandError(str(exc))
