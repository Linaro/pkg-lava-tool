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
Lava init commands.
"""

import copy
import os

from lava.helper.command import BaseCommand
from lava.helper.template import expand_template
from lava.job.commands import new as new_job
from lava.parameter import (
    Parameter,
    ListParameter,
)
from lava.testdef.commands import new as new_testdef
from lava.tool.errors import CommandError


DIRNAME_PARAMETER = Parameter("dirname")
JOBFILE_PARAMETER = ListParameter("jobfiles", depends=DIRNAME_PARAMETER)
TESTFILE_PARAMETER = ListParameter("testfiles", depends=DIRNAME_PARAMETER)

INIT_TEMPLATE = {
    "dirname": DIRNAME_PARAMETER,
    "jobfiles": JOBFILE_PARAMETER,
    "testfiles": TESTFILE_PARAMETER,
}


class init(BaseCommand):
    """Setup the base directory structure."""

    @classmethod
    def register_arguments(cls, parser):
        super(init, cls).register_arguments(parser)
        parser.add_argument("DIR", help="The name of the directory to be "
                            "initialized.")

    def invoke(self):
        full_path = os.path.abspath(self.args.DIR)

        if os.path.isdir(full_path):
            raise CommandError("Directory '{0}' alraedy "
                               "exists.".format(self.args.DIR))
        else:
            try:
                os.makedirs(full_path)
            except OSError:
                raise CommandError("Cannot create directory "
                                   "'{0}'.".format(self.args.DIR))

        data = self._update_data()
        self._create_dir_structure(data, full_path)

    def _update_data(self):
        """Updates the template and ask values to the user.

        The template in this case is a layout of the directory structure as it
        would be written to disk.

        :return A dictionary containing all the necessary file names to create.
        """
        data = copy.deepcopy(INIT_TEMPLATE)

        # Do not ask again the dirname parameter.
        data["dirname"].value = self.args.DIR
        data["dirname"].asked = True

        expand_template(data, self.config)
        return data

    def _create_dir_structure(self, data, full_path):
        job_files = ListParameter.deserialize(data["jobfiles"])
        test_files = ListParameter.deserialize(data["testfiles"])
        for job in job_files:
            self._create_job_file(os.path.join(full_path, job))

        for test in test_files:
            self._create_test_file(os.path.join(full_path, test))

    def _create_job_file(self, job_file):
        args = copy.copy(self.args)
        args.FILE = job_file
        job_cmd = new_job(self.parser, args)
        job_cmd.invoke()
        print job_file

    def _create_test_file(self, test_file):
        testdef_cmd = new_testdef(self.parser, self.args)
        print test_file
