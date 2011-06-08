"""
"""

import StringIO
import sys

from lava_tool.mocker import CONTAINS, MockerTestCase
from lava_tool.authtoken import MemoryAuthBackend
from lava_tool.commands.auth import auth_add


class FakeArgs:
    token_file = None
    no_check = False

class AuthAddTests(MockerTestCase):

    def setUp(self):
        MockerTestCase.setUp(self)
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO.StringIO()
        self.saved_stderr = sys.stderr
        sys.stderr = StringIO.StringIO()

    def tearDown(self):
        MockerTestCase.tearDown(self)
        sys.stdout = self.saved_stdout
        sys.stderr = self.saved_stderr

    def make_command(self, auth_backend, **kwargs):
        args = FakeArgs()
        args.__dict__.update(kwargs)
        return auth_add(None, args, auth_backend)

    def test_token_taken_from_argument(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN', auth_backend.get_token_for_host('user', 'example.com'))

    def test_token_taken_from_getpass(self):
        mocked_getpass = self.mocker.replace('getpass.getpass', passthrough=False)
        mocked_getpass(CONTAINS('Paste token'))
        self.mocker.result("TOKEN")
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user@example.com', no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN', auth_backend.get_token_for_host('user', 'example.com'))
