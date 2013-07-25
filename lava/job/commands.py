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

from lava.helper.command import BaseCommand
from lava.job import Job
from lava.job.templates import (
    BOOT_TEST_KEY,
    JOB_TYPES,
)
from lava.tool.command import CommandGroup
from lava.tool.errors import CommandError


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
                            help=("The type of job to create. Defaults to "
                                  "'{0}'.".format(BOOT_TEST_KEY)),
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
        super(submit, self).submit(self.args.FILE)


class run(BaseCommand):

    """Runs the specified job file on the local dispatcher."""

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument("FILE", help=("The job file to submit."))

    def invoke(self):
        super(run, self).run(self.args.FILE)


class status(BaseCommand):

    """Retrieves the status of a job."""

    @classmethod
    def register_arguments(cls, parser):
        super(status, cls).register_arguments(parser)
        parser.add_argument("JOB_ID",
                            help=("Prints status information about the "
                                  "provided job id."),
                            nargs="?",
                            default=None)

    def invoke(self):
        if self.args.JOB_ID:
            super(status, self).status(self.args.JOB_ID)
        else:
            raise CommandError("It is necessary to specify a job id.")
