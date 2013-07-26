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

from mock import patch

from lava.helper.tests.helper_test import HelperTest
from lava.parameter import (
    ListParameter,
    Parameter,
    SingleChoiceParameter,
)
from lava_tool.utils import to_list


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

    def test_to_list_0(self):
        value = "a_value"
        expected = [value]
        obtained = to_list(value)
        self.assertIsInstance(obtained, list)
        self.assertEquals(expected, obtained)

    def test_to_list_1(self):
        expected = ["a_value", "b_value"]
        obtained = to_list(expected)
        self.assertIsInstance(obtained, list)
        self.assertEquals(expected, obtained)


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

    def test_set_value_0(self):
        # Pass a string to a ListParameter, expect a list.
        set_value = "foo"
        expected = [set_value]
        self.list_parameter.set(set_value)
        self.assertEquals(expected, self.list_parameter.value)

    def test_set_value_1(self):
        # Pass a list to a ListParameter, expect the same list.
        expected = ["foo", "bar"]
        self.list_parameter.set(expected)
        self.assertEquals(expected, self.list_parameter.value)

    def test_add_value_0(self):
        # Add a value to a ListParameter, expect a list back.
        add_value = "foo"
        expected = [add_value]
        self.list_parameter.add(add_value)
        self.assertEquals(expected, self.list_parameter.value)

    def test_add_value_1(self):
        # Add a list value to a ListParameter with already a value set, expect
        # a list with both values.
        # The ListParameter is initialized with a string.
        add_value = ["foo"]
        list_param = ListParameter("list", value="bar")
        expected = ["bar", "foo"]
        list_param.add(add_value)
        self.assertEquals(expected, list_param.value)

    def test_add_value_2(self):
        # Add a list value to a ListParameter with already a value set, expect
        # a list with both values.
        # The ListParameter is initialized with a list.
        add_value = ["foo"]
        list_param = ListParameter("list", value=["bar", "baz"])
        expected = ["bar", "baz", "foo"]
        list_param.add(add_value)
        self.assertEquals(expected, list_param.value)


class TestsSingleChoiceParameter(GeneralParameterTest):

    def setUp(self):
        super(TestsSingleChoiceParameter, self).setUp()
        self.choices = ["foo", "bar", "baz", "bam"]
        self.param_id = "single_choice"
        self.single_choice_param = SingleChoiceParameter(self.param_id,
                                                         self.choices)

    def test_with_old_value(self):
        # There is an old value for a single choice parameter, the user
        # is prompted to select from the list of values, but she presses
        # enter. The old value is returned.
        old_value = "bat"
        self.mocked_raw_input.side_effect = ["\n"]
        obtained = self.single_choice_param.prompt("", old_value=old_value)
        self.assertEquals(old_value, obtained)

    def test_without_old_value(self):
        # There is no old value, user just select the first choice.
        self.mocked_raw_input.side_effect = ["1"]
        obtained = self.single_choice_param.prompt("")
        self.assertEquals("foo", obtained)

    def test_with_wrong_user_input(self):
        # No old value, user inserts at least two wrong choices, and the select
        # the third one.
        self.mocked_raw_input.side_effect = ["1000", "0", "3"]
        obtained = self.single_choice_param.prompt("")
        self.assertEquals("baz", obtained)
