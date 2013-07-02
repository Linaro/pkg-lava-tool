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


DEFAULT_TESTDEF_VERSION = "1.0"
DEFAULT_TESTDEF_FORMAT = "Lava-Test Test Definition 1.0"
DEFAULT_TESTDEF_ENVIRONMENT = "lava-test-shell"

NAME_PARAMETER = Parameter("name")
DESCRIPTION_PARAMETER = Parameter("description", depends=NAME_PARAMETER)
ENVIRONMENT_PARAMETER = Parameter("environment",
                                  depends=NAME_PARAMETER,
                                  value=DEFAULT_TESTDEF_ENVIRONMENT)
STEPS_PARAMETER = ListParameter("steps", depends=NAME_PARAMETER)

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
