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
lava.config unit tests.
"""

import os
import sys
import tempfile

from StringIO import StringIO
from mock import MagicMock, patch, call

from lava.config import (
    Config,
    InteractiveConfig,
    ConfigParser,
)
from lava.helper.tests.helper_test import HelperTest
from lava.parameter import (
    Parameter,
    ListParameter,
)
from lava.tool.errors import CommandError


class MockedConfig(Config):
    """A subclass of the original Config class.

    Used to test the Config class, but to not have the same constructor in
    order to use temporary files for the configuration.
    """
    def __init__(self, config_file):
        self._cache = {}
        self._config_file = config_file
        self._config_backend = ConfigParser()
        self._config_backend.read([self._config_file])


class MockedInteractiveConfig(InteractiveConfig):
    def __init__(self, config_file, force_interactive=False):
        self._cache = {}
        self._config_file = config_file
        self._config_backend = ConfigParser()
        self._config_backend.read([self._config_file])
        self._force_interactive = force_interactive


class ConfigTestCase(HelperTest):
    """General test case class for the different Config classes."""
    def setUp(self):
        super(ConfigTestCase, self).setUp()
        self.config_file = tempfile.NamedTemporaryFile(delete=False)

        self.param1 = Parameter("foo")
        self.param2 = Parameter("bar", depends=self.param1)

    def tearDown(self):
        super(ConfigTestCase, self).tearDown()
        if os.path.isfile(self.config_file.name):
            os.unlink(self.config_file.name)


class ConfigTest(ConfigTestCase):

    def setUp(self):
        super(ConfigTest, self).setUp()
        self.config = MockedConfig(self.config_file.name)

    def test_assert_temp_config_file(self):
        # Dummy test to make sure we are overriding correctly the Config class.
        self.assertEqual(self.config._config_file, self.config_file.name)

    def test_config_put_in_cache_0(self):
        self.config._put_in_cache("key", "value", "section")
        self.assertEqual(self.config._cache["section"]["key"], "value")

    def test_config_get_from_cache_0(self):
        self.config._put_in_cache("key", "value", "section")
        obtained = self.config._get_from_cache(Parameter("key"), "section")
        self.assertEqual("value", obtained)

    def test_config_get_from_cache_1(self):
        self.config._put_in_cache("key", "value", "DEFAULT")
        obtained = self.config._get_from_cache(Parameter("key"), "DEFAULT")
        self.assertEqual("value", obtained)

    def test_config_put_0(self):
        # Puts a value in the DEFAULT section.
        self.config._put_in_cache = MagicMock()
        self.config.put("foo", "foo")
        expected = "foo"
        obtained = self.config._config_backend.get("DEFAULT", "foo")
        self.assertEqual(expected, obtained)

    def test_config_put_1(self):
        # Puts a value in a new section.
        self.config._put_in_cache = MagicMock()
        self.config.put("foo", "foo", "bar")
        expected = "foo"
        obtained = self.config._config_backend.get("bar", "foo")
        self.assertEqual(expected, obtained)

    def test_config_put_parameter_0(self):
        self.config._calculate_config_section = MagicMock(return_value="")
        self.assertRaises(CommandError, self.config.put_parameter, self.param1)

    @patch("lava.config.Config.put")
    def test_config_put_parameter_1(self, mocked_config_put):
        self.config._calculate_config_section = MagicMock(
            return_value="DEFAULT")

        self.param1.value = "bar"
        self.config.put_parameter(self.param1)

        self.assertEqual(mocked_config_put.mock_calls,
                         [call("foo", "bar", "DEFAULT")])

    def test_config_get_0(self):
        # Tests that with a non existing parameter, it returns None.
        param = Parameter("baz")
        self.config._get_from_cache = MagicMock(return_value=None)
        self.config._calculate_config_section = MagicMock(
            return_value="DEFAULT")

        expected = None
        obtained = self.config.get(param)
        self.assertEqual(expected, obtained)

    def test_config_get_1(self):
        self.config.put_parameter(self.param1, "foo")
        self.config._get_from_cache = MagicMock(return_value=None)
        self.config._calculate_config_section = MagicMock(
            return_value="DEFAULT")

        expected = "foo"
        obtained = self.config.get(self.param1)
        self.assertEqual(expected, obtained)

    def test_calculate_config_section_0(self):
        expected = "DEFAULT"
        obtained = self.config._calculate_config_section(self.param1)
        self.assertEqual(expected, obtained)

    def test_calculate_config_section_1(self):
        self.config.put_parameter(self.param1, "foo")
        expected = "foo=foo"
        obtained = self.config._calculate_config_section(self.param2)
        self.assertEqual(expected, obtained)

    def test_config_save(self):
        self.config.put_parameter(self.param1, "foo")
        self.config.save()

        expected = "[DEFAULT]\nfoo = foo\n\n"
        obtained = ""
        with open(self.config_file.name) as tmp_file:
            obtained = tmp_file.read()
        self.assertEqual(expected, obtained)

    @patch("lava.config.AT_EXIT_CALLS", spec=set)
    def test_config_atexit_call_list(self, mocked_calls):
        # Tests that the save() method is added to the set of atexit calls.
        config = Config()
        config._config_file = self.config_file.name
        config.put_parameter(self.param1, "foo")

        expected = [call.add(config.save)]

        self.assertEqual(expected, mocked_calls.mock_calls)


class InteractiveConfigTest(ConfigTestCase):

    def setUp(self):
        super(InteractiveConfigTest, self).setUp()
        self.config = MockedInteractiveConfig(
            config_file=self.config_file.name)

    @patch("lava.config.Config.get", new=MagicMock(return_value=None))
    def test_non_interactive_config_0(self):
        # Mocked config default is not to be interactive.
        # Try to get a value that does not exists, users just press enter when
        # asked for a value. Value will be empty.
        sys.stdin = StringIO("\n")
        value = self.config.get(Parameter("foo"))
        self.assertEqual("", value)

    @patch("lava.config.Config.get", new=MagicMock(return_value="value"))
    def test_non_interactive_config_1(self):
        # Parent class config returns a value, but we are not interactive.
        value = self.config.get(Parameter("foo"))
        self.assertEqual("value", value)

    @patch("lava.config.Config.get", new=MagicMock(return_value=None))
    def test_non_interactive_config_2(self):
        expected = "bar"
        sys.stdin = StringIO(expected)
        value = self.config.get(Parameter("foo"))
        self.assertEqual(expected, value)

    @patch("lava.config.Config.get", new=MagicMock(return_value="value"))
    def test_interactive_config_0(self):
        # We force to be interactive, meaning that even if a value is found,
        # it will be asked anyway.
        self.config._force_interactive = True
        expected = "a_new_value"
        sys.stdin = StringIO(expected)
        value = self.config.get(Parameter("foo"))
        self.assertEqual(expected, value)

    @patch("lava.config.Config.get", new=MagicMock(return_value="value"))
    def test_interactive_config_1(self):
        # Force to be interactive, but when asked for the new value press
        # Enter. The old value should be returned.
        self.config._force_interactive = True
        sys.stdin = StringIO("\n")
        value = self.config.get(Parameter("foo"))
        self.assertEqual("value", value)

    def test_calculate_config_section_0(self):
        self.config._force_interactive = True
        obtained = self.config._calculate_config_section(self.param1)
        expected = "DEFAULT"
        self.assertEqual(expected, obtained)

    def test_calculate_config_section_1(self):
        self.param2.depends.asked = True
        self.config._force_interactive = True
        self.config.put(self.param1.id, "foo")
        obtained = self.config._calculate_config_section(self.param2)
        expected = "foo=foo"
        self.assertEqual(expected, obtained)

    def test_calculate_config_section_2(self):
        self.config._force_interactive = True
        self.config._config_backend.get = MagicMock(return_value=None)
        sys.stdin = StringIO("baz")
        expected = "foo=baz"
        obtained = self.config._calculate_config_section(self.param2)
        self.assertEqual(expected, obtained)

    def test_calculate_config_section_3(self):
        # Tests that when a parameter has its value in the cache and also on
        # file, we honor the cached version.
        self.param2.depends.asked = True
        self.config._force_interactive = True
        self.config._get_from_cache = MagicMock(return_value="bar")
        self.config._config_backend.get = MagicMock(return_value="baz")
        expected = "foo=bar"
        obtained = self.config._calculate_config_section(self.param2)
        self.assertEqual(expected, obtained)

    @patch("lava.config.Config.get", new=MagicMock(return_value=None))
    @patch("lava.parameter.sys.exit")
    @patch("lava.parameter.raw_input", create=True)
    def test_interactive_config_exit(self, mocked_raw, mocked_sys_exit):
        self.config._calculate_config_section = MagicMock(
            return_value="DEFAULT")

        mocked_raw.side_effect = KeyboardInterrupt()

        self.config._force_interactive = True
        self.config.get(self.param1)
        self.assertTrue(mocked_sys_exit.called)

    @patch("lava.parameter.raw_input", create=True)
    def test_interactive_config_with_list_parameter(self, mocked_raw_input):
        # Tests that we get a list back in the Config class when using
        # ListParameter and that it contains the expected values.
        expected = ["foo", "bar"]
        mocked_raw_input.side_effect = expected + ["\n"]
        obtained = self.config.get(ListParameter("list"))
        self.assertIsInstance(obtained, list)
        self.assertEqual(expected, obtained)

    def test_interactive_save_list_param(self):
        # Tests that when saved to file, the ListParameter parameter is stored
        # correctly.
        param_values = ["foo", "more than one words", "bar"]
        list_param = ListParameter("list")
        list_param.value = param_values

        self.config.put_parameter(list_param, param_values)
        self.config.save()

        expected = "[DEFAULT]\nlist = " + ",".join(param_values) + "\n\n"
        obtained = ""
        with open(self.config_file.name, "r") as read_file:
            obtained = read_file.read()
        self.assertEqual(expected, obtained)
