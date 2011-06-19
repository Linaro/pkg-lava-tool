# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
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
Module with LavaDispatcher - the command dispatcher
"""

import argparse
import pkg_resources
import sys

from lava_tool.interface import LavaCommandError


class LavaDispatcher(object):
    """
    Class implementing command line interface for launch control
    """

    toolname = None
    description = None
    epilog = None

    def __init__(self):
        # XXX The below needs to allow some customization.
        parser_args = dict(add_help=False)
        if self.description is not None:
            parser_args['description'] = self.description
        if self.epilog is not None:
            parser_args['epilog'] = self.epilog
        self.parser = argparse.ArgumentParser(**parser_args)
        self.subparsers = self.parser.add_subparsers(
                title="Sub-command to invoke")
        prefixes = ['lava_tool']
        if self.toolname is not None:
            prefixes.append(self.toolname)
        for prefix in prefixes:
            for entrypoint in pkg_resources.iter_entry_points(
                "%s.commands" % prefix):
                self.add_command_cls(entrypoint.load())

    def add_command_cls(self, command_cls):
        sub_parser = self.subparsers.add_parser(
            command_cls.get_name(),
            help=command_cls.get_help(),
            epilog=command_cls.get_epilog())
        sub_parser.set_defaults(command_cls=command_cls)
        sub_parser.set_defaults(sub_parser=sub_parser)
        command_cls.register_arguments(sub_parser)

    def dispatch(self, raw_args=None):
        args = self.parser.parse_args(raw_args)
        command = args.command_cls(self.parser, args)
        try:
            command.reparse_arguments(args.sub_parser, raw_args)
        except NotImplementedError:
            pass
        try:
            return command.invoke()
        except LavaCommandError as ex:
            print >> sys.stderr, "ERROR: %s" % (ex,)
            return 1


def run_with_dispatcher_class(cls):
    raise SystemExit(cls().dispatch())


def main():
    run_with_dispatcher_class(LavaDispatcher)
