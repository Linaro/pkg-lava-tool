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

""" """

import copy
from unittest import TestCase

from lava.helper.template import (
    get_key,
    set_value
)


TEST_TEMPLATE = {
    "key1": "value1",
    "key2": [
        "value2", "value3"
    ],
    "key3": [
        {
            "key4": "value4",
            "key5": "value5"
        },
        {
            "key6": "value6",
            "key7": "value7"
        },
        [
            {
                "key8": "value8"
            }
        ]
    ],
    "key10": {
        "key11": "value11"
    }
}


class TestParameter(TestCase):

    def test_get_key_simple_key(self):
        expected = "value1"
        obtained = get_key(TEST_TEMPLATE, "key1")
        self.assertEquals(expected, obtained)

    def test_get_key_nested_key(self):
        expected = "value4"
        obtained = get_key(TEST_TEMPLATE, "key4")
        self.assertEquals(expected, obtained)

    def test_get_key_nested_key_1(self):
        expected = "value7"
        obtained = get_key(TEST_TEMPLATE, "key7")
        self.assertEquals(expected, obtained)

    def test_get_key_nested_key_2(self):
        expected = "value8"
        obtained = get_key(TEST_TEMPLATE, "key8")
        self.assertEquals(expected, obtained)

    def test_get_key_nested_key_3(self):
        expected = "value11"
        obtained = get_key(TEST_TEMPLATE, "key11")
        self.assertEquals(expected, obtained)

    def test_set_value_0(self):
        data = copy.deepcopy(TEST_TEMPLATE)
        expected = "foo"
        set_value(data, "key1", expected)
        obtained = get_key(data, "key1")
        self.assertEquals(expected, obtained)

    def test_set_value_1(self):
        data = copy.deepcopy(TEST_TEMPLATE)
        expected = "foo"
        set_value(data, "key6", expected)
        obtained = get_key(data, "key6")
        self.assertEquals(expected, obtained)

    def test_set_value_2(self):
        data = copy.deepcopy(TEST_TEMPLATE)
        expected = "foo"
        set_value(data, "key11", expected)
        obtained = get_key(data, "key11")
        self.assertEquals(expected, obtained)
