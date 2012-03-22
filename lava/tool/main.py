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
lava.tool.main
==============

Implementation of the `lava` shell command.
"""

import logging
import sys

from lava.tool.dispatcher import Dispatcher


class LavaDispatcher(Dispatcher):
    """
    Dispatcher implementing the `lava` shell command

    This dispatcher imports plugins from `lava.commands` pkg_resources
    namespace. Additional plugins can be registered as either
    :class:`lava.command.Command` or :class:`lava.command.SubCommand`
    sub-classes.
    """

    def __init__(self):
        # Call this early so that we don't get logging.basicConfig
        # being called by accident. Otherwise we'd have to
        # purge all loggers from the root logger and that sucks
        self.setup_logging()
        # Initialize the base dispatcher
        super(LavaDispatcher, self).__init__()
        # And import the non-flat namespace commands
        self.import_commands('lava.commands')

    @classmethod
    def construct_parser(cls):
        """
        Construct a parser for this dispatcher.

        This is only used if the parser is not provided by the parent
        dispatcher instance.
        """
        # Construct a basic parser
        parser = super(LavaDispatcher, cls).construct_parser()
        # Add the --verbose flag
        parser.add_argument(
            "-v", "--verbose",
            default=False,
            action="store_true",
            help="Be more verbose (displays more messages globally)")
        # Add the --debug flag
        parser.add_argument(
            "-D", "--debug",
            action="store_true",
            default=False,
            help="Enable debugging on all loggers")
        # Add the --trace flag
        parser.add_argument(
            "-T", "--trace",
            action="append",
            default=[],
            help="Enable debugging of the specified logger, can be specified multiple times")
        # Return the improved parser
        return parser 

    def setup_logging(self):
        """
        Setup logging for the root dispatcher
        """
        # Enable warning/error message handler
        class OnlyProblemsFilter(logging.Filterer):
            def filter(self, record):
                if record.levelno >= logging.WARN:
                    return 1
                return 0
        err_handler = logging.StreamHandler(sys.stderr)
        err_handler.setLevel(logging.WARN)
        err_handler.setFormatter(
            logging.Formatter("%(levelname)s: %(message)s"))
        err_handler.addFilter(OnlyProblemsFilter())
        logging.getLogger().addHandler(err_handler)
        # Enable the debug handler
        class DebugFilter(logging.Filter):
            def filter(self, record):
                if record.levelno == logging.DEBUG:
                    return 1
                return 0
        dbg_handler = logging.StreamHandler(sys.stderr)
        dbg_handler.setLevel(logging.DEBUG)
        dbg_handler.setFormatter(
            logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        dbg_handler.addFilter(DebugFilter())
        logging.getLogger().addHandler(dbg_handler)

    def _adjust_logging_level(self, args):
        # Enable verbose message handler
        if args.verbose:
            logging.getLogger().setLevel(logging.INFO)
            class OnlyInfoFilter(logging.Filterer):
                def filter(self, record):
                    if record.levelno == logging.INFO:
                        return 1
                    return 0
            msg_handler = logging.StreamHandler(sys.stdout)
            msg_handler.setLevel(logging.INFO)
            msg_handler.setFormatter(
                logging.Formatter("%(message)s"))
            msg_handler.addFilter(OnlyInfoFilter())
            logging.getLogger().addHandler(msg_handler)
        # Enable debugging 
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        # Enable trace loggers
        for name in args.trace:
            logging.getLogger(name).setLevel(logging.DEBUG)
