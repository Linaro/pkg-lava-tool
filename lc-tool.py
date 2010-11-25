#!/usr/bin/python
# lc-tool - command line interface for validation dashboard
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


if __name__ == '__main__':
    try:
        import launch_control_tool.commands
        from launch_control_tool.dispatcher import main
    except ImportError:
        print "Unable to import launch_control.commands.dispatcher"
        print "Your installation is probably faulty"
        raise
    else:
        main()
