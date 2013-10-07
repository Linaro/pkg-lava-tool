# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
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
Package with unit tests for lava_tool
"""

import doctest
import unittest


def app_modules():
    return [
        'lava_tool.commands',
        'lava_tool.dispatcher',
        'lava_tool.interface',
        'lava_dashboard_tool.commands',
    ]


def test_modules():
    return [
        'lava.device.tests.test_commands',
        'lava.device.tests.test_device',
        'lava.helper.tests.test_command',
        'lava.helper.tests.test_dispatcher',
        'lava.helper.tests.test_template',
        'lava.job.tests.test_commands',
        'lava.job.tests.test_job',
        'lava.script.tests.test_commands',
        'lava.script.tests.test_script',
        'lava.testdef.tests.test_commands',
        'lava.tests.test_commands',
        'lava.tests.test_config',
        'lava.tests.test_parameter',
        'lava_dashboard_tool.tests.test_commands',
        'lava_tool.tests.test_auth_commands',
        'lava_tool.tests.test_authtoken',
        'lava_tool.tests.test_commands',
        'lava_tool.tests.test_utils',
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
