import argparse
import getpass
import urlparse
import sys
import xmlrpclib

from lava_tool.authtoken import add_token_to_uri, KeyringAuthBackend
from lava_tool.interface import Command


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
        parsed_host = urlparse.urlparse(self.args.HOST)
        if parsed_host.scheme != 'https':
            print >> sys.stderr, "oi!"
            return 1
        if parsed_host.username:
            username = parsed_host.username
        else:
            username = getpass.getuser()
        if self.args.token_file:
            token = self.args.token_file.read()
        else:
            token = getpass.getpass("Paste token for %s: " % self.args.HOST)
        host = parsed_host.hostname
        if parsed_host.port:
            host += ':' + str(parsed_host.port)
        self.auth_backend.add_token(parsed_host.scheme, username, host, token)
        if not self.args.no_check:
            print 'check'


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
        uri = add_token_to_uri(uri, KeyringAuthBackend())
        return xmlrpclib.ServerProxy(uri)

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
