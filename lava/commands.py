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
import sys

from lava.helper.command import BaseCommand
from lava.helper.template import expand_template
from lava.parameter import (
    Parameter,
    ListParameter,
)
from lava.tool.errors import CommandError

DIRNAME = "dirname"
JOBFILE = "jobfile"
TESTS = "tests"

DIRNAME_PARAMETER = Parameter(DIRNAME)
JOBFILE_PARAMETER = Parameter(JOBFILE)
TESTFILE_PARAMETER = ListParameter(TESTS)

INIT_TEMPLATE = {
    DIRNAME: DIRNAME_PARAMETER,
    JOBFILE: JOBFILE_PARAMETER,
    TESTS: TESTFILE_PARAMETER,
}


class init(BaseCommand):
    """Set ups the base directory structure."""

    @classmethod
    def register_arguments(cls, parser):
        super(init, cls).register_arguments(parser)
        parser.add_argument("DIR",
                            help=("The name of the directory to initialize. "
                                  "Defaults to current working directory"),
                            nargs="?",
                            default=os.getcwd())

    def invoke(self):
        full_path = os.path.abspath(self.args.DIR)

        if os.path.isfile(full_path):
            raise CommandError("'{0}' already exists, and is a "
                               "file.".format(self.args.DIR))

        if not os.path.isdir(full_path):
            try:
                os.makedirs(full_path)
            except OSError:
                raise CommandError("Cannot create directory "
                                   "'{0}'.".format(self.args.DIR))

        data = self._update_data()
        self._create_files(data, full_path)

    def _update_data(self):
        """Updates the template and ask values to the user.

        The template in this case is a layout of the directory structure as it
        would be written to disk.

        :return A dictionary containing all the necessary file names to create.
        """
        data = copy.deepcopy(INIT_TEMPLATE)

        # Do not ask again the dirname parameter.
        data[DIRNAME].value = self.args.DIR
        data[DIRNAME].asked = True

        expand_template(data, self.config)
        return data

    def _create_files(self, data, full_path):
        test_files = ListParameter.deserialize(data[TESTS])

        for test in test_files:
            print >> sys.stdout, ("\nCreating test definition file "
                                  "'{0}':".format(test))
            self._create_test_file(os.path.join(full_path, test))

        job = data[JOBFILE]
        print >> sys.stdout, "\nCreating job file '{0}':".format(job)
        self._create_job_file(os.path.join(full_path, job))

    def _create_job_file(self, job_file):
        """Creates the job file on the filesystem."""

        # Invoke the command to create new job files: make a copy of the local
        # args and add what is necessary for the command.
        from lava.job.commands import new

        args = copy.copy(self.args)
        args.FILE = job_file

        job_cmd = new(self.parser, args)
        job_cmd.invoke()

    def _create_test_file(self, test_file):
        """Creates the test definition file on the filesystem."""

        # Invoke the command to create new testdef files: make a copy of the
        # local args and add what is necessary for the command.
        from lava.testdef.commands import new

        args = copy.copy(self.args)
        args.FILE = test_file

        testdef_cmd = new(self.parser, args)
        testdef_cmd.invoke()
