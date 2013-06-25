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

"""
Parameter class and its accessory methods/functions.
"""

import sys


class Parameter(object):
    """A parameter with an optional dependency."""
    def __init__(self, id, value=None, depends=None):
        """Creates a new parameter.

        :param id: The name of this parameter.
        :param value: The value of this parameter. Defaults to None.
        :param depends: If this Parameter depends on another one. Defaults
                        to None.
        :type Parameter
        """
        self.id = id
        self.value = value
        self.depends = depends
        self.asked = False

    def prompt(self, reask=False):
        """Gets the parameter value from the user.

        To get user input, the builtin `raw_input` function will be used. Input
        will also be stripped of possible whitespace chars. If Enter or any
        sort of whitespace chars in typed, the old Parameter value will be
        returned.

        :param reask: If the parameter has to be reasked.
        :type bool
        :return The input as typed by the user, or the old Parameter value.
        """
        if reask:
            prompt = "{0} [{1}]: ".format(self.id, self.value)
        else:
            prompt = "{0}: ".format(self.id)

        user_input = None
        try:
            user_input = raw_input(prompt).strip()
        except EOFError:
            pass
        except KeyboardInterrupt:
            sys.exit(-1)

        if user_input is not None:
            if len(user_input) == 0 and self.value:
                # Keep the old value when user press enter or another
                # whitespace char.
                pass
            else:
                self.value = user_input
        return self.value
