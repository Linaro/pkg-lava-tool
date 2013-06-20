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

from lava.parameter import Parameter

device_type = Parameter("device_type")
prebuilt_image = Parameter("prebuilt_image", depends=device_type)

BOOT_TEST = {
    "job_name": "Boot test",
    "device_type": device_type,
    "actions": [
        {
            "command": "deploy_linaro_image",
            "parameters": {
                "image": prebuilt_image
            }
        },
        {
            "command": "boot_linaro_image"
        }
    ]
}

LAVA_TEST_SHELL = {
    "job_name": "LAVA Test Shell",
    "device_type": device_type,
    "actions": [
        {
            "command": "deploy_linaro_image",
            "parameters": {
                "image": prebuilt_image,
            }
        },
        {
            "command": "lava_test_shell",
            "parameters": {
                "testdef_urls": [
                    Parameter("testdef_url")
                ]
            }
        }
    ]
}
