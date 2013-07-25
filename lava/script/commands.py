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

"""Commands to run or submit a script."""

import os
import tempfile

from lava.job.commands import DEFAULT_JOB_EXTENSION
from lava.tool.command import CommandGroup
from lava.helper.command import BaseCommand

JOB_FILE_EXTENSION = "." + DEFAULT_JOB_EXTENSION


class script(CommandGroup):

    """LAVA script file handling."""

    namespace = "lava.script.commands"


class run(BaseCommand):

    """Runs the specified shell script on a local device."""

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Shell script file to run.")

    def invoke(self):
        try:
            job_file_name = "shell_run_tmp_job" + JOB_FILE_EXTENSION
            job_file = os.path.join(tempfile.gettempdir(), job_file_name)

            tar_content = [self.args.FILE]
            self.create_tar_repo_job(job_file, self.args.FILE, tar_content)

            super(run, self).run(job_file)
        finally:
            if os.path.isfile(job_file):
                os.unlink(job_file)


class submit(BaseCommand):

    """Submits the specified shell script to a LAVA server."""

    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Shell script file to send.")

    def invoke(self):
        try:
            job_file_name = "shell_submit_tmp_job" + JOB_FILE_EXTENSION
            job_file = os.path.join(tempfile.gettempdir(), job_file_name)

            tar_content = [self.args.FILE]
            self.create_tar_repo_job(job_file, self.args.FILE, tar_content)

            super(submit, self).submit(job_file)
        finally:
            if os.path.isfile(job_file):
                os.unlink(job_file)
