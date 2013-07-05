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

import StringIO
import base64
import os
import sys
import types
import urlparse

from lava.tool.errors import CommandError


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

        user_input = self.get_user_input(prompt)

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

    def get_user_input(self, prompt=""):
        """Asks the user for input data.

        :param prompt: The prompt that should be given to the user.
        :return A string with what the user typed.
        """
        data = None
        try:
            data = raw_input(prompt).strip()
        except EOFError:
            # Force to return None.
            data = None
        except KeyboardInterrupt:
            sys.exit(-1)
        return data


class ListParameter(Parameter):
    """A specialized Parameter to handle list values."""

    # This is used as a deletion character. When we have an old value and the
    # user enters this char, it sort of deletes the value.
    DELETE_CHAR = "-"

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
            if old_value is not None and (0 < len(old_value) >= index):
                prompt = "{0:>3d}.\n\told: {1}\n\tnew: ".format(
                    index, old_value[index-1])
                user_input = self.get_user_input(prompt)
            else:
                prompt = "{0:>3d}. ".format(index)
                user_input = self.get_user_input(prompt)

            if user_input is not None:
                # The user has pressed Enter.
                if len(user_input) == 0:
                    if old_value is not None and (0 < len(old_value) >= index):
                        user_input = old_value[index-1]
                    else:
                        break

                if len(user_input) == 1 and user_input == self.DELETE_CHAR \
                        and (0 < len(old_value) >= index):
                    # We have an old value, user presses the DELETE_CHAR and
                    # we do not store anything. This is done to delete an
                    # old entry.
                    pass
                else:
                    self.value.append(user_input)
                index += 1

        self.asked = True
        return self.value


class UrlParameter(ListParameter):
    """A parameter holding a list of URLs."""

    FILE_SCHEME = "file"
    DATA_SCHEME = "data"
    # This is the delimiter used when encoding the values using the
    # data scheme.
    DELIMITER = ";"

    def __init__(self, id, value=None, depends=None):
        super(UrlParameter, self).__init__(id, depends=depends)
        # The supported URL schemes:
        #   file: normal file URL.
        #   data: base64 encoded string of the file pointed to and its path.
        self.url_schemes = [
            self.FILE_SCHEME,
            self.DATA_SCHEME,
        ]
        self.urls = []

    @classmethod
    def base64encode(cls, path):
        """Encodes in base64 the provided path.

        If path is a path to an existing file, the encoding will work in this
        way: it will encode the path, and the content of the file. The result
        will be a string with the two encoded values joined by a semi-colon:
        the first value is the path, the second the content.

        :param path: What to encode.
        :return The encoded value.
        """
        encoded_string = ""
        full_path = os.path.abspath(path)
        if os.path.isfile(full_path):
            # The encoded string will be the file path plus its content.
            # We use a comma as a delimiter to separate the path from the
            # content.
            encoded_values = []
            encoded_values.append(base64.encodestring(full_path).strip())

            try:
                encoded_content = StringIO.StringIO()

                with open(path) as read_file:
                    base64.encode(read_file, encoded_content)

                encoded_values.append(encoded_content.getvalue().strip())
            except IOError:
                raise CommandError("Cannot read file '{0}'.".format(path))

            encoded_string = cls.DELIMITER.join(encoded_values)
        else:
            raise CommandError("Provided path does not exists: "
                               "{0}.".format(path))
        return encoded_string

    @classmethod
    def base64decode(cls, string):
        """Decodes the provided string."""
        decoded_string = ""
        split_string = string.split(cls.DELIMITER)
        # It has to be exactly 2.
        if len(split_string) == 2:
            # We are interested only in the path, not the content.
            decoded_string = base64.decodestring(split_string[0]).strip()
        return decoded_string

    def _calculate_old_values(self, old_value):
        """Deserialize the old values passed, and decode them.

        :return A tuple with the scheme, and the list of encoded values.
        """
        old_value = self.deserialize(old_value)
        old_scheme = urlparse.urlparse(old_value[0]).scheme

        cleaned_values = []
        for value in old_value:
            # If we have a data scheme, decode the string and get the path.
            if old_scheme == self.DATA_SCHEME:
                value = self.base64decode(urlparse.urlparse(value).path)
            path = urlparse.urlparse(value).path
            cleaned_values.append(path)

        return (old_scheme, cleaned_values)

    def _get_url_scheme(self, old_scheme=None):
        """Asks the user the URL scheme to adopt."""
        if old_scheme is not None:
            prompt = "\nURL scheme [was: {0}]:".format(old_scheme)
        else:
            prompt = "\nURL scheme:"
        print >> sys.stdout, prompt

        index = 1
        for url_type in self.url_schemes:
            print >> sys.stdout, "\t{0:d}. {1}".format(index, url_type)
            index += 1

        types_len = len(self.url_schemes)
        while True:
            user_input = self.get_user_input("Choose URL scheme: ")

            if user_input in [str(x) for x in range(1, types_len + 1)]:
                url_scheme = self.url_schemes[int(user_input) - 1]
                break
            else:
                continue
        return url_scheme

    def prompt(self, old_value=None):
        """First asks the URL scheme, then asks the URL."""
        old_scheme = None
        if old_value is not None:
            old_scheme, old_value = self._calculate_old_values(old_value)

        url_scheme = self._get_url_scheme(old_scheme=old_scheme)
        if url_scheme:
            # Now really ask the list of files.
            super(UrlParameter, self).prompt(old_value=old_value)

        for path in self.value:
            if url_scheme == self.DATA_SCHEME:
                # We need to do it by hand, or urlparse.urlparse will remove
                # the delimiter for econded data when we read an empty file.
                data = self.base64encode(path)
                url = ":".join([url_scheme, data])
            else:
                parts = list(urlparse.urlparse(os.path.abspath(path)))
                parts[0] = url_scheme
                url = urlparse.urlunparse(parts)

            self.urls.append(url)

        return self.urls
