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
        # Set description based on class description
        if cls.description is not None:
            parser_args['description'] = cls.description
        # Set the epilog based on class epilog
        if cls.epilog is not None:
            parser_args['epilog'] = cls.epilog
        # Return the fresh parser
        return argparse.ArgumentParser(**parser_args)

    def import_commands(self, entrypoint_name):
        """
        Import commands from given entry point namespace
        """
        logging.debug("Loading commands in entry point %r", entrypoint_name)
        for entrypoint in pkg_resources.iter_entry_points(entrypoint_name):
            try:
                command_cls = entrypoint.load()
            except (ImportError, pkg_resources.DistributionNotFound) as exc:
                logging.exception("Unable to load command: %s", entrypoint.name)
            else:
                self.add_command_cls(command_cls)

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
        from lava.tool.command import CommandGroup 
        if issubclass(command_cls, CommandGroup):
            # Handle CommandGroup somewhat different. Instead of calling
            # register_arguments we call register_subcommands
            command_cls.register_subcommands(sub_parser)
            # Let's also call register arguments in case we need both
            command_cls.register_arguments(sub_parser)
        else:
            # Handle plain commands by recording their commands in the
            # dedicated sub-parser we've crated for them.
            command_cls.register_arguments(sub_parser)
            # In addition, since we don't want to require all sub-classes of
            # Command to super-call register_arguments (everyone would forget
            # this anyway) we manually register the command class for that
            # sub-parser so that dispatch() can look it up later.
            sub_parser.set_defaults(
                command_cls=command_cls,
                parser=sub_parser)
        # Make sure the sub-parser knows about this dispatcher
        sub_parser.set_defaults(dispatcher=self)

    def _adjust_logging_level(self, args):
        """
        Adjust logging level after seeing the initial arguments
        """

    def dispatch(self, raw_args=None):
        """
        Dispatch a command with the specified arguments.

        If arguments are left out they are looked up in sys.argv automatically
        """
        # First parse whatever input arguments we've got
        args = self.parser.parse_args(raw_args)
        # Adjust logging level after seeing arguments
        self._adjust_logging_level(args)
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
    def run(cls, args=None):
        """
        Dispatch commandsd and exit
        """
        raise SystemExit(cls().dispatch(args))

    def say(self, command, message, *args, **kwargs):
        """
        Handy wrapper for print + format
        """
        print "{0} >>> {1}".format(
            command.get_name(),
            message.format(*args, **kwargs))
