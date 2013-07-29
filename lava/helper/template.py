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

"""Helper functions for a template."""

from lava.parameter import Parameter


def expand_template(template, config):
    """Updates a template based on the values from the provided config.

    :param template: A template to be updated.
    :param config: A Config instance where values should be taken.
    """

    def update(data):
        """Internal recursive function."""
        if isinstance(data, dict):
            keys = data.keys()
        elif isinstance(data, list):
            keys = range(len(data))
        else:
            return
        for key in keys:
            entry = data[key]
            if isinstance(entry, Parameter):
                data[key] = config.get(entry)
            else:
                update(entry)

    update(template)


def get_key(data, search_key):
    """Goes through a template looking for a key.

    :param data: The template to traverse.
    :param search_key: The key to look for.
    :return The key value.
    """
    return_value = None
    found = False

    if isinstance(data, dict):
        bucket = []

        for key, value in data.iteritems():
            if key == search_key:
                return_value = value
                found = True
                break
            else:
                bucket.append(value)

        if bucket and not found:
            for element in bucket:
                if isinstance(element, list):
                    for element in element:
                        bucket.append(element)
                elif isinstance(element, dict):
                    for key, value in element.iteritems():
                        if key == search_key:
                            return_value = value
                            found = True
                            break
                        else:
                            bucket.append(value)
                if found:
                    break

    return return_value


def set_value(data, search_key, new_value):
    """Sets a new value for a template key.

    :param data: The data structure to update.
    :type dict
    :param search_key: The key to search and update.
    :param new_value: The new value to set.
    """
    is_set = False

    if isinstance(data, dict):
        bucket = []

        for key, value in data.iteritems():
            if key == search_key:
                data[key] = new_value
                is_set = True
                break
            else:
                bucket.append(value)

        if bucket and not is_set:
            for element in bucket:
                if isinstance(element, list):
                    for element in element:
                        bucket.append(element)
                elif isinstance(element, dict):
                    for key, value in element.iteritems():
                        if key == search_key:
                            element[key] = new_value
                            is_set = True
                            break
                        else:
                            bucket.append(value)
                if is_set:
                    break
