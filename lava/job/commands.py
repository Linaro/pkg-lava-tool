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

from os.path import exists

from lava.job import Job
from lava.job.templates import *
from lava.tool.command import Command, CommandGroup
from lava.tool.errors import CommandError


class job(CommandGroup):
    """
    LAVA job file handling
    """

    namespace = 'lava.job.commands'

class new(Command):

    def __init__(self, parser, args):
        super(new, self).__init__(parser, args)
        self.config_source = {} # FIXME

    @classmethod
    def register_arguments(self, parser):
        super(new, self).register_arguments(parser)
        parser.add_argument("FILE", help=("Job file to be created."))

    def invoke(self):
        if exists(self.args.FILE):
            raise CommandError('%s already exists', self.args.FILE)

        with open(self.args.FILE, 'w') as f:
            job = Job(BOOT_TEST)
            job.fill_in(self.config_source)
            job.write(f)


class submit(Command):
    def invoke(self):
        print("hello world")

class run(Command):
    def invoke(self):
        print("hello world")
