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

"""
Test definition commands class.
"""

import os
import tempfile

from lava.helper.command import BaseCommand
from lava.job import DEFAULT_JOB_FILENAME
from lava.tool.command import CommandGroup
from lava_tool.utils import verify_path_non_existance


class testdef(CommandGroup):

    """LAVA test definitions handling."""

    namespace = "lava.testdef.commands"


class TestdefBaseCommand(BaseCommand):

    def _create_tmp_job_file(self, testdef_file):
        testdef_file = os.path.abspath(testdef_file)
        verify_path_non_existance(testdef_file)

        job_file = os.path.join(tempfile.gettempdir(),
                                DEFAULT_JOB_FILENAME)

        tar_content = [testdef_file]
        job_file = self.create_tar_repo_job(job_file, testdef_file,
                                            tar_content)

        return job_file


class new(TestdefBaseCommand):

    """Creates a new test definition file."""

    @classmethod
    def register_arguments(cls, parser):
        super(new, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Test definition file to create.")

    def invoke(self):
        full_path = os.path.abspath(self.args.FILE)
        self.create_test_definition(full_path)


class run(TestdefBaseCommand):

    """Runs the specified test definition on a local device."""

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Test definition file to run.")

    def invoke(self):
        job_file = ""
        try:
            job_file = self._create_tmp_job_file(self.args.FILE)
            super(run, self).run(job_file)
        finally:
            if os.path.isfile(job_file):
                os.unlink(job_file)


class submit(TestdefBaseCommand):

    """Submits the specified test definition to a LAVA server."""

    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("FILE", help="Test definition file to send.")

    def invoke(self):
        job_file = ""
        try:
            job_file = self._create_tmp_job_file(self.args.FILE)
            super(submit, self).submit(job_file)
        finally:
            if os.path.isfile(job_file):
                os.unlink(job_file)
