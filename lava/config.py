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
import sys


from ConfigParser import ConfigParser, NoOptionError, NoSectionError

__all__ = ['Config', 'InteractiveConfig']

# Store for function calls to be made at exit time.
AT_EXIT_CALLS = set()
# Config default section.
DEFAULT_SECTION = "DEFAULT"

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


class Parameter(object):
    """A parameter with optional dependencies."""
    def __init__(self, id, depends=None):
        self.id = id
        self.depends = depends


class Config(object):
    """A generic config object."""
    def __init__(self):
        # The cache where to store parameters.
        self._cache = {}
        self._config_file = (os.environ.get('LAVACONFIG') or
                             os.path.join(os.path.expanduser('~'),
                                          '.lavaconfig'))
        self._config_backend = ConfigParser()
        self._config_backend.read([self._config_file])
        AT_EXIT_CALLS.add(self.save)

    def _calculate_config_section(self, parameter):
        """Calculates the config section of the specified parameter.

        :param parameter: The parameter to calculate the section of.
        :type Parameter
        :return The config section.
        """
        config_section = DEFAULT_SECTION
        if parameter.depends:
            config_section = "{0}={1}".format(parameter.depends.id,
                                              self.get(parameter.depends))
        return config_section

    def get(self, parameter):
        """Retrieves a Parameter from the config file.

        :param parameter: The parameter to search.
        :type Parameter
        :return The parameter value, or None if it is not found.
        """
        config_section = self._calculate_config_section(parameter)
        value = self._get_from_cache(parameter, config_section)

        if not value:
            try:
                value = self._config_backend.get(config_section, parameter.id)
            except (NoOptionError, NoSectionError):
                # Ignore, we return None since value is already None.
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

    def _put_in_cache(self, key, value, section):
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
        if (not self._config_backend.has_section(section) and
                section != DEFAULT_SECTION):
            self._config_backend.add_section(section)
        self._config_backend.set(section, key, value)
        # Store in the cache too.
        self._put_in_cache(key, value, section)

    def put_parameter(self, parameter, value):
        """Adds a Parameter to the config file and cache.

        :param Parameter: The parameter to add.
        :param value: The value of the parameter.
        """
        config_section = self._calculate_config_section(parameter)
        self.put(parameter.id, value, config_section)

    def save(self):
        """Saves the config to file."""
        with open(self._config_file, "w") as write_file:
            self._config_backend.write(write_file)


class InteractiveConfig(Config):
    """An interactive config.

    If a value is not found in the config file, it will ask it and then stores
    it.
    """
    def __init__(self, force_interactive=False):
        super(InteractiveConfig, self).__init__()
        self._force_interactive = force_interactive

    def _calculate_config_section(self, parameter):
        """Calculates the config section of the specified parameter.

        :param parameter: The parameter to calculate the section of.
        :type Parameter
        :return The config section.
        """
        config_section = DEFAULT_SECTION
        if parameter.depends:
            # This is mostly relevant to the InteractiveConfig class.
            # If a parameter has a dependencies we do as follows:
            # - Get the dependency cached value
            # - Get the dependency value from the config file
            # - If both are None, it means the dependency has not been inserted
            #   yet, and we ask for it.
            cached_value = self._get_from_cache(
                parameter.depends,
                self._calculate_config_section(parameter.depends))

            config_value = self._config_backend.get(
                self._calculate_config_section(parameter.depends),
                parameter.depends.id)

            value = cached_value or config_value
            if not value:
                value = self.get(parameter.depends)
            config_section = "{0}={1}".format(parameter.depends.id, value)
        return config_section

    def get(self, parameter):
        """Overrides the parent one.

        The only difference with the parent one, is that it will ask to type
        a parameter value in case it is not found.
        """
        value = super(InteractiveConfig, self).get(parameter)

        if value and self._force_interactive:
            prompt = "Reinsert value for {0} [was: {1}]: ".format(
                parameter.id,
                value)
        else:
            prompt = "Insert value for {0}: ".format(parameter.id)

        if not value or self._force_interactive:
            config_section = self._calculate_config_section(parameter)

            try:
                user_input = raw_input(prompt).strip()
            except EOFError:
                user_input = None
            except KeyboardInterrupt:
                sys.exit(-1)

            if user_input:
                value = user_input
                self.put(parameter.id, value, config_section)
        return value
