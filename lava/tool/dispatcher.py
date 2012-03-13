# Copyright (C) 2010, 2011, 2012 Linaro Limited
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
import logging
import pkg_resources
import sys

from lava.tool.errors import CommandError


class Dispatcher(object):
    """
    Class implementing command line interface for launch control
    """

    description = None
    epilog = None

    def __init__(self, parser=None, name=None):
        self.parser = parser or self.construct_parser()
        self.subparsers = self.parser.add_subparsers(
                title="Sub-command to invoke")
        self.name = name

    def __repr__(self):
        return "%r(name=%r)" % (self.__class__.__name__, self.name)

    @classmethod
    def construct_parser(cls):
        """
        Construct a parser for this dispatcher.

        This is only used if the parser is not provided by the parent
        dispatcher instance.
        """
        parser_args = dict(add_help=True)
        if cls.description is not None:
            parser_args['description'] = cls.description
        if cls.epilog is not None:
            parser_args['epilog'] = cls.epilog
        return argparse.ArgumentParser(**parser_args)

    def import_commands(self, entrypoint_name):
        """
        Import commands from given entry point namespace
        """
        logging.debug("Loading commands in entry point %r", entrypoint_name)
        for entrypoint in pkg_resources.iter_entry_points(entrypoint_name):
                self.add_command_cls(entrypoint.load())

    def add_command_cls(self, command_cls):
        """
        Add a new command class to this dispatcher.

        The command must be a subclass of Command or SubCommand.
        """
        logging.debug("Loading command class %r", command_cls)
        # Create a sub-parser where the command/sub-command can register
        # things.
        sub_parser = self.subparsers.add_parser(
            command_cls.get_name(),
            help=command_cls.get_help(),
            epilog=command_cls.get_epilog())
        from lava.tool.command import SubCommand
        if issubclass(command_cls, SubCommand):
            # Handle SubCommand somewhat different. Instead of calling
            # register_arguments we call register_subcommands
            command_cls.register_subcommands(sub_parser)
        else:
            # Handle plain commands easily by recording their commands in the
            # dedicated sub-parser we've crated for them.
            command_cls.register_arguments(sub_parser)
            # In addition, since we don't want to require all sub-classes of
            # Command to super-call register_arguments (everyone would forget
            # this anyway) we manually register the command class for that
            # sub-parser so that dispatch() can look it up later.
            sub_parser.set_defaults(
                command_cls=command_cls,
                parser=sub_parser)

    def dispatch(self, raw_args=None):
        """
        Dispatch a command with the specified arguments.

        If arguments are left out they are looked up in sys.argv automatically
        """
        # First parse whatever input arguments we've got
        args = self.parser.parse_args(raw_args)
        # Then look up the command class and construct it with the parser it
        # belongs to and the parsed arguments.
        command = args.command_cls(args.parser, args)
        try:
            # Give the command a chance to re-parse command line arguments
            command.reparse_arguments(args.parser, raw_args)
        except NotImplementedError:
            pass
        try:
            return command.invoke()
        except CommandError as ex:
            print >> sys.stderr, "ERROR: %s" % (ex,)
            return 1

    @classmethod
    def run(cls):
        """
        Dispatch commandsd and exit
        """
        raise SystemExit(cls().dispatch())
