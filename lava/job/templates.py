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
    UrlListParameter,
)

DEVICE_TYPE_ID = "device_type"
IMAGE_ID = "image"
TESTDEF_URLS_ID = "testdef_urls"

DEVICE_TYPE_PARAMETER = Parameter(DEVICE_TYPE_ID)
PREBUILT_IMAGE_PARAMETER = Parameter(IMAGE_ID, depends=DEVICE_TYPE_PARAMETER)
# Never store the testdef_urls parameter in the config file.
TESTDEF_URL_PARAMETER = UrlListParameter(TESTDEF_URLS_ID,
                                         depends=DEVICE_TYPE_PARAMETER)
TESTDEF_URL_PARAMETER.store = False

BOOT_TEST = {
    "job_name": "Boot test",
    DEVICE_TYPE_ID: DEVICE_TYPE_PARAMETER,
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
    DEVICE_TYPE_ID: DEVICE_TYPE_PARAMETER,
    "actions": [
        {
            "command": "deploy_linaro_image",
            "parameters": {
                IMAGE_ID: PREBUILT_IMAGE_PARAMETER,
            }
        },
        {
            "command": "lava_test_shell",
            "parameters": {
                TESTDEF_URLS_ID: TESTDEF_URL_PARAMETER,
            }
        }
    ]
}
