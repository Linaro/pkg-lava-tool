# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
#
# This file is part of lava-scheduler-tool.
#
# lava-scheduler-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-scheduler-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-scheduler-tool.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse
import xmlrpclib

from lava_tool.authtoken import AuthenticatingServerProxy, KeyringAuthBackend
from lava.tool.command import Command, CommandGroup
from lava.tool.errors import CommandError
from lava.tool.commands import ExperimentalCommandMixIn


class scheduler(CommandGroup):
    """
    Interact with LAVA Scheduler
    """

    namespace = "lava.scheduler.commands"


class submit_job(ExperimentalCommandMixIn, Command):
    """
    Submit a job to lava-scheduler
    """

    @classmethod
    def register_arguments(cls, parser):
        super(submit_job, cls).register_arguments(parser)
        parser.add_argument("SERVER")
        parser.add_argument("JSON_FILE")

    def invoke(self):
        self.print_experimental_notice()
        server = AuthenticatingServerProxy(
            self.args.SERVER, auth_backend=KeyringAuthBackend())
        with open(self.args.JSON_FILE, 'rb') as stream:
            command_text = stream.read()
        try:
            job_id = server.scheduler.submit_job(command_text)
        except xmlrpclib.Fault, e:
            raise CommandError(str(e))
        else:
            print "submitted as job id:", job_id


class resubmit_job(ExperimentalCommandMixIn, Command):

    @classmethod
    def register_arguments(self, parser):
        parser.add_argument("SERVER")
        parser.add_argument("JOB_ID", type=int)

    def invoke(self):
        self.print_experimental_notice()
        server = AuthenticatingServerProxy(
            self.args.SERVER, auth_backend=KeyringAuthBackend())
        try:
            job_id = server.scheduler.resubmit_job(self.args.JOB_ID)
        except xmlrpclib.Fault, e:
            raise CommandError(str(e))
        else:
            print "resubmitted as job id:", job_id


class cancel_job(ExperimentalCommandMixIn, Command):

    @classmethod
    def register_arguments(self, parser):
        parser.add_argument("SERVER")
        parser.add_argument("JOB_ID", type=int)

    def invoke(self):
        self.print_experimental_notice()
        server = AuthenticatingServerProxy(
            self.args.SERVER, auth_backend=KeyringAuthBackend())
        server.scheduler.cancel_job(self.args.JOB_ID)


class job_output(Command):
    """
    Get job output from the scheduler.
    """

    @classmethod
    def register_arguments(cls, parser):
        super(job_output, cls).register_arguments(parser)
        parser.add_argument("SERVER")
        parser.add_argument("JOB_ID",
                            type=int,
                            help="Job ID to download output file")
        parser.add_argument("--overwrite",
                            action="store_true",
                            help="Overwrite files on the local disk")
        parser.add_argument("--output", "-o",
                            type=argparse.FileType("wb"),
                            default=None,
                            help="Alternate name of the output file")

    def invoke(self):
        if self.args.output is None:
            filename = str(self.args.JOB_ID) + '_output.txt'
            if os.path.exists(filename) and not self.args.overwrite:
                print >> sys.stderr, "File {filename!r} already exists".format(
                    filename=filename)
                print >> sys.stderr, "You may pass --overwrite to write over it"
                return -1
            stream = open(filename, "wb")
        else:
            stream = self.args.output
            filename = self.args.output.name

        server = AuthenticatingServerProxy(
            self.args.SERVER, auth_backend=KeyringAuthBackend())
        stream.write(server.scheduler.job_output(self.args.JOB_ID).data)

        print "Downloaded job output of {0} to file {1!r}".format(
            self.args.JOB_ID, filename)
