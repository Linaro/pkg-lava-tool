# Copyright (C) 2013 Linaro Limited
#
# Author: Antonio Terceiro <antonio.terceiro@linaro.org>
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

from lava.parameter import (
    Parameter,
    TarRepoParameter,
)

ACTIONS_ID = "actions"
COMMAND_ID = "command"
IMAGE_ID = "image"
PARAMETERS_ID = "parameters"
TARGET_ID = "target"
TESTDEF_REPOS_ID = "testdef_repos"
TESTDEF_REPOS_TAR_REPO = "tar-repo"

DEVICE_TYPE_PARAMETER = Parameter(TARGET_ID)
PREBUILT_IMAGE_PARAMETER = Parameter(IMAGE_ID, depends=DEVICE_TYPE_PARAMETER)

# Never store the testdef_urls parameter in the config file.
TESTDEF_URL_PARAMETER = TarRepoParameter(TESTDEF_REPOS_TAR_REPO)
TESTDEF_URL_PARAMETER.store = False

BOOT_TEST = {
    "timeout": 18000,
    "job_name": "Boot test",
    TARGET_ID: DEVICE_TYPE_PARAMETER,
    ACTIONS_ID: [
        {
            COMMAND_ID: "deploy_linaro_image",
            PARAMETERS_ID: {
                "image": PREBUILT_IMAGE_PARAMETER
            }
        },
        {
            COMMAND_ID: "boot_linaro_image"
        }
    ]
}

LAVA_TEST_SHELL = {
    "job_name": "LAVA Test Shell",
    "timeout": 18000,
    TARGET_ID: DEVICE_TYPE_PARAMETER,
    ACTIONS_ID: [
        {
            COMMAND_ID: "deploy_linaro_image",
            PARAMETERS_ID: {
                IMAGE_ID: PREBUILT_IMAGE_PARAMETER,
            }
        },
        {
            COMMAND_ID: "lava_test_shell",
            PARAMETERS_ID: {
                "timeout": 18000,
                TESTDEF_REPOS_ID: [
                        {
                            "testdef": "lavatest.yaml",
                            TESTDEF_REPOS_TAR_REPO: TESTDEF_URL_PARAMETER
                        }
                ]
            }
        }
    ]
}
