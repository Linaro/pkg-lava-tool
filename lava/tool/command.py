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

import inspect


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

        The default implementation stores both arguments as instance
        attributes.
        """
        self.parser = parser
        self.args = args

    def say(self, message, *args, **kwargs):
        """
        Handy wrapper for print + format
        """
        self.args.dispatcher.say(self, message, *args, **kwargs)

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


class CommandGroup(Command):
    """
    Base class for all command sub-command hubs.

    This class is needed when one wants to get a custom level of command
    options that can be freely extended, just like the top-level lava-tool
    command.

    For example, a CommandGroup 'actions' will load additional commands from a
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
        them with a Dispatcher class. The parsers used by that dispatcher
        are linked to the calling dispatcher parser so the new commands enrich
        the top-level parser tree.

        In addition, the provided parser stores a dispatcher instance in its
        defaults. This is useful when one wants to access it later. To a final
        command instance it shall be available as self.args.dispatcher.
        """
        from lava.tool.dispatcher import Dispatcher
        dispatcher = Dispatcher(parser, name=cls.get_name())
        namespace = cls.get_namespace()
        if namespace is not None:
            dispatcher.import_commands(namespace)
        parser.set_defaults(dispatcher=dispatcher)


SubCommand = CommandGroup
