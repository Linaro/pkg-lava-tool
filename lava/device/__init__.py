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

from lava.device.templates import (
    KNOWN_TEMPLATES,
    DEFAULT_TEMPLATE,
)
from lava.tool.errors import CommandError


def __re_compile(name):
    """Creates a generic regex for the specified device name.

    :param name: The name of the device.
    :return A Pattern object.
    """
    return re.compile('^.*%s.*' % name, re.I)


# Dictionary of know devices.
# Keys are the general device name taken from lava.device.templates, values
# are tuples of: a regex matcher to match the device, and the device associated
# template.
KNOWN_DEVICES = dict([(device, (__re_compile(device), template))
                     for device, template in KNOWN_TEMPLATES.iteritems()])


class Device(object):
    """A generic device."""
    def __init__(self, hostname, template):
        self.device_type = None
        self.hostname = hostname
        self.template = template.copy()

    def write(self, conf_file):
        """Writes the object to file.

        :param conf_file: The full path of the file where to write."""
        with open(conf_file, 'w') as write_file:
            write_file.write(self.__str__())

    def _update(self):
        """Updates the template with the values specified for this class.

        Subclasses need to override this when they add more specific
        attributes.
        """
        # This is needed for the 'default' behavior. If we matched a known
        # device, we do not need to update its device_type, since its already
        # defined in the template.
        if self.device_type:
            self.template.update(hostname=self.hostname,
                                 device_type=self.device_type)
        else:
            self.template.update(hostname=self.hostname)

    def __str__(self):
        self._update()
        string_list = []
        for key, value in self.template.iteritems():
            if not value:
                value = ''
            string_list.append("%s = %s\n" % (str(key), str(value)))
        return "".join(string_list)

    def __repr__(self):
        self._update()
        return str(self.template)


def _get_device_type_from_user():
    """Makes the user write what kind of device this is.

    If something goes wrong, raises CommandError.
    """
    try:
        dev_type = raw_input("Please specify the device type: ").strip()
    except (EOFError, KeyboardInterrupt):
        dev_type = None
    if not dev_type:
        raise CommandError("DEVICE name not specified or not correct.")
    return dev_type


def get_known_device(name):
    """Tries to match a device name with a known device type.

    :param name: The name of the device we want matched to a real device.
    :return A Device instance.
        """
    instance = None
    for known_dev, (matcher, dev_template) in KNOWN_DEVICES.iteritems():
        if matcher.match(name):
            instance = Device(name, dev_template)
    if not instance:
        dev_type = _get_device_type_from_user()
        known_dev = KNOWN_DEVICES.get(dev_type, None)
        if known_dev:
            instance = Device(name, known_dev[1][1])
        else:
            print ("Device '%s' does not match a known device." % dev_type)
            instance = Device(name, DEFAULT_TEMPLATE)
            # Not stricly necessary, users can fill up the field later.
            instance.device_type = dev_type

    return instance
