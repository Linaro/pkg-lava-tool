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
import types
import urllib
import urlparse


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

    @classmethod
    def serialize(cls, value):
        """Serializes the passed value to be friendly written to file.

        Lists are serialized as a comma separated string of values.

        :param value: The value to serialize.
        :return The serialized value as string.
        """
        serialized = ""
        if isinstance(value, list):
            serialized = ",".join(str(x) for x in value if x)
        else:
            serialized = str(value)
        return serialized


class ListParameter(Parameter):
    """A specialized Parameter to handle list values."""

    def __init__(self, id, value=None, depends=None):
        super(ListParameter, self).__init__(id, depends=depends)
        self.value = []

    @classmethod
    def deserialize(cls, value):
        """Deserialize a value into a list.

        The value must have been serialized with the class instance serialize()
        method.

        :param value: The string value to be deserialized.
        :type str
        :return A list of values.
        """
        deserialized = []
        if isinstance(value, types.StringTypes):
            deserialized = filter(None, (x.strip() for x in value.split(",")))
        else:
            deserialized = list(value)
        return deserialized

    def prompt(self, old_value=None):
        """Gets the parameter in a list form.

        To exit the input procedure it is necessary to insert an empty line.

        :return The list of values.
        """

        if old_value is not None:
            # We might get the old value read from file via ConfigParser, and
            # usually it comes in string format.
            old_value = self.deserialize(old_value)

        print >> sys.stdout, "Values for '{0}': ".format(self.id)

        index = 1
        while True:
            user_input = None
            try:
                if old_value is not None and (0 < len(old_value) >= index):
                    prompt = "{0:>3d}.\n\told: {1}\n\tnew: "
                    user_input = raw_input(
                        prompt.format(index, old_value[index-1])).strip()
                else:
                    prompt = "{0:>3d}. "
                    user_input = raw_input(prompt.format(index)).strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                sys.exit(-1)

            if user_input is not None:
                if len(user_input) == 0:
                    if old_value is not None and (0 < len(old_value) >= index):
                        user_input = old_value[index-1]
                    else:
                        break

                self.value.append(user_input)
                index += 1

        self.asked = True
        return self.value


class UrlParameter(ListParameter):

    def __init__(self, id, value=None, depends=None):
        super(UrlParameter, self).__init__(id, depends=depends)
        # The supported URL schemes:
        #   file: normal file URL
        #   data: base64 encoded string of the file pointed to
        self.url_types = ["file", "data"]
        self.urls = []

    @classmethod
    def base64encode(cls):
        pass

    @classmethod
    def base64decode(cls):
        pass

    def prompt(self, old_value=None):
        """First asks the URL scheme, then asks the URL."""
        types_len = len(self.url_types)

        # TODO: need to handle old_values here too.
        # TODO: need to encode/decode in base64 when using data
        print >> sys.stdout, "\nType of URL:"

        index = 1
        for url_type in self.url_types:
            print >> sys.stdout, "\t{0:d}. {1}".format(index, url_type)
            index += 1

        user_input = None
        while True:
            try:
                user_input = raw_input("Choose URL type: ").strip()
            except EOFError:
                continue
            except KeyboardInterrupt:
                sys.exit(-1)

            if user_input not in [str(x) for x in range(1, types_len + 1)]:
                continue
            else:
                # Create the correct ULR scheme.
                url_scheme = self.url_types[int(user_input) - 1] + ":"

                # Now really ask the list of files.
                super(UrlParameter, self).prompt(old_value=old_value)

                if self.value is not None:
                    for path in self.value:
                        url = urlparse.urljoin(url_scheme,
                                               urllib.pathname2url(path))
                        self.urls.append(url)
                break

        return self.urls
