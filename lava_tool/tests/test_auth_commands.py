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
Unit tests for the lava_tool.commands.auth package
"""

import StringIO
import sys
import tempfile
import xmlrpclib

from mocker import ARGS, KWARGS, CONTAINS, MockerTestCase

from lava_tool.authtoken import MemoryAuthBackend
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
            auth_backend, HOST='http://user:TOKEN@example.com/RPC2/',
            no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))

    def test_RPC2_implied(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))

    def test_scheme_recorded(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='https://user:TOKEN@example.com/RPC2/',
            no_check=True)
        cmd.invoke()
        self.assertEqual(
            None,
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'https://example.com/RPC2/'))

    def test_path_on_server_recorded(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='https://user:TOKEN@example.com/path',
            no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'https://example.com/path/RPC2/'))

    def test_token_taken_from_getpass(self):
        mocked_getpass = self.mocker.replace(
            'getpass.getpass', passthrough=False)
        mocked_getpass(CONTAINS('Paste token'))
        self.mocker.result("TOKEN")
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user@example.com', no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))

    def test_token_taken_from_file(self):
        auth_backend = MemoryAuthBackend([])
        token_file = tempfile.NamedTemporaryFile('w')
        token_file.write("TOKEN")
        token_file.flush()
        cmd = self.make_command(
            auth_backend, HOST='http://user@example.com', no_check=True,
            token_file=token_file.name)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))

    def test_token_file_and_in_url_conflict(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=True,
            token_file='some-file-name')
        self.assertRaises(LavaCommandError, cmd.invoke)

    def test_non_existent_token_reported(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=True,
            token_file='does-not-exist')
        self.assertRaises(LavaCommandError, cmd.invoke)

    def test_user_taken_from_getuser(self):
        mocked_getuser = self.mocker.replace(
            'getpass.getuser', passthrough=False)
        mocked_getuser()
        self.mocker.result("user")
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        token_file = tempfile.NamedTemporaryFile('w')
        token_file.write("TOKEN")
        token_file.flush()
        cmd = self.make_command(
            auth_backend, HOST='http://example.com', no_check=True,
            token_file=token_file.name)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))

    def test_port_included(self):
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend,
            HOST='http://user:TOKEN@example.com:1234',
            no_check=True)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com:1234/RPC2/'))

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
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=False)
        cmd.invoke()
        self.assertEqual(
            'TOKEN',
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))

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
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=False)
        self.assertRaises(LavaCommandError, cmd.invoke)

    def test_check_fails_token_not_recorded(self):
        mocked_AuthenticatingServerProxy = self.mocker.replace(
            'lava_tool.authtoken.AuthenticatingServerProxy', passthrough=False)
        mocked_sp = mocked_AuthenticatingServerProxy(ARGS, KWARGS)
        self.mocker.nospec()
        mocked_sp.system.whoami()
        self.mocker.throw(xmlrpclib.ProtocolError('', 401, '', []))
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=False)
        self.assertRaises(LavaCommandError, cmd.invoke)
        self.assertEqual(
            None,
            auth_backend.get_token_for_endpoint(
                'user', 'http://example.com/RPC2/'))

    def test_check_other_http_failure_just_raised(self):
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
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=False)
        self.assertRaises(xmlrpclib.ProtocolError, cmd.invoke)

    def test_fault_reported(self):
        mocked_AuthenticatingServerProxy = self.mocker.replace(
            'lava_tool.authtoken.AuthenticatingServerProxy', passthrough=False)
        mocked_sp = mocked_AuthenticatingServerProxy(ARGS, KWARGS)
        # nospec() is required because of
        # https://bugs.launchpad.net/mocker/+bug/794351
        self.mocker.nospec()
        mocked_sp.system.whoami()
        self.mocker.throw(xmlrpclib.Fault(100, 'faultString'))
        self.mocker.replay()
        auth_backend = MemoryAuthBackend([])
        cmd = self.make_command(
            auth_backend, HOST='http://user:TOKEN@example.com', no_check=False)
        self.assertRaises(LavaCommandError, cmd.invoke)
