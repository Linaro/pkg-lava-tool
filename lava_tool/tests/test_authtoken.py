"""
"""

from unittest import TestCase

from lava_tool.authtoken import AuthenticatingTransportMixin
from lava_tool.interface import LavaCommandError


class TestAuthenticatingTransportMixin(TestCase):

    def test_no_user_no_auth(self):
        a = AuthenticatingTransportMixin()
        _, headers, _ = a.get_host_info('example.com')
        self.assertEqual(None, headers)
