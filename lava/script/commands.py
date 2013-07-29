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

from lava.helper.command import BaseCommand
from lava.job import DEFAULT_JOB_FILENAME
from lava.testdef import DEFAULT_TESTDEF_FILENAME
from lava.tool.command import CommandGroup
from lava_tool.utils import verify_path_non_existance


class script(CommandGroup):

    """LAVA script file handling."""

    namespace = "lava.script.commands"


class ScriptBaseCommand(BaseCommand):

    def _create_tmp_job_file(self, script_file):
        """Creates a temporary job file to run or submit the passed file.

        The temporary job file and its accessory test definition file are
        not removed by this method.

        :param script_file: The script file that has to be run or submitted.
        :return A tuple with the job file path, and the test definition path.
        """
        script_file = os.path.abspath(script_file)
        verify_path_non_existance(script_file)

        temp_dir = tempfile.gettempdir()

        # The name of the job and testdef files.
        job_file = os.path.join(temp_dir, DEFAULT_JOB_FILENAME)
        testdef_file = os.path.join(temp_dir, DEFAULT_TESTDEF_FILENAME)

        # The steps that the testdef file should have. We need to change it
        # from the default one, since the users are passing their own file.
        steps = "./" + os.path.basename(script_file)
        testdef_file = self.create_test_definition(testdef_file,
                                                   steps=steps)

        # The content of the tar file.
        tar_content = [script_file, testdef_file]
        job_file = self.create_tar_repo_job(job_file, testdef_file,
                                            tar_content)

        return (job_file, testdef_file)


class run(ScriptBaseCommand):

    """Runs the specified shell script on a local device."""

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Shell script file to run.")

    def invoke(self):
        job_file = ""
        testdef_file = ""

        try:
            job_file, testdef_file = self._create_tmp_job_file(self.args.FILE)
            super(run, self).run(job_file)
        finally:
            if os.path.isfile(job_file):
                os.unlink(job_file)
            if os.path.isfile(testdef_file):
                os.unlink(testdef_file)


class submit(ScriptBaseCommand):

    """Submits the specified shell script to a LAVA server."""

    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Shell script file to send.")

    def invoke(self):
        job_file = ""
        testdef_file = ""

        try:
            job_file, testdef_file = self._create_tmp_job_file(self.args.FILE)
            super(submit, self).submit(job_file)
        finally:
            if os.path.isfile(job_file):
                os.unlink(job_file)
            if os.path.isfile(testdef_file):
                os.unlink(testdef_file)
