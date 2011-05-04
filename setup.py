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
import lava_tool


setup(
    name = 'launch-control-tool',
    version = versiontools.format_version(lava_tool.__version__),
    author = "Zygmunt Krynicki",
    author_email = "zygmunt.krynicki@linaro.org",
    packages = find_packages(),
    description = "Command line utility for Launch Control",
    url='https://launchpad.net/launch-control-tool',
    test_suite='lava_tool.tests.test_suite',
    license="LGPLv3",
    entry_points = """
    [console_scripts]
    lc-tool = lava_tool.dispatcher:main
    [lava_tool.commands]
    bundles = lava_tool.commands.dashboard:bundles
    deserialize = lava_tool.commands.dashboard:deserialize
    get = lava_tool.commands.dashboard:get
    help = lava_tool.commands.misc:help
    put = lava_tool.commands.dashboard:put
    server_version = lava_tool.commands.dashboard:server_version
    make_stream = lava_tool.commands.dashboard:make_stream
    backup = lava_tool.commands.dashboard:backup
    restore = lava_tool.commands.dashboard:restore
    pull = lava_tool.commands.dashboard:pull
    streams = lava_tool.commands.dashboard:streams
    data_views = lava_tool.commands.dashboard:data_views
    query_data_view = lava_tool.commands.dashboard:query_data_view
    version = lava_tool.commands.misc:version
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
