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

import sys

from StringIO import StringIO
from mock import patch

from lava.helper.tests.helper_test import HelperTest
from lava.parameter import (
    ListParameter,
    Parameter,
)


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
        sys.stdin = StringIO("\n")
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
        # Tests that when passing 3 values, a list which contains them is
        # returned.
        expected = ["foo", "bar", "foobar"]
        self.mocked_raw_input.side_effect = expected + ["\n"]
        obtained = self.list_parameter.prompt()
        self.assertEqual(expected, obtained)
