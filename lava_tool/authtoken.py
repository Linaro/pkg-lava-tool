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

import base64
import urllib
import xmlrpclib

import keyring.core

from lava_tool.interface import LavaCommandError


class AuthBackend(object):

    def add_token(self, username, endpoint_url, token):
        raise NotImplementedError

    def get_token_for_endpoint(self, user, endpoint_url):
        raise NotImplementedError


class KeyringAuthBackend(AuthBackend):

    def add_token(self, username, endpoint_url, token):
        keyring.core.set_password(
            "lava-tool-%s" % endpoint_url, username, token)

    def get_token_for_host(self, username, endpoint_url):
        return keyring.core.get_password(
            "lava-tool-%s" % endpoint_url, username)


class MemoryAuthBackend(AuthBackend):

    def __init__(self, user_endpoint_token_list):
        self._tokens = {}
        for user, endpoint, token in user_endpoint_token_list:
            self._tokens[(user, endpoint)] = token

    def add_token(self, username, endpoint_url, token):
        self._tokens[(username, endpoint_url)] = token

    def get_token_for_endpoint(self, username, endpoint_url):
        return self._tokens.get((username, endpoint_url))


class AuthenticatingTransportMixin:

    def send_request(self, connection, handler, request_body):
        xmlrpclib.Transport.send_request(
            self, connection, handler, request_body)
        if self._extra_headers:
            extra_headers = self._extra_headers
            if isinstance(extra_headers, dict):
                extra_headers = extra_headers.items()
            if [1 for eh in extra_headers if eh[0].lower() == "authorization"]:
                return
        ## host = connection.host
        ## port = ''
        ## if connection.port != connection.default_port:
        ##     port = ':' + int(connection.port)
        auth, host = urllib.splituser(self._connection[0])
        if auth is None:
            return
        user, token = urllib.splitpasswd(auth)
        if token is None:
            endpoint_url = '%s://%s%s' % (self._scheme, host, handler)
            token = self.auth_backend.get_token_for_endpoint(
                user, endpoint_url)
            if token is None:
                raise LavaCommandError(
                    "Username provided but no token found.")
        auth = base64.b64encode(urllib.unquote(user + ':' + token))
        connection.putheader("Authorization", "Basic " + auth)

    def get_host_info(self, host):

        x509 = {}
        if isinstance(host, tuple):
            host, x509 = host

        return host, None, x509


class AuthenticatingTransport(
        AuthenticatingTransportMixin, xmlrpclib.Transport):
    _scheme = 'http'
    def __init__(self, use_datetime=0, auth_backend=None):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self.auth_backend = auth_backend


class AuthenticatingSafeTransport(
        AuthenticatingTransportMixin, xmlrpclib.SafeTransport):
    _scheme = 'https'
    def __init__(self, use_datetime=0, auth_backend=None):
        xmlrpclib.SafeTransport.__init__(self, use_datetime)
        self.auth_backend = auth_backend


class AuthenticatingServerProxy(xmlrpclib.ServerProxy):

    def __init__(self, uri, transport=None, encoding=None, verbose=0,
                 allow_none=0, use_datetime=0, auth_backend=None):
        if transport is None:
            if urllib.splittype(uri)[0] == "https":
                transport = AuthenticatingSafeTransport(
                    use_datetime=use_datetime, auth_backend=auth_backend)
            else:
                transport = AuthenticatingTransport(
                    use_datetime=use_datetime, auth_backend=auth_backend)
        xmlrpclib.ServerProxy.__init__(
            self, uri, transport, encoding, verbose, allow_none, use_datetime)
