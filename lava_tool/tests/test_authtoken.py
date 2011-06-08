"""
"""

import base64
from unittest import TestCase

from lava_tool.authtoken import (
    AuthenticatingTransportMixin,
    MemoryAuthBackend,
    )
from lava_tool.interface import LavaCommandError


class TestAuthenticatingTransportMixin(TestCase):

    def headers_for_host(self, host, auth_backend):
        a = AuthenticatingTransportMixin()
        a.auth_backend = auth_backend
        _, headers, _ = a.get_host_info(host)
        return headers

    def user_and_password_from_headers(self, headers):
        if len(headers) != 1:
            self.fail("expected exactly 1 header, got %r" % headers)
        [(name, value)] = headers
        if name != 'Authorization':
            self.fail("non-authorization header found in %r" % headers)
        if not value.startswith("Basic "):
            self.fail("non-basic auth header found in %r" % headers)
        auth = base64.b64decode(value[len("Basic "):])
        if ':' in auth:
            return tuple(auth.split(':', 1))
        else:
            return (auth, None)

    def test_no_user_no_auth(self):
        headers = self.headers_for_host('example.com', MemoryAuthBackend([]))
        self.assertEqual(None, headers)

    def test_error_when_user_but_no_token(self):
        self.assertRaises(
            LavaCommandError,
            self.headers_for_host, 'user@example.com', MemoryAuthBackend([]))

    def test_token_used_for_auth(self):
        headers = self.headers_for_host(
            'user@example.com',
            MemoryAuthBackend([('user', 'example.com', "TOKEN")]))
        self.assertEqual(
            ('user', 'TOKEN'), self.user_and_password_from_headers(headers))
