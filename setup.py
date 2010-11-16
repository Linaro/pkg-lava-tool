#!/usr/bin/env python
#
# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of Launch Control.
#
# Launch Control is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# Launch Control is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Launch Control.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

from launch_control_tool import get_version


setup(
    name = 'launch_control_tool',
    version = get_version(),
    author = "Zygmunt Krynicki",
    author_email = "zygmunt.krynicki@linaro.org",
    packages = find_packages(),
    scripts = ['lc-tool.py'],
    description = "Command line utility for launch-control",
    url='https://launchpad.net/launch-control-tool',
    test_suite='launch_control_tool.tests.test_suite',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Testing",
    ],
)
