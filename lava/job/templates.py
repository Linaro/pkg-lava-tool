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

TESTDEF_REPOS_TAR_REPO = "tar-repo"

DEVICE_TYPE_PARAMETER = Parameter("device_type")
PREBUILT_IMAGE_PARAMETER = Parameter("image", depends=DEVICE_TYPE_PARAMETER)

# Never store the testdef_urls parameter in the config file.
TESTDEF_URL_PARAMETER = TarRepoParameter(TESTDEF_REPOS_TAR_REPO)
TESTDEF_URL_PARAMETER.store = False

# Use another ID for the server parameter, might be different.
SERVER_PARAMETER = Parameter("stream_server")
STREAM_PARAMETER = Parameter("stream")

BOOT_TEST = {
    "timeout": 18000,
    "job_name": "Boot test",
    "device_type": DEVICE_TYPE_PARAMETER,
    "actions": [
        {
            "command": "deploy_linaro_image",
            "parameters": {
                "image": PREBUILT_IMAGE_PARAMETER
            }
        },
        {
            "command": "boot_linaro_image"
        }
    ]
}

LAVA_TEST_SHELL = {
    "job_name": "LAVA Test Shell",
    "timeout": 18000,
    "device_type": DEVICE_TYPE_PARAMETER,
    "actions": [
        {
            "command": "deploy_linaro_image",
            "parameters": {
                "image": PREBUILT_IMAGE_PARAMETER,
            }
        },
        {
            "command": "lava_test_shell",
            "parameters": {
                "timeout": 1800,
                "testdef_repos": [
                        {
                            "testdef": "lavatest.yaml",
                            "tar-repo": TESTDEF_URL_PARAMETER
                        }
                ]
            }
        },
        {
            "command": "submit_results",
            "parameters" : {
                "stream": STREAM_PARAMETER,
                "server": SERVER_PARAMETER
            }
        }
    ]
}
