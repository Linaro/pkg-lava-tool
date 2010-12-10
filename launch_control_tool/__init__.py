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

"""
Launch Control Tool package
"""


__version__ = (0, 2, 0, "final", 0)


def get_version():
    """
    Return a string representing the version of this package
    """
    # XXX: I should get this code in a common library someday
    major, minor, micro, releaselevel, serial = __version__
    assert releaselevel in ('dev', 'alpha', 'beta', 'candidate', 'final')
    base_version = "%s.%s" % (major, minor)
    if micro != 0:
        base_version += ".%s" % micro
    if releaselevel != 'final':
        base_version += "-%s" % releaselevel
    return base_version


