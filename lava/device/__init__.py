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

from lava.tool.errors import CommandError


class Device(object):
    """A generic device."""
    def __init__(self, name):
        super(Device, self).__init__()
        self.device_type = None
        self.hostname = name

    def write(where):
        """Writes the object to file.

        :param where: The full path of the file where to write."""
        with open(where, 'w') as f:
            # TODO need a way to serialized the object
            f.write('')


class PandaDevice(Device):
    """A panda device."""
    def __init__(self, name):
        super(PandaDevice, self).__init__(name)
        self.device_type = 'panda'


# Dictionary with key the name of a know device, and value a tuple composed of
# a matcher used to guess the device type, and its associated Device class.
known_devices = {
    'panda': (re.compile('^panda'), PandaDevice),
}


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


def get_known_device(device):
    """Tries to match a device name with a known device type.

    :param device: The name of the device we want matched to a real device.
    :return Its special Device instance, or a general one.
        """
    instance = None
    for known_dev, (matcher, clazz) in known_devices.iteritems():
        if matcher.match(device):
            instance = clazz(device)
    if not instance:
        dev_type = _get_device_type_from_user()
        known_dev = known_devices.get(dev_type, None)
        if known_dev:
            clazz = known_dev[1]
            instance = clazz(device)
        else:
            print ("Device '%s' does not match a known device." % dev_type)
            instance = Device(device)
            instance.device_type = dev_type

    return instance


if __name__ == '__main__':
    instance = get_known_device('pippo')
    print instance.device_type, instance.hostname
