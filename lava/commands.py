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


class submit(BaseCommand):
    """Submits a job to LAVA."""

    # Possible suffixes for a job file.
    JOB_FILE_SUFFIXES = ["json"]

    @classmethod
    def register_arguments(cls, parser):
        super(submit, cls).register_arguments(parser)
        parser.add_argument("JOB",
                            help=("The job file to send, or a directory "
                                  "containing a job file. If nothing is "
                                  "passed, it uses the current working "
                                  "directory."),
                            nargs="?",
                            default=os.getcwd())

    def invoke(self):
        full_path = os.path.abspath(self.args.JOB)

        if os.path.isfile(full_path):
            job_file = full_path
        else:
            job_file = self._retrieve_job_file(full_path)

        self._submit_job(job_file)

    def _retrieve_job_file(self, path):
        """Searches for a job file in the provided path.

        :return The job file full path.
        """
        for element in os.listdir(path):
            element_path = os.path.join(path, element)
            if os.path.isdir(element_path):
                continue
            elif os.path.isfile(element_path):
                job_file = os.path.split(element)[1]
                # Extension here contains also the leading dot.
                full_extension = os.path.splitext(job_file)[1]

                if full_extension:
                    # Make sure that we have an extension and remove the dot.
                    extension = full_extension[1:].strip().lower()
                    if extension in self.JOB_FILE_SUFFIXES:
                        return element_path
        else:
            raise CommandError("No job file found in: '{0}'".format(path))

    def _submit_job(self, job_file):
        """Submits a job file to LAVA."""
        from lava.job.commands import submit

        args = copy.copy(self.args)
        args.FILE = job_file

        submit_cmd = submit(self.parser, args)
        submit_cmd.invoke()
