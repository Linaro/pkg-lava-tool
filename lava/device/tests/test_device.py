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
Device class unit tests.
"""

from unittest import TestCase

from lava.device import (
    PandaDevice,
    get_known_device,
)


class DeviceTest(TestCase):

    def test_get_known_device_panda(self):
        instance = get_known_device('panda_new_01')
        self.assertIsInstance(instance, PandaDevice)

    def test_get_known_device_unknown(self):
        pass
