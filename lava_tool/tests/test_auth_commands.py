"""
"""

import StringIO
import sys
import xmlrpclib

from lava_tool.authtoken import MemoryAuthBackend
from lava_tool.mocker import ARGS, KWARGS, CONTAINS, MockerTestCase
from lava_tool.interface import LavaCommandError
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

    def test_token_taken_from_file(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user@example.com', no_check=True,
            token_file=StringIO.StringIO('TOKEN'))
        cmd.invoke()
        self.assertEqual(
            'TOKEN', auth_backend.get_token_for_host('user', 'example.com'))

    def test_token_file_and_in_url_conflict(self):
        mocked_getuser = self.mocker.replace('getpass.getuser', passthrough=False)
        mocked_getuser()
        self.mocker.result("user")
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://example.com', no_check=True,
            token_file=StringIO.StringIO('TOKEN'))
        cmd.invoke()
        self.assertEqual(
            'TOKEN', auth_backend.get_token_for_host('user', 'example.com'))

    def test_user_taken_from_getpass(self):
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

    def test_port_included(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com:1234', no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN', auth_backend.get_token_for_host('user', 'example.com:1234'))

    def test_check_made(self):
        mocked_AuthenticatingServerProxy = self.mocker.replace(
            'lava_tool.authtoken.AuthenticatingServerProxy', passthrough=False)
        mocked_sp = mocked_AuthenticatingServerProxy(ARGS, KWARGS)
        # nospec() is required because of
        # https://bugs.launchpad.net/mocker/+bug/794351
        self.mocker.nospec()
        mocked_sp.system.whoami()
        self.mocker.result('user')
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com:1234', no_check=False)
        cmd.invoke()
        self.assertEqual(
            'TOKEN', auth_backend.get_token_for_host('user', 'example.com:1234'))

    def test_check_auth_failure_reported_nicely(self):
        mocked_AuthenticatingServerProxy = self.mocker.replace(
            'lava_tool.authtoken.AuthenticatingServerProxy', passthrough=False)
        mocked_sp = mocked_AuthenticatingServerProxy(ARGS, KWARGS)
        # nospec() is required because of
        # https://bugs.launchpad.net/mocker/+bug/794351
        self.mocker.nospec()
        mocked_sp.system.whoami()
        self.mocker.throw(xmlrpclib.ProtocolError('', 401, '', []))
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com:1234', no_check=False)
        self.assertRaises(LavaCommandError, cmd.invoke)

    def test_check_other_failure_just_raised(self):
        mocked_AuthenticatingServerProxy = self.mocker.replace(
            'lava_tool.authtoken.AuthenticatingServerProxy', passthrough=False)
        mocked_sp = mocked_AuthenticatingServerProxy(ARGS, KWARGS)
        # nospec() is required because of
        # https://bugs.launchpad.net/mocker/+bug/794351
        self.mocker.nospec()
        mocked_sp.system.whoami()
        self.mocker.throw(xmlrpclib.ProtocolError('', 500, '', []))
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com:1234', no_check=False)
        self.assertRaises(xmlrpclib.ProtocolError, cmd.invoke)
