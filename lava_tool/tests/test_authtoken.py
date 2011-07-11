# Copyright (C) 2011 Linaro Limited
#
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
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

"""
Unit tests for the lava_tool.authtoken package
"""

import base64
import StringIO
from unittest import TestCase
import urlparse
import sys
import xmlrpclib

from mocker import ARGS, KWARGS, Mocker

from lava_tool.authtoken import (
    AuthenticatingServerProxy,
    MemoryAuthBackend,
    )
from lava_tool.interface import LavaCommandError

if sys.version_info[:2] <= (2, 6):
    TWO_SIX = True
else:
    TWO_SIX = False

class TestAuthenticatingServerProxy(TestCase):

    def auth_headers_for_method_call_on(self, url, auth_backend):
        parsed = urlparse.urlparse(url)
        expected_host = parsed.hostname
        if parsed.port:
            expected_host += ':' + str(parsed.port)
        server_proxy = AuthenticatingServerProxy(
            url, auth_backend=auth_backend)
        mocker = Mocker()
        if url.startswith('https'):
            cls_name = 'httplib.HTTPS'
            expected_constructor_args = (expected_host, ARGS)
        else:
            cls_name = 'httplib.HTTP'
            expected_constructor_args = (expected_host, ARGS)
        if not TWO_SIX:
            cls_name += 'Connection'
        mocked_HTTPConnection = mocker.replace(cls_name, passthrough=False)
        mocked_connection = mocked_HTTPConnection(*expected_constructor_args)
        # nospec() is required because of
        # https://bugs.launchpad.net/mocker/+bug/794351
        mocker.nospec()
        auth_data = []
        mocked_connection.putrequest(ARGS, KWARGS)
        if TWO_SIX:
            mocked_connection.send(ARGS, KWARGS)

        def match_header(header, *values):
            if header.lower() == 'authorization':
                if len(values) != 1:
                    self.fail(
                        'more than one value for '
                        'putheader("Authorization", ...)')
                auth_data.append(values[0])
        mocked_connection.putheader(ARGS)
        mocker.call(match_header)
        mocker.count(1, None)

        mocked_connection.endheaders(ARGS, KWARGS)

        if TWO_SIX:
            mocked_connection.getreply(ARGS, KWARGS)
            mocker.result((200, None, None))
            s = StringIO.StringIO(xmlrpclib.dumps((1,), methodresponse=True))
            mocked_connection.getfile()
            mocker.result(s)
            mocked_connection._conn
            mocker.result(None)
        else:
            mocked_connection.getresponse(ARGS, KWARGS)
            s = StringIO.StringIO(xmlrpclib.dumps((1,), methodresponse=True))
            s.status = 200
            mocker.result(s)

        mocked_connection.close()
        mocker.count(0, 1)

        with mocker:
            server_proxy.method()

        return auth_data

    def user_and_password_from_auth_data(self, auth_data):
        if len(auth_data) != 1:
            self.fail("expected exactly 1 header, got %r" % len(auth_data))
        [value] = auth_data
        if not value.startswith("Basic "):
            self.fail("non-basic auth header found in %r" % auth_data)
        auth = base64.b64decode(value[len("Basic "):])
        if ':' in auth:
            return tuple(auth.split(':', 1))
        else:
            return (auth, None)

    def test_no_user_no_auth(self):
        auth_headers = self.auth_headers_for_method_call_on(
            'http://localhost/RPC2/', MemoryAuthBackend([]))
        self.assertEqual([], auth_headers)

    def test_token_used_for_auth_http(self):
        auth_headers = self.auth_headers_for_method_call_on(
            'http://user@localhost/RPC2/',
            MemoryAuthBackend([('user', 'http://localhost/RPC2/', 'TOKEN')]))
        self.assertEqual(
            ('user', 'TOKEN'),
            self.user_and_password_from_auth_data(auth_headers))

    def test_token_used_for_auth_https(self):
        auth_headers = self.auth_headers_for_method_call_on(
            'https://user@localhost/RPC2/',
            MemoryAuthBackend([('user', 'https://localhost/RPC2/', 'TOKEN')]))
        self.assertEqual(
            ('user', 'TOKEN'),
            self.user_and_password_from_auth_data(auth_headers))

    def test_port_included(self):
        auth_headers = self.auth_headers_for_method_call_on(
            'http://user@localhost:1234/RPC2/',
            MemoryAuthBackend(
                [('user', 'http://localhost:1234/RPC2/', 'TOKEN')]))
        self.assertEqual(
            ('user', 'TOKEN'),
            self.user_and_password_from_auth_data(auth_headers))

    def test_error_when_user_but_no_token(self):
        self.assertRaises(
            LavaCommandError,
            self.auth_headers_for_method_call_on,
            'http://user@localhost/RPC2/',
            MemoryAuthBackend([]))
