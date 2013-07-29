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
           + lavatest.yaml

If DIR is not passed, it will use the current working directory.
JOB_FILE is a file name that will be asked to the user, along with
other necessary information to define the tests.

If the user manually updates either the lavatest.yaml or mytest.sh file, it is
necessary to run the following command in order to update the job definition:

 `lava update [JOB|DIR]`
"""

import copy
import json
import os
import sys

from lava.helper.command import BaseCommand
from lava.helper.template import (
    expand_template,
    set_value
)
from lava.job import (
    JOB_FILE_EXTENSIONS,
)
from lava.job.templates import (
    LAVA_TEST_SHELL_TAR_REPO_KEY,
)
from lava.parameter import (
    Parameter,
)
from lava.testdef import (
    DEFAULT_TESTDEF_FILENAME,
)
from lava.tool.errors import CommandError
from lava_tool.utils import (
    base64_encode,
    create_dir,
    create_tar,
    edit_file,
    retrieve_file,
    write_file,
)

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

        create_dir(full_path)
        data = self._update_data()

        # Create the directory that will contain the test definition and
        # shell script.
        test_path = create_dir(full_path, TESTS_DIR)
        shell_script = self.create_shell_script(test_path)
        # Let the user modify the file.
        edit_file(shell_script)

        testdef_file = self.create_test_definition(
            os.path.join(test_path, DEFAULT_TESTDEF_FILENAME))

        job = data[JOBFILE_ID]
        self.create_tar_repo_job(
            os.path.join(full_path, job), testdef_file, test_path)

    def _update_data(self):
        """Updates the template and ask values to the user.

        The template in this case is a layout of the directory structure as it
        would be written to disk.

        :return A dictionary containing all the necessary file names to create.
        """
        data = copy.deepcopy(INIT_TEMPLATE)
        expand_template(data, self.config)

        return data


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
        job_file = retrieve_file(full_path, JOB_FILE_EXTENSIONS)

        super(run, self).run(job_file)


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
        job_file = retrieve_file(full_path, JOB_FILE_EXTENSIONS)

        super(submit, self).submit(job_file)


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
            tar_repo = None
            try:
                tar_repo = create_tar(tests_dir)
                encoded_tests = base64_encode(tar_repo)

                json_data = None
                with open(job_file, "r") as json_file:
                    try:
                        json_data = json.load(json_file)
                        set_value(json_data, LAVA_TEST_SHELL_TAR_REPO_KEY,
                                  encoded_tests)
                    except Exception:
                        raise CommandError("Cannot read job file "
                                           "'{0}'.".format(job_file))

                content = json.dumps(json_data, indent=4)
                write_file(job_file, content)

                print >> sys.stdout, "Job definition updated."
            finally:
                if tar_repo and os.path.isfile(tar_repo):
                    os.unlink(tar_repo)
        else:
            raise CommandError("Cannot find tests directory.")
