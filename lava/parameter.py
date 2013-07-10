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

# Character used to join serialized list parameters.
LIST_SERIALIZE_DELIMITER = ","


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
        # Whether to store or not the parameter.
        self.store = True

    def set(self, value):
        """Sets the value of the parameter.

        :param value: The value to set.
        """
        self.value = value

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
            serialized = LIST_SERIALIZE_DELIMITER.join(
                str(x) for x in value if x)
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


class SingleChoiceParameter(Parameter):
    """A parameter implemeting a single choice between multiple choices."""
    def __init__(self, id, choices):
        super(SingleChoiceParameter, self).__init__(id)
        if isinstance(choices, types.StringTypes):
            self.choices = [choices]
        else:
            self.choices = list(choices)

    def prompt(self, prompt, old_value=None):
        """Asks the user for their choice."""
        # Sliglty different than the other parameters: here we first present
        # the user with what the choices are about.
        print >> sys.stdout, prompt

        index = 1
        for choice in self.choices:
            print >> sys.stdout, "\t{0:d}. {1}".format(index, choice)
            index += 1

        choices_len = len(self.choices)
        while True:
            user_input = self.get_user_input("Choice: ")

            if len(user_input) == 0 and old_value:
                choice = old_value
                break
            elif user_input in [str(x) for x in range(1, choices_len + 1)]:
                choice = self.choices[int(user_input) - 1]
                break

        return choice


class UrlSchemeParameter(SingleChoiceParameter):
    """A parameter to choose the URL scheme to use."""
    # The supported URL schemes:
    #   file: normal file URL.
    #   data: base64 encoded string of the file pointed to and its path.
    FILE_SCHEME = "file"
    DATA_SCHEME = "data"

    SCHEME_CHOICES = [
        FILE_SCHEME,
        DATA_SCHEME,
    ]

    def __init__(self, value=None, id="url_scheme"):
        super(UrlSchemeParameter, self).__init__(id, self.SCHEME_CHOICES)
        self.value = value

    def prompt(self, prompt="", old_value=None):
        if not self.asked:
            if old_value is not None:
                prompt = "\nURL scheme [was: {0}]:".format(old_value)
            else:
                prompt = "\nURL scheme:"
            self.value = super(UrlSchemeParameter, self).prompt(
                prompt=prompt, old_value=old_value)

        return self.value


class ListParameter(Parameter):
    """A specialized Parameter to handle list values."""

    # This is used as a deletion character. When we have an old value and the
    # user enters this char, it sort of deletes the value.
    DELETE_CHAR = "-"

    def __init__(self, id, value=None, depends=None):
        super(ListParameter, self).__init__(id, depends=depends)
        self.value = []
        if value:
            self.set(value)

    def set(self, value):
        """Sets the value of the parameter.

        :param value: The value to set.
        """
        if isinstance(value, types.StringTypes):
            value = self.deserialize(value)
        else:
            value = list(value)

        self.value = value

    def add(self, value):
        """Adds a new value to the list of values of this parameter.

        :param value: The value to add.
        """
        if isinstance(value, list):
            value = self.serialize(value)
        self.value.append(value)

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
            deserialized = filter(None, (x.strip() for x in value.split(
                LIST_SERIALIZE_DELIMITER)))
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


class UrlListParameter(ListParameter):
    """A parameter holding a list of URLs."""

    # This is the delimiter used when encoding the values using the
    # data scheme.
    DELIMITER = ";"
    # Delimiter used when writing data: type URLs.
    URL_SCHEME_DELIMITER = ":"

    def __init__(self, id, value=None, depends=None):
        super(UrlListParameter, self).__init__(id, depends=depends)
        # The scheme will be just one for all URLs. Automatically default to
        # the "data:" scheme, and do not ask it to the user.
        self.scheme = UrlSchemeParameter(value=UrlSchemeParameter.DATA_SCHEME)
        self.scheme.asked = True
        # Where we store the URLs.
        self.urls = []

    @classmethod
    def base64encode(cls, paths):
        """Encodes in base64 the provided path.

        If path is a path to an existing file, the encoding will work in this
        way: it will encode the path, and the content of the file. The result
        will be a string with the two encoded values joined by a semi-colon:
        the first value is the path, the second the content.

        :param path: What to encode.
        :return The encoded value.
        """
        import tempfile
        import tarfile

        try:
            temp_tar_file = tempfile.NamedTemporaryFile(suffix=".tar",
                                                        delete=False)
            with tarfile.open(temp_tar_file.name) as tar_file:
                for path in paths:
                    full_path = os.path.abspath(path)
                    tar_file.add(full_path)

            encoded_content = StringIO.StringIO()

            if os.path.isfile(temp_tar_file.name):
                try:
                    with open(temp_tar_file.name) as read_file:
                        base64.encode(read_file, encoded_content)

                    return encoded_content.getvalue().strip()
                except IOError:
                    raise CommandError("Cannot read file '{0}'.".format(path))
            else:
                raise CommandError("Provided path does not exists: "
                                   "{0}.".format(path))
        finally:
            os.unlink(temp_tar_file.name)

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
            if old_scheme == self.scheme.DATA_SCHEME:
                value = self.base64decode(urlparse.urlparse(value).path)
            path = urlparse.urlparse(value).path
            cleaned_values.append(path)

        return (old_scheme, cleaned_values)

    def prompt(self, old_value=None):
        """Asks for the URI to test definition files."""
        url_scheme = self.scheme.prompt()
        # Now really ask the list of files.
        super(UrlListParameter, self).prompt(old_value=old_value)

        if url_scheme == UrlSchemeParameter.DATA_SCHEME:
            # We need to do it by hand, or urlparse.urlparse will remove
            # the delimiter for econded data when we read an empty file.
            data = self.base64encode(self.value)
            url = self.URL_SCHEME_DELIMITER.join([url_scheme, data])
            self.urls.append(url)
        else:
            for path in self.value:
                parts = list(urlparse.urlparse(os.path.abspath(path)))
                parts[0] = url_scheme
                url = urlparse.urlunparse(parts)
                self.urls.append(url)

        return self.urls
