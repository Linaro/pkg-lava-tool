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
import string


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

    def prompt(self, old_value=None):
        """Gets the parameter value from the user.

        To get user input, the builtin `raw_input` function will be used. Input
        will also be stripped of possible whitespace chars. If Enter or any
        sort of whitespace chars in typed, the old Parameter value will be
        returned.

        :param old_value: The old parameter value.
        :return The input as typed by the user, or the old value.
        """
        if old_value is not None:
            prompt = "{0} [{1}]: ".format(self.id, old_value)
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
            if len(user_input) == 0 and old_value:
                # Keep the old value when user press enter or another
                # whitespace char.
                self.value = old_value
            else:
                self.value = user_input

        self.asked = True
        return self.value


class ListParameter(Parameter):
    """A specialized Parameter to handle list values."""

    def __init__(self, id, depends=None):
        super(ListParameter, self).__init__(id)
        self.value = []

    def prompt(self, old_value=None):
        """Gets the parameter in a list form.

        To exit the input procedure it is necessary to insert an empty line.

        :return The list of values.
        """
        # TODO handle old values and parameters re-insertion.
        user_input = None
        while True:
            # TODO: think about a prompt.
            user_input = raw_input("").strip()
            if user_input in string.whitespace:
                # Input is terminated with an empty string.
                break
            elif user_input is not None:
                self.value.append(user_input)
        return self.value
