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

When invoking:

 `lava init [DIR]`

the command will create a default directory and files structure as follows:

DIR/
   |
   +- JOB_FILE.json
   +- tests/
           |
           + mytest.sh
           + TEST_DEF.yaml

If DIR is not passed, it will use the current working directory.
JOB_FILE and TEST_DEF are file names that will be asked to the user, along with
other necessary information to define the tests.

If the user manually updates either the TEST_DEF.yaml or mytest.sh file, it is
necessary to run the following command in order to update the job definition:

 `lava update [JOB|DIR]`
"""

import copy
import json
import os
import sys

from lava.helper.command import BaseCommand
from lava.helper.template import expand_template
from lava.job.commands import JOB_FILE_EXTENSIONS
from lava.parameter import (
    Parameter,
    TarRepoParameter,
)
from lava.job.templates import (
    ACTIONS_ID,
    PARAMETERS_ID,
    TESTDEF_REPOS_ID,
    TESTDEF_REPOS_TAR_REPO,
)
from lava.testdef.templates import (
    DEFAULT_TESTDEF_FILE,
    DEFAULT_TESTDEF_SCRIPT,
    DEFAULT_TESTDEF_SCRIPT_CONTENT,
)
from lava.tool.errors import CommandError

# Default directory structure name.
TESTS_DIR = "tests"

# Internal parameter ids.
JOBFILE_ID = "jobfile"

JOBFILE_PARAMETER = Parameter(JOBFILE_ID)
JOBFILE_PARAMETER.store = False

INIT_TEMPLATE = {
    JOBFILE_ID: JOBFILE_PARAMETER,
}


class init(BaseCommand):
    """Set-ups the base directory structure."""

    @classmethod
    def register_arguments(cls, parser):
        super(init, cls).register_arguments(parser)
        parser.add_argument("DIR",
                            help=("The name of the directory to initialize. "
                                  "Defaults to current working directory."),
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

        test_path = os.path.join(full_path, TESTS_DIR)
        if not os.path.isdir(test_path):
            try:
                os.makedirs(test_path)
            except OSError:
                raise CommandError("Cannot create directory "
                                   "'{0}'.".format(self.args.DIR))

        data = self._update_data()
        self._create_files(data, full_path, test_path)

    def _update_data(self):
        """Updates the template and ask values to the user.

        The template in this case is a layout of the directory structure as it
        would be written to disk.

        :return A dictionary containing all the necessary file names to create.
        """
        data = copy.deepcopy(INIT_TEMPLATE)
        expand_template(data, self.config)

        return data

    def _create_files(self, data, full_path, test_path):
        # This is the default script file as defined in the testdef template.
        default_script = os.path.join(test_path, DEFAULT_TESTDEF_SCRIPT)

        if not os.path.isfile(default_script):
            # We do not have the default testdef script. Create it, but
            # remind the user to update it.
            print >> sys.stdout, ("\nCreating default test script "
                                  "'{0}'.".format(DEFAULT_TESTDEF_SCRIPT))

            with open(default_script, "w") as write_file:
                write_file.write(DEFAULT_TESTDEF_SCRIPT_CONTENT)

            # Prompt the user to write the script file.
            self.edit_file(default_script)

        print >> sys.stdout, ("\nCreating test definition "
                              "'{0}':".format(DEFAULT_TESTDEF_FILE))
        self._create_test_file(os.path.join(test_path,
                                            DEFAULT_TESTDEF_FILE))

        job = data[JOBFILE_ID]
        print >> sys.stdout, "\nCreating job file '{0}':".format(job)
        self._create_job_file(os.path.join(full_path, job), test_path)

    def _create_job_file(self, job_file, test_path=None):
        """Creates the job file on the filesystem."""

        # Invoke the command to create new job files: make a copy of the local
        # args and add what is necessary for the command.
        from lava.job.commands import new

        args = copy.copy(self.args)
        args.FILE = job_file

        job_cmd = new(self.parser, args)
        job_cmd.invoke(tests_dir=test_path)

    def _create_test_file(self, test_file):
        """Creates the test definition file on the filesystem."""

        # Invoke the command to create new testdef files: make a copy of the
        # local args and add what is necessary for the command.
        from lava.testdef.commands import new

        args = copy.copy(self.args)
        args.FILE = test_file

        testdef_cmd = new(self.parser, args)
        testdef_cmd.invoke()


class run(BaseCommand):
    """Runs a job on the local dispatcher."""

    @classmethod
    def register_arguments(cls, parser):
        super(run, cls).register_arguments(parser)
        parser.add_argument("JOB",
                            help=("The job file to run, or a directory "
                                  "containing a job file. If nothing is "
                                  "passed, it uses the current working "
                                  "directory."),
                            nargs="?",
                            default=os.getcwd())

    def invoke(self):
        full_path = os.path.abspath(self.args.JOB)
        job_file = self.retrieve_file(full_path, JOB_FILE_EXTENSIONS)

        self._run_job(job_file)

    def _run_job(self, job_file):
        """Runs a job on the dispatcher."""
        from lava.job.commands import run

        args = copy.copy(self.args)
        args.FILE = job_file

        run_cmd = run(self.parser, args)
        run_cmd.invoke()


class submit(BaseCommand):
    """Submits a job to LAVA."""

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
        job_file = self.retrieve_file(full_path, JOB_FILE_EXTENSIONS)

        self._submit_job(job_file)

    def _submit_job(self, job_file):
        """Submits a job file to LAVA."""
        from lava.job.commands import submit

        args = copy.copy(self.args)
        args.FILE = job_file

        submit_cmd = submit(self.parser, args)
        submit_cmd.invoke()


class update(BaseCommand):
    """Updates a job file with the correct data."""

    @classmethod
    def register_arguments(cls, parser):
        super(update, cls).register_arguments(parser)
        parser.add_argument("JOB",
                            help=("Automatically updates a job file "
                                  "definition. If nothing is passed, it uses"
                                  "the current working directory."),
                            nargs="?",
                            default=os.getcwd())

    def invoke(self):
        full_path = os.path.abspath(self.args.JOB)
        job_file = self.retrieve_file(full_path, JOB_FILE_EXTENSIONS)
        job_dir = os.path.dirname(job_file)
        tests_dir = os.path.join(job_dir, TESTS_DIR)

        if os.path.isdir(tests_dir):
            encoded_tests = TarRepoParameter.get_encoded_tar(tests_dir)

            json_data = None
            with open(job_file, "r") as json_file:
                try:
                    json_data = json.load(json_file)
                    # TODO: find a better way to retrieve a key.
                    json_data[ACTIONS_ID][1][PARAMETERS_ID][TESTDEF_REPOS_ID][TESTDEF_REPOS_TAR_REPO] = \
                        encoded_tests
                except Exception:
                    raise CommandError("Cannot read job file '{0}'.".format(
                        job_file))

            with open(job_file, "w") as write_file:
                try:
                    write_file.write(json.dumps(json_data, indent=4))
                except Exception:
                    raise CommandError("Cannot update job file "
                                       "'{0}'.".format(json_file))
            print >> sys.stdout, "Job definition updated."
        else:
            raise CommandError("Cannot find tests directory.")
