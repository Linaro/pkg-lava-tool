import argparse
import getpass
import urlparse
import sys
import xmlrpclib

from lava_tool.authtoken import (
    AuthenticatingServerProxy,
    KeyringAuthBackend,
    MemoryAuthBackend,
    )
from lava_tool.interface import Command, LavaCommandError


class auth_add(Command):
    """
    """

    def __init__(self, parser, args, auth_backend=None):
        super(auth_add, self).__init__(parser, args)
        if auth_backend is None:
            self.auth_backend = KeyringAuthBackend()

    @classmethod
    def register_arguments(cls, parser):
        super(auth_add, cls).register_arguments(parser)
        parser.add_argument(
            "HOST",
            help=("Endpoint to add token for, in the form "
                  "scheme://username@host.  The username will default to "
                  "the currently logged in user."))
        parser.add_argument(
            "--token-file", default=None, type=argparse.FileType("rb"),
            help="Read the secret from here rather than prompting for it.")
        parser.add_argument(
            "--no-check", action='store_true',
            help="XXX.")

    def invoke(self):
        uri = self.args.HOST
        if '://' not in uri:
            uri = 'http://' + uri
        parsed_host = urlparse.urlparse(uri)
        if parsed_host.username:
            username = parsed_host.username
        else:
            username = getpass.getuser()
        if self.args.token_file:
            if parsed_host.password:
                raise LavaCommandError(
                    "token specified in url but --token-file also passed")
            else:
                token = self.args.token_file.read()
        else:
            if parsed_host.password:
                token = parsed_host.password
            else:
                token = getpass.getpass("Paste token for %s: " % uri)
        host = parsed_host.hostname
        if parsed_host.port:
            host += ':' + str(parsed_host.port)
        if not self.args.no_check:
            if not uri.endswith('/'):
                uri += '/'
            uri += 'RPC2/'
            sp = AuthenticatingServerProxy(
                uri, auth_backend=MemoryAuthBackend(
                    [(username, host, token)]))
            try:
                token_user = sp.system.whoami()
            except xmlrpclib.ProtocolError as ex:
                if ex.errcode == 401:
                    raise LavaCommandError("token rejected by server")
                else:
                    raise
            if token_user is None or token_user != username:
                raise LavaCommandError("???")
        self.auth_backend.add_token(username, host, token)
        print 'token added successfully'


class auth_list(Command):
    """
    """
    def invoke(self):
        pass


class auth_remove(Command):
    """
    """
    def invoke(self):
        pass


class test_api(Command):

    def get_authenticated_server_proxy(self, uri):
        return AuthenticatingServerProxy(
            uri, auth_backend=KeyringAuthBackend())

    @classmethod
    def register_arguments(cls, parser):
        super(test_api, cls).register_arguments(parser)
        parser.add_argument(
            "HOST",
            help=("Endpoint to add token for, in the form "
                  "scheme://username@host.  The username will default to "
                  "the currently logged in user."))

    def invoke(self):
        print self.get_authenticated_server_proxy(self.args.HOST).scheduler.test()
