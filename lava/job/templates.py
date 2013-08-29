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
    ListParameter,
    Parameter,
)

LAVA_TEST_SHELL_TAR_REPO_KEY = "tar-repo"
LAVA_TEST_SHELL_TESDEF_KEY = "testdef"

DEVICE_TYPE_PARAMETER = Parameter("device_type")
PREBUILT_IMAGE_PARAMETER = Parameter("image", depends=DEVICE_TYPE_PARAMETER)

TESTDEF_URLS_PARAMETER = ListParameter("testdef_urls")
TESTDEF_URLS_PARAMETER.store = False

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
                "testdef_urls": TESTDEF_URLS_PARAMETER,
            }
        }
    ]
}

# This is a special case template, only use when automatically create job files
# starting from a testdef or a script. Never to be used directly by the user.
LAVA_TEST_SHELL_TAR_REPO = {
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
                        LAVA_TEST_SHELL_TESDEF_KEY: None,
                        LAVA_TEST_SHELL_TAR_REPO_KEY: None,
                    }
                ]
            }
        }
    ]
}

BOOT_TEST_KEY = "boot-test"
LAVA_TEST_SHELL_KEY = "lava-test-shell"

# Dict with all the user available job templates.
JOB_TYPES = {
    BOOT_TEST_KEY: BOOT_TEST,
    LAVA_TEST_SHELL_KEY: LAVA_TEST_SHELL,
}
