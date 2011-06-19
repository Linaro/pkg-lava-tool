# Copyright (C) 2010 Linaro Limited
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
Package with command line commands
"""

import argparse
import re


class ExperimentalNoticeAction(argparse.Action):
    """
    Argparse action that implements the --experimental-notice
    """

    message = """
    Some lc-tool sub-commands are marked as EXPERIMENTAL. Those commands are
    not guaranteed to work identically, or have identical interface between
    subsequent lc-tool releases.

    We do that to make it possible to provide good user interface and
    server-side API when working on new features. Once a feature is stabilized
    the UI will be frozen and all subsequent changes will retain backwards
    compatibility.
    """
    message = message.lstrip()
    message = re.sub(re.compile("[ \t]+", re.M), " ", message)
    message = re.sub(re.compile("^ ", re.M), "", message)

    def __init__(self,
                 option_strings, dest, default=None, required=False,
                 help=None):
        super(ExperimentalNoticeAction, self).__init__(
            option_strings=option_strings, dest=dest, default=default, nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        parser.exit(message=self.message)


class ExperimentalCommandMixIn(object):
    """
    Experimental command.

    Prints a warning message on each call to invoke()
    """

    def invoke(self):
        self.print_experimental_notice()
        return super(ExperimentalCommandMixIn, self).invoke()

    @classmethod
    def register_arguments(cls, parser):
        retval = super(ExperimentalCommandMixIn,
                       cls).register_arguments(parser)
        parser.register("action", "experimental_notice",
                        ExperimentalNoticeAction)
        group = parser.add_argument_group("experimental commands")
        group.add_argument("--experimental-notice",
                            action="experimental_notice",
                            default=argparse.SUPPRESS,
                            help="Explain the nature of experimental commands")
        return retval

    def print_experimental_notice(self):
        print ("EXPERIMENTAL - SUBJECT TO CHANGE"
               " (See --experimental-notice for more info)")
