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
Config class.
"""

import atexit
import os
import readline
import xdg.BaseDirectory as xdgBaseDir

from ConfigParser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
)

from lava.parameter import Parameter
from lava.tool.errors import CommandError

__all__ = ['Config', 'InteractiveCache', 'InteractiveConfig']

# Store for function calls to be made at exit time.
AT_EXIT_CALLS = set()
# Config default section.
DEFAULT_SECTION = "DEFAULT"
# This is the default base name used to create XDG resources.
DEFAULT_XDG_RESOURCE = "linaro"
# This is the default name for lava-tool resources.
DEFAULT_LAVA_TOOL_RESOURCE = "lava-tool"

HISTORY = os.path.join(os.path.expanduser("~"), ".lava_history")
try:
    readline.read_history_file(HISTORY)
except IOError:
    pass
atexit.register(readline.write_history_file, HISTORY)


def _run_at_exit():
    """Runs all the function at exit."""
    for call in list(AT_EXIT_CALLS):
        call()
atexit.register(_run_at_exit)


class Config(object):
    """A generic config object."""

    def __init__(self):
        # The cache where to store parameters.
        self._cache = {}
        self._config_file = None
        self._config_backend = None
        AT_EXIT_CALLS.add(self.save)

    @property
    def config_file(self):
        if self._config_file is None:
            self._config_file = (os.environ.get('LAVACONFIG') or
                                 os.path.join(self._ensure_xdg_dirs(),
                                              'lava-tool.ini'))
        return self._config_file

    @config_file.setter
    def config_file(self, value):
        self._config_file = value

    @property
    def config_backend(self):
        if self._config_backend is None:
            self._config_backend = ConfigParser()
            self._config_backend.read([self.config_file])
        return self._config_backend

    def _ensure_xdg_dirs(self):
        """Make sure we have the default resource.

        :return The path to the XDG resource.
        """
        return xdgBaseDir.save_config_path(DEFAULT_XDG_RESOURCE,
                                           DEFAULT_LAVA_TOOL_RESOURCE)

    def _calculate_config_section(self, parameter):
        """Calculates the config section of the specified parameter.

        :param parameter: The parameter to calculate the section of.
        :type Parameter
        :return The config section.
        """
        section = DEFAULT_SECTION
        if parameter.depends:
            section = "{0}={1}".format(parameter.depends.id,
                                       self.get(parameter.depends))
        return section

    def get(self, parameter, section=None):
        """Retrieves a Parameter value.

        The value is taken either from the Parameter itself, or from the cache,
        or from the config file.

        :param parameter: The parameter to search.
        :type Parameter
        :return The parameter value, or None if it is not found.
        """
        if not section:
            section = self._calculate_config_section(parameter)
        # Try to get the parameter value first if it has one.
        if parameter.value is not None:
            value = parameter.value
        else:
            value = self._get_from_cache(parameter, section)

        if value is None:
            value = self._get_from_backend(parameter, section)
        return value

    def get_from_backend(self, parameter, section=None):
        """Gets a configuration parameter directly from the config file."""
        if not section:
            section = self._calculate_config_section(parameter)
        return self._get_from_backend(parameter, section)

    def _get_from_backend(self, parameter, section):
        """Gets the parameter value from the config backend.

        :param parameter: The Parameter to look up.
        :param section: The section in the Config.
        """
        value = None
        try:
            value = self.config_backend.get(section, parameter.id)
        except (NoOptionError, NoSectionError):
            # Ignore, we return None.
            pass
        return value

    def _get_from_cache(self, parameter, section):
        """Looks for the specified parameter in the internal cache.

        :param parameter: The parameter to search.
        :type Parameter
        :return The parameter value, of None if it is not found.
        """
        value = None
        if section in self._cache.keys():
            if parameter.id in self._cache[section].keys():
                value = self._cache[section][parameter.id]
        return value

    def _put_in_cache(self, key, value, section=DEFAULT_SECTION):
        """Insert the passed parameter in the internal cache.

        :param parameter: The parameter to insert.
        :type Parameter
        :param section: The name of the section in the config file.
        :type str
        """
        if section not in self._cache.keys():
            self._cache[section] = {}
        self._cache[section][key] = value

    def put(self, key, value, section=DEFAULT_SECTION):
        """Adds a parameter to the config file.

        :param key: The key to add.
        :param value: The value to add.
        :param section: The name of the section as in the config file.
        """
        if (not self.config_backend.has_section(section) and
                section != DEFAULT_SECTION):
            self.config_backend.add_section(section)

        # This is done to serialize a list when ConfigParser is written to
        # file. Since there is no real support for list in ConfigParser, we
        # serialized it in a common way that can get easily deserialized.
        if isinstance(value, list):
            value = Parameter.serialize(value)

        self.config_backend.set(section, key, value)
        # Store in the cache too.
        self._put_in_cache(key, value, section)

    def put_parameter(self, parameter, value=None, section=None):
        """Adds a Parameter to the config file and cache.

        :param Parameter: The parameter to add.
        :type Parameter
        :param value: The value of the parameter. Defaults to None.
        :param section: The section where this parameter should be stored.
                        Defaults to None.
        """
        if not section:
            section = self._calculate_config_section(parameter)

        if value is None and parameter.value is not None:
            value = parameter.value
        elif value is None:
            raise CommandError("No value assigned to '{0}'.".format(
                parameter.id))
        self.put(parameter.id, value, section)

    def save(self):
        """Saves the config to file."""
        # Since we lazy load the config_backend property, this check is needed
        # when a user enters a wrong command or it will overwrite the 'config'
        # file with empty contents.
        if self._config_backend:
            with open(self.config_file, "w") as write_file:
                self.config_backend.write(write_file)


class InteractiveConfig(Config):
    """An interactive config.

    If a value is not found in the config file, it will ask it and then stores
    it.
    """
    def __init__(self, force_interactive=True):
        super(InteractiveConfig, self).__init__()
        self._force_interactive = force_interactive

    @property
    def force_interactive(self):
        return self._force_interactive

    @force_interactive.setter
    def force_interactive(self, value):
        self._force_interactive = value

    def get(self, parameter, section=None):
        """Overrides the parent one.

        The only difference with the parent one, is that it will ask to type
        a parameter value in case it is not found.
        """
        if not section:
            section = self._calculate_config_section(parameter)
        value = super(InteractiveConfig, self).get(parameter, section)

        if value is None or self.force_interactive:
            value = parameter.prompt(old_value=value)

        if value is not None and parameter.store:
            self.put(parameter.id, value, section)
        return value


class InteractiveCache(InteractiveConfig):

    """An interactive cache where parameters that can change are stored.

    This class is basically the same as the Confing and InteractiveConfig ones,
    only the base directory where the cache file is stored is different.

    In this case it will use the $XDG_CACHE_HOME value as defined in XDG.
    """

    @property
    def config_file(self):
        if self._config_file is None:
            self._config_file = (os.environ.get('LAVACACHE') or
                                 os.path.join(self._ensure_xdg_dirs(),
                                              'parameters.ini'))
        return self._config_file

    @config_file.setter
    def config_file(self, value):
        self._config_file = value

    def _ensure_xdg_dirs(self):
        """Make sure we have the default resource.

        :return The path to the XDG resource.
        """
        return xdgBaseDir.save_cache_path(DEFAULT_XDG_RESOURCE,
                                          DEFAULT_LAVA_TOOL_RESOURCE)
