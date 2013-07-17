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

"""Test definition templates."""

from lava.parameter import (
    ListParameter,
    Parameter,
)

DEFAULT_TESTDEF_FILE = "lavatest.yaml"

DEFAULT_TESTDEF_VERSION = "1.0"
DEFAULT_TESTDEF_FORMAT = "Lava-Test Test Definition 1.0"

# This is what will be called by default by the test definition yaml file.
DEFAULT_TESTDEF_SCRIPT = "mytest.sh"
DEFAULT_TESTDEF_SCRIPT_CONTENT = """#!/bin/sh
# Automatic generated content by lava-tool.
# Please add your own instructions.
"""
DEFAULT_TESTDEF_STEP = "./mytest.sh"

DEFAULT_ENVIRONMET_VALUE = "lava_test_shell"

# All these parameters will not be stored on the local config file.
NAME_PARAMETER = Parameter("name")
NAME_PARAMETER.store = False

DESCRIPTION_PARAMETER = Parameter("description", depends=NAME_PARAMETER)
DESCRIPTION_PARAMETER.store = False

ENVIRONMENT_PARAMETER = ListParameter("environment",
                                      depends=NAME_PARAMETER)
ENVIRONMENT_PARAMETER.add(DEFAULT_ENVIRONMET_VALUE)
ENVIRONMENT_PARAMETER.asked = True
ENVIRONMENT_PARAMETER.store = False

# Steps parameter. Default to a local shell script that the user defines.
# We do not ask this parameter, and we do not store it either.
STEPS_PARAMETER = ListParameter("steps", depends=NAME_PARAMETER)
STEPS_PARAMETER.add(DEFAULT_TESTDEF_STEP)
STEPS_PARAMETER.asked = True
STEPS_PARAMETER.store = False

TESTDEF_TEMPLATE = {
    "metadata": {
        "name": NAME_PARAMETER,
        "format": DEFAULT_TESTDEF_FORMAT,
        "version": DEFAULT_TESTDEF_VERSION,
        "description": DESCRIPTION_PARAMETER,
        "environment": ENVIRONMENT_PARAMETER,
    },
    "run": {
        "steps": STEPS_PARAMETER,
    },
}
