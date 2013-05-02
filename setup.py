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
    entry_points="""
    [console_scripts]
    lava-tool = lava_tool.dispatcher:main
    lava = lava.tool.main:LavaDispatcher.run
    lava-dashboard-tool=lava_dashboard_tool.main:main
    [lava.commands]
    help = lava.tool.commands.help:help
    scheduler = lava_scheduler_tool.commands:scheduler
    dashboard = lava_dashboard_tool.commands:dashboard
    [lava_tool.commands]
    help = lava.tool.commands.help:help
    auth-add = lava_tool.commands.auth:auth_add
    submit-job = lava_scheduler_tool.commands:submit_job
    resubmit-job = lava_scheduler_tool.commands:resubmit_job
    cancel-job = lava_scheduler_tool.commands:cancel_job
    job-output = lava_scheduler_tool.commands:job_output
    backup=lava_dashboard_tool.commands:backup
    bundles=lava_dashboard_tool.commands:bundles
    data_views=lava_dashboard_tool.commands:data_views
    deserialize=lava_dashboard_tool.commands:deserialize
    get=lava_dashboard_tool.commands:get
    make_stream=lava_dashboard_tool.commands:make_stream
    pull=lava_dashboard_tool.commands:pull
    put=lava_dashboard_tool.commands:put
    query_data_view=lava_dashboard_tool.commands:query_data_view
    restore=lava_dashboard_tool.commands:restore
    server_version=lava_dashboard_tool.commands:server_version
    streams=lava_dashboard_tool.commands:streams
    version=lava_dashboard_tool.commands:version
    [lava.scheduler.commands]
    submit-job = lava_scheduler_tool.commands:submit_job
    resubmit-job = lava_scheduler_tool.commands:resubmit_job
    cancel-job = lava_scheduler_tool.commands:cancel_job
    job-output = lava_scheduler_tool.commands:job_output
    [lava.dashboard.commands]
    backup=lava_dashboard_tool.commands:backup
    bundles=lava_dashboard_tool.commands:bundles
    data_views=lava_dashboard_tool.commands:data_views
    deserialize=lava_dashboard_tool.commands:deserialize
    get=lava_dashboard_tool.commands:get
    make_stream=lava_dashboard_tool.commands:make_stream
    pull=lava_dashboard_tool.commands:pull
    put=lava_dashboard_tool.commands:put
    query_data_view=lava_dashboard_tool.commands:query_data_view
    restore=lava_dashboard_tool.commands:restore
    server_version=lava_dashboard_tool.commands:server_version
    streams=lava_dashboard_tool.commands:streams
    version=lava_dashboard_tool.commands:version
    [lava_dashboard_tool.commands]
    backup=lava_dashboard_tool.commands:backup
    bundles=lava_dashboard_tool.commands:bundles
    data_views=lava_dashboard_tool.commands:data_views
    deserialize=lava_dashboard_tool.commands:deserialize
    get=lava_dashboard_tool.commands:get
    make_stream=lava_dashboard_tool.commands:make_stream
    pull=lava_dashboard_tool.commands:pull
    put=lava_dashboard_tool.commands:put
    query_data_view=lava_dashboard_tool.commands:query_data_view
    restore=lava_dashboard_tool.commands:restore
    server_version=lava_dashboard_tool.commands:server_version
    streams=lava_dashboard_tool.commands:streams
    version=lava_dashboard_tool.commands:version
    """,
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
        'argparse >= 1.1',
        'keyring',
        'json-schema-validator >= 2.0',
        'versiontools >= 1.3.1'
    ],
    setup_requires=['versiontools >= 1.3.1'],
    tests_require=['mocker >= 1.0'],
    zip_safe=True)
