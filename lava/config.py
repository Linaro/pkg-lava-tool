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

import atexit
from ConfigParser import ConfigParser, NoOptionError, NoSectionError
import os
import readline

__all__ = ['InteractiveConfig', 'NonInteractiveConfig']

history = os.path.join(os.path.expanduser("~"), ".lava_history")
try:
    readline.read_history_file(history)
except IOError:
    pass
atexit.register(readline.write_history_file, history)

config_file = (os.environ.get('LAVACONFIG') or
               os.path.join(os.path.expanduser('~'), '.lavaconfig'))
config_backend = ConfigParser()
config_backend.read([config_file])


def save_config():
    with open(config_file, 'w') as f:
        config_backend.write(f)
atexit.register(save_config)


class Parameter(object):

    def __init__(self, id, depends=None):
        self.id = id
        self.depends = depends


class InteractiveConfig(object):

    def __init__(self, force_interactive=False):
        self._force_interactive = force_interactive
        self._cache = {}

    def get(self, parameter):
        key = parameter.id
        value = None
        if parameter.depends:
            pass
            config_section = parameter.depends.id + '=' + self.get(parameter.depends)
        else:
            config_section = "DEFAULT"

        if config_section in self._cache:
            if key in self._cache[config_section]:
                return self._cache[config_section][key]

        prompt = '%s: ' % key

        try:
            value = config_backend.get(config_section, key)
        except (NoOptionError, NoSectionError):
            pass
        if value:
            if self._force_interactive:
                prompt = "%s[%s]: " % (key, value)
            else:
                return value
        try:
            user_input = raw_input(prompt).strip()
        except EOFError:
            user_input = None
        if user_input:
            value = user_input
            if not config_backend.has_section(config_section) and config_section != 'DEFAULT':
                config_backend.add_section(config_section)
            config_backend.set(config_section, key, value)

        if value:
            if config_section not in self._cache:
                self._cache[config_section] = {}
            self._cache[config_section][key] = value
            return value
        else:
            raise KeyError(key)

class NonInteractiveConfig(object):

    def __init__(self, data):
        self.data = data

    def get(self, parameter):
        return self.data[parameter.id]
