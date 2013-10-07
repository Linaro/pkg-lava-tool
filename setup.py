#!/usr/bin/env python
#
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

from setuptools import setup, find_packages
from os.path import dirname, join

entry_points = open(join(dirname(__file__), 'entry_points.ini')).read()

setup(
    name='lava-tool',
    version=":versiontools:lava.tool:__version__",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    namespace_packages=['lava'],
    packages=find_packages(),
    description="Command line utility for Linaro validation services",
    url='https://launchpad.net/lava-tool',
    test_suite='lava_tool.tests.test_suite',
    license="LGPLv3",
    entry_points=entry_points,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=[
        'PyYAML >= 3.10',
        'argparse >= 1.1',
        'argcomplete >= 0.3',
        'keyring',
        'json-schema-validator >= 2.0',
        'versiontools >= 1.3.1',
        'pyxdg == 0.25',
    ],
    setup_requires=['versiontools >= 1.3.1'],
    tests_require=[
        'mocker >= 1.0',
        'mock >= 0.7.2'
    ],
    zip_safe=True)
