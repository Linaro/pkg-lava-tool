# Copyright (c) 2010 Linaro
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of Launch Control.
#
# Launch Control is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Launch Control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Launch Control.  If not, see <http://www.gnu.org/licenses/>.

"""
Package with unit tests for launch_control
"""

import doctest
import unittest


def app_modules():
    return [
            'launch_control.commands',
            'launch_control.commands.dashboard',
            'launch_control.commands.dispatcher',
            'launch_control.commands.interface',
            'launch_control.commands.misc',
            'launch_control.models',
            'launch_control.models.bundle',
            'launch_control.models.hw_context',
            'launch_control.models.hw_device',
            'launch_control.models.sw_context',
            'launch_control.models.sw_image',
            'launch_control.models.sw_package',
            'launch_control.models.test_case',
            'launch_control.models.test_result',
            'launch_control.models.test_run',
            'launch_control.utils.call_helper',
            'launch_control.utils.filesystem',
            'launch_control.utils.import_prohibitor',
            'launch_control.utils.json',
            'launch_control.utils.json.decoder',
            'launch_control.utils.json.encoder',
            'launch_control.utils.json.impl',
            'launch_control.utils.json.interface',
            'launch_control.utils.json.pod',
            'launch_control.utils.json.proxies',
            'launch_control.utils.json.proxies.datetime',
            'launch_control.utils.json.proxies.decimal',
            'launch_control.utils.json.proxies.timedelta',
            'launch_control.utils.json.proxies.uuid',
            'launch_control.utils.json.registry',
            'launch_control.utils.registry',
            ]


def test_modules():
    return [
            'launch_control.tests.test_commands',
            'launch_control.tests.test_dashboard_bundle_format_1_0',
            'launch_control.tests.test_registry',
            'launch_control.tests.test_utils_filesystem',
            'launch_control.tests.test_utils_json_package',
            ]


def test_suite():
    """
    Build an unittest.TestSuite() object with all the tests in _modules.
    Each module is harvested for both regular unittests and doctests
    """
    modules = app_modules() + test_modules()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in modules:
        unit_suite = loader.loadTestsFromName(name)
        suite.addTests(unit_suite)
        doc_suite = doctest.DocTestSuite(name)
        suite.addTests(doc_suite)
    return suite
