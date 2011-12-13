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
Interface for all lava-tool commands
"""

import argparse
import inspect
import logging
import pkg_resources
import sys


class LavaCommandError(Exception):
    """
    Raise this from a Command's invoke() method to display an error nicely.

    lava-tool will exit with a status of 1 if this is raised.
    """


class Command(object):
    """
    Base class for all command line tool sub-commands.
    """

    def __init__(self, parser, args):
        """
        Prepare instance for executing commands.

        This method is called immediately after all arguments are parsed and
        results are available. This gives subclasses a chance to configure
        themselves. The provided parser is an instance of
        argparse.ArgumentParser but it may not be the top-level parser (it will
        be a parser specific for this command)

        The default implementation stores both arguments as instance attributes.
        """
        self.parser = parser
        self.args = args

    def invoke(self):
        """
        Invoke command action.
        """
        raise NotImplementedError()

    def reparse_arguments(self, parser, raw_args):
        """
        Re-parse raw arguments into normal arguments

        Parser is the same as in register_arguments (a sub-parser) The true,
        topmost parser is in self.parser.

        This method is only needed for specific commands that need to peek at
        the arguments before being able to truly redefine the parser and
        re-parse the raw arguments again.
        """
        raise NotImplementedError()

    @classmethod
    def get_name(cls):
        """
        Return the name of this command.

        The default implementation strips any leading underscores and replaces
        all other underscores with dashes.
        """
        return cls.__name__.lstrip("_").replace("_", "-")

    @classmethod
    def get_help(cls):
        """
        Return the help message of this command
        """
        doc = inspect.getdoc(cls)
        if doc is not None and "" in doc:
            doc = doc[:doc.index("")].rstrip()
        return doc

    @classmethod
    def get_epilog(cls):
        """
        Return the epilog of the help message
        """
        doc = inspect.getdoc(cls)
        if doc is not None and "" in doc:
            doc = doc[doc.index("") + 1:].lstrip()
        else:
            doc = None
        return doc

    @classmethod
    def register_arguments(cls, parser):
        """
        Register arguments if required.

        Subclasses can override this to add any arguments that will be
        exposed to the command line interface.
        """
        pass


class SubCommand(Command):
    """
    Base class for all command sub-command hubs.

    This class is needed when one wants to get a custom level of command
    options that can be freely extended, just like the top-level lava-tool
    command.

    For example, a SubCommand 'actions' will load additional commands from a
    the 'lava.actions' namespace. For the end user it will be available as::

        $ lava-tool foo actions xxx

    Where xxx is one of the Commands that is declared to live in the namespace
    provided by 'foo actions'.
    """

    namespace = None

    @classmethod
    def get_namespace(cls):
        """
        Return the pkg-resources entry point namespace name from which
        sub-commands will be loaded.
        """
        return cls.namespace

    @classmethod
    def register_subcommands(cls, parser):
        """
        Register sub commands.

        This method is called around the same time as register_arguments()
        would be called for the plain command classes. It loads commands from
        the entry point namespace returned by get_namespace() and registeres
        them with a BaseDispatcher class. The parsers used by that dispatcher
        are linked to the calling dispatcher parser so the new commands enrich
        the top-level parser tree.

        In addition, the provided parser stores a dispatcher instance in its
        defaults. This is useful when one wants to access it later. To a final
        command instance it shall be available as self.args.dispatcher.
        """
        dispatcher = BaseDispatcher(parser, name=cls.get_name())
        namespace = cls.get_namespace()
        if namespace is not None:
            dispatcher.import_commands(namespace)
        parser.set_defaults(dispatcher=dispatcher)


class BaseDispatcher(object):
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
        # Create a sub-parser where the command/sub-command can register things.
        sub_parser = self.subparsers.add_parser(
            command_cls.get_name(),
            help=command_cls.get_help(),
            epilog=command_cls.get_epilog())
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
        except LavaCommandError as ex:
            print >> sys.stderr, "ERROR: %s" % (ex,)
            return 1
