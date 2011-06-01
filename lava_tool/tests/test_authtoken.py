"""
"""

from unittest import TestCase

from lava_tool.authtoken import add_token_to_uri

class StubAuthBackend(object):

    def __init__(self, user_host_token_list):
        self._tokens = {}
        for user, host, token in user_host_token_list:
            self._tokens[(user, host)] = token

    def get_token_for_host(self, username, host):
        return self._tokens.get((username, host))

class TestAddTokenToUri(TestCase):

    def test_no_username_no_token(self):
        auth_backend = StubAuthBackend([])
        uri = 'https://example.com/'
        self.assertEquals(uri, add_token_to_uri(uri, auth_backend))

