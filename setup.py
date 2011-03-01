#!/usr/bin/env python
#
# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of launch-control-tool.
#
# launch-control-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# launch-control-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launch-control-tool.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import versiontools
import launch_control_tool


setup(
    name = 'launch-control-tool',
    version = versiontools.format_version(launch_control_tool.__version__),
    author = "Zygmunt Krynicki",
    author_email = "zygmunt.krynicki@linaro.org",
    packages = find_packages(),
    description = "Command line utility for Launch Control",
    url='https://launchpad.net/launch-control-tool',
    test_suite='launch_control_tool.tests.test_suite',
    license="LGPLv3",
    entry_points = """
    [console_scripts]
    lc-tool = launch_control_tool.dispatcher:main
    [launch_control_tool.commands]
    bundles = launch_control_tool.commands.dashboard:bundles
    deserialize = launch_control_tool.commands.dashboard:deserialize
    get = launch_control_tool.commands.dashboard:get
    help = launch_control_tool.commands.misc:help
    put = launch_control_tool.commands.dashboard:put
    server_version = launch_control_tool.commands.dashboard:server_version
    streams = launch_control_tool.commands.dashboard:streams
    version = launch_control_tool.commands.misc:version
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Testing",
    ],
    install_requires = [
        'versiontools >= 1.1',
        'argparse >= 1.1'
    ],
    setup_requires = [
        'versiontools >= 1.1',
    ],
    tests_require = [
    ],
    zip_safe = True,
)
