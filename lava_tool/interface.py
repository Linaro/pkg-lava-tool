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
        themselves.

        The default implementation stores both arguments
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
