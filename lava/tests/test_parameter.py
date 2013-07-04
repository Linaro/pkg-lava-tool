# Copyright (C) 2013 Linaro Limited
#
# Author: Milo Casagrande <milo.casagrande@linaro.org>
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
lava.parameter unit tests.
"""

import base64

from mock import patch

from lava.helper.tests.helper_test import HelperTest
from lava.parameter import (
    ListParameter,
    Parameter,
    UrlParameter,
)
from lava.tool.errors import CommandError


class GeneralParameterTest(HelperTest):
    """General class with setUp and tearDown methods for Parameter tests."""
    def setUp(self):
        super(GeneralParameterTest, self).setUp()
        # Patch class raw_input, start it, and stop it on tearDown.
        self.patcher1 = patch("lava.parameter.raw_input", create=True)
        self.mocked_raw_input = self.patcher1.start()

    def tearDown(self):
        super(GeneralParameterTest, self).tearDown()
        self.patcher1.stop()


class ParameterTest(GeneralParameterTest):
    """Tests for the Parameter class."""

    def setUp(self):
        super(ParameterTest, self).setUp()
        self.parameter1 = Parameter("foo", value="baz")

    def test_prompt_0(self):
        # Tests that when we have a value in the parameters and the user press
        # Enter, we get the old value back.
        self.mocked_raw_input.return_value = "\n"
        obtained = self.parameter1.prompt()
        self.assertEqual(self.parameter1.value, obtained)

    def test_prompt_1(self,):
        # Tests that with a value stored in the parameter, if and EOFError is
        # raised when getting user input, we get back the old value.
        self.mocked_raw_input.side_effect = EOFError()
        obtained = self.parameter1.prompt()
        self.assertEqual(self.parameter1.value, obtained)


class ListParameterTest(GeneralParameterTest):
    """Tests for the specialized ListParameter class."""

    def setUp(self):
        super(ListParameterTest, self).setUp()
        self.list_parameter = ListParameter("list")

    def test_prompt_0(self):
        # Test that when pressing Enter, the prompt stops and the list is
        # returned.
        expected = []
        self.mocked_raw_input.return_value = "\n"
        obtained = self.list_parameter.prompt()
        self.assertEqual(expected, obtained)

    def test_prompt_1(self):
        # Tests that when passing 3 values, a list with those values
        # is returned
        expected = ["foo", "bar", "foobar"]
        self.mocked_raw_input.side_effect = expected + ["\n"]
        obtained = self.list_parameter.prompt()
        self.assertEqual(expected, obtained)

    def test_serialize_0(self):
        # Tests the serialize method of ListParameter passing a list.
        expected = "foo,bar,baz,1"
        to_serialize = ["foo", "bar", "baz", "", 1]

        obtained = self.list_parameter.serialize(to_serialize)
        self.assertEqual(expected, obtained)

    def test_serialize_1(self):
        # Tests the serialize method of ListParameter passing an int.
        expected = "1"
        to_serialize = 1

        obtained = self.list_parameter.serialize(to_serialize)
        self.assertEqual(expected, obtained)

    def test_deserialize_0(self):
        # Tests the deserialize method of ListParameter with a string
        # of values.
        expected = ["foo", "bar", "baz"]
        to_deserialize = "foo,bar,,baz,"
        obtained = self.list_parameter.deserialize(to_deserialize)
        self.assertEqual(expected, obtained)

    def test_deserialize_1(self):
        # Tests the deserialization method of ListParameter passing a list.
        expected = ["foo", 1, "", "bar"]
        obtained = self.list_parameter.deserialize(expected)
        self.assertEqual(expected, obtained)


class UrlParameterTests(GeneralParameterTest):

    def setUp(self):
        super(UrlParameterTests, self).setUp()
        self.url_parameter = UrlParameter("url_par")

    def test_prompt_0(self):
        # User is asked the type of URL scheme, chooses the first one, then
        # enters the path of a file.
        self.mocked_raw_input.side_effect = ["1", self.temp_file.name, "\n"]
        expected = ["file://" + self.temp_file.name]
        obtained = self.url_parameter.prompt()
        self.assertEqual(expected, obtained)

    def test_prompt_1(self):
        # User is asked the tye of URL scheme: she types a wrong number, then
        # chooses number 2. She then enters the path to an empty file.
        self.mocked_raw_input.side_effect = ["100", "2", self.temp_file.name,
                                             "\n"]
        encoded_path = base64.encodestring(self.temp_file.name).strip()
        encoded_content = base64.encodestring("").strip()
        expected = ["data:" + encoded_path + ";" + encoded_content]
        obtained = self.url_parameter.prompt()
        self.assertEqual(expected, obtained)

    def test_prompt_2(self):
        # User is asked the tye of URL scheme: she types 2.
        # She then enters the path to a file with content.
        self.mocked_raw_input.side_effect = ["2", self.temp_file.name,
                                             "\n"]
        content_string = "some content for the file"
        with open(self.temp_file.name, "w") as write_file:
            write_file.write(content_string)
        encoded_path = base64.encodestring(self.temp_file.name).strip()
        encoded_content = base64.encodestring(content_string).strip()
        expected = ["data:" + encoded_path + ";" + encoded_content]
        obtained = self.url_parameter.prompt()
        self.assertEqual(expected, obtained)

    def test_base64_encode_with_no_file(self):
        # Pass a simple string and make sure it is encoded correctly.
        fake_file = "a_fake_non_existing_file.txt"
        self.assertRaises(CommandError, UrlParameter.base64encode, fake_file)

    def test_base64_encode_with_file(self):
        # Pass an existing file name, and make sure it is econded correctly.
        string_2_encode = "a data string to encode"
        with open(self.temp_file.name, "w") as write_file:
            write_file.write(string_2_encode)

        encoded_path = base64.encodestring(self.temp_file.name).strip()
        encoded_content = base64.encodestring(string_2_encode).strip()

        expected = ";".join([encoded_path, encoded_content])
        obtained = UrlParameter.base64encode(self.temp_file.name)

        self.assertEqual(expected, obtained)

    def test_base64_decode_with_file_content_string(self):
        # Tests that when passing a encoded string of a file path and its
        # content, only the file path is returned.
        expected = self.temp_file.name
        encoded_path = base64.encodestring(expected).strip()
        encoded_content = base64.encodestring("some content").strip()
        string_2_decode = ";".join([encoded_path, encoded_content])
        obtained = UrlParameter.base64decode(string_2_decode)
        self.assertEqual(expected, obtained)
