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

import re

from copy import deepcopy

from lava.config import Config
from lava.device.templates import (
    DEFAULT_TEMPLATE,
    HOSTNAME_PARAMETER,
    KNOWN_TEMPLATES,
    update_template,
)
from lava.tool.errors import CommandError


def __re_compile(name):
    """Creates a generic regex for the specified device name.

    :param name: The name of the device.
    :return A Pattern object.
    """
    return re.compile('^.*{0}.*'.format(name), re.I)


# Dictionary of know devices.
# Keys are the general device name taken from lava.device.templates, values
# are tuples of: a regex matcher to match the device, and the device associated
# template.
KNOWN_DEVICES = dict([(device, (__re_compile(device), template))
                     for device, template in KNOWN_TEMPLATES.iteritems()])


class Device(object):
    """A generic device."""
    def __init__(self, hostname=None, template=None):
        self.hostname = hostname
        self.template = deepcopy(template)

    def write(self, conf_file):
        """Writes the object to file.

        :param conf_file: The full path of the file where to write."""
        with open(conf_file, 'w') as write_file:
            write_file.write(str(self))

    def update(self, config):
        """Updates the Device object values based on the provided config.

        :param config: A Config instance.
        """
        if not isinstance(config, Config):
            raise CommandError("Error updating the device values.")

        # We should always have a hostname, since it defaults to the name
        # given on the command line for the config file.
        if self.hostname:
            config._put_in_cache(HOSTNAME_PARAMETER.id, self.hostname, "DEFAULT")

        update_template(self.template, config)

    def __str__(self):
        string_list = []
        for key, value in self.template.iteritems():
            string_list.append("{0} = {1}\n".format(str(key), str(value)))
        return "".join(string_list)


def get_known_device(name):
    """Tries to match a device name with a known device type.

    :param name: The name of the device we want matched to a real device.
    :return A Device instance.
        """
    instance = Device(name, DEFAULT_TEMPLATE)
    for known_dev, (matcher, dev_template) in KNOWN_DEVICES.iteritems():
        if matcher.match(name):
            instance = Device(name, dev_template)
            break
    return instance
