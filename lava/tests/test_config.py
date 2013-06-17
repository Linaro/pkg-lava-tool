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
Config class unit tests.
"""

import os
import sys
import tempfile

from StringIO import StringIO
from unittest import TestCase
from mock import MagicMock, patch, call

from lava.config import (
    Config,
    InteractiveConfig,
    ConfigParser,
    Parameter,
)


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


class TestInteractiveConfig(InteractiveConfig):
    def __init__(self, config_file, force_interactive=False):
        self._cache = {}
        self._config_file = config_file
        self._config_backend = ConfigParser()
        self._config_backend.read([self._config_file])
        self._force_interactive = force_interactive


class ConfigTest(TestCase):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(delete=False)
        self.config = MockedConfig(self.config_file.name)

        self.param1 = Parameter("foo")
        self.param2 = Parameter("bar", depends=self.param1)

    def tearDown(self):
        if os.path.isfile(self.config_file.name):
            os.unlink(self.config_file.name)

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


class InteractiveConfigTest(TestCase):

    def setUp(self):
        self.config_file = tempfile.NamedTemporaryFile(delete=False)
        self.config = TestInteractiveConfig(config_file=self.config_file.name)

        self.original_stdin = sys.stdin
        self.original_stdout = sys.stdout
        sys.stdout = open(os.path.devnull, "w")
        self.original_stderr = sys.stderr
        sys.stderr = open(os.path.devnull, "w")

    def tearDown(self):
        if os.path.isfile(self.config_file.name):
            os.unlink(self.config_file.name)

        sys.stdin = self.original_stdin
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

    @patch("lava.config.Config.get", new=MagicMock(return_value=None))
    def test_non_interactive_config_0(self):
        # Default is not to be interactive.
        # Try to get a value that does not exists, users just press enter when
        # asked for a value.
        sys.stdin = StringIO("\n")
        value = self.config.get(Parameter("foo"))
        self.assertEqual(None, value)

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

    def test_non_interactive_config_3(self):
        self.fail()
