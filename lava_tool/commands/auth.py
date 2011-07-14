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

import getpass
import urlparse
import xmlrpclib

from lava_tool.authtoken import (
    AuthenticatingServerProxy,
    KeyringAuthBackend,
    MemoryAuthBackend,
    )
from lava_tool.interface import Command, LavaCommandError


def normalize_xmlrpc_url(uri):
    if '://' not in uri:
        uri = 'http://' + uri
    if not uri.endswith('/'):
        uri += '/'
    if not uri.endswith('/RPC2/'):
        uri += 'RPC2/'
    return uri


class auth_add(Command):
    """
    Add an authentication token.
    """

    def __init__(self, parser, args, auth_backend=None):
        super(auth_add, self).__init__(parser, args)
        if auth_backend is None:
            auth_backend = KeyringAuthBackend()
        self.auth_backend = auth_backend

    @classmethod
    def register_arguments(cls, parser):
        super(auth_add, cls).register_arguments(parser)
        parser.add_argument(
            "HOST",
            help=("Endpoint to add token for, in the form "
                  "scheme://username@host.  The username will default to "
                  "the currently logged in user."))
        parser.add_argument(
            "--token-file", default=None,
            help="Read the secret from here rather than prompting for it.")
        parser.add_argument(
            "--no-check", action='store_true',
            help=("By default, a call to the remote server is made to check "
                  "that the added token works before remembering it.  "
                  "Passing this option prevents this check."))

    def invoke(self):
        uri = normalize_xmlrpc_url(self.args.HOST)
        parsed_host = urlparse.urlparse(uri)

        if parsed_host.username:
            username = parsed_host.username
        else:
            username = getpass.getuser()

        host = parsed_host.hostname
        if parsed_host.port:
            host += ':' + str(parsed_host.port)

        uri = '%s://%s@%s%s' % (
            parsed_host.scheme, username, host, parsed_host.path)

        if self.args.token_file:
            if parsed_host.password:
                raise LavaCommandError(
                    "Token specified in url but --token-file also passed.")
            else:
                try:
                    token_file = open(self.args.token_file)
                except IOError as ex:
                    raise LavaCommandError(
                        "opening %r failed: %s" % (self.args.token_file, ex))
                token = token_file.read().strip()
        else:
            if parsed_host.password:
                token = parsed_host.password
            else:
                token = getpass.getpass("Paste token for %s: " % uri)

        userless_uri = '%s://%s%s' % (
            parsed_host.scheme, host, parsed_host.path)

        if not self.args.no_check:
            sp = AuthenticatingServerProxy(
                uri, auth_backend=MemoryAuthBackend(
                    [(username, userless_uri, token)]))
            try:
                token_user = sp.system.whoami()
            except xmlrpclib.ProtocolError as ex:
                if ex.errcode == 401:
                    raise LavaCommandError(
                        "Token rejected by server for user %s." % username)
                else:
                    raise
            except xmlrpclib.Fault as ex:
                raise LavaCommandError(
                    "Server reported error during check: %s." % ex)
            if token_user != username:
                raise LavaCommandError(
                    "whoami() returned %s rather than expected %s -- this is "
                    "a bug." % (token_user, username))

        self.auth_backend.add_token(username, userless_uri, token)

        print 'Token added successfully for user %s.' % username
