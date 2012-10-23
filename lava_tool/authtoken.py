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
import urllib2
import os
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

    def get_token_for_endpoint(self, username, endpoint_url):
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


class XMLRPCTransport(xmlrpclib.Transport):

    def __init__(self, scheme, auth_backend):
        xmlrpclib.Transport.__init__(self)
        self._scheme = scheme
        self.auth_backend = auth_backend
        self._opener = urllib2.build_opener()
        self.verbose = 0

    def request(self, host, handler, request_body, verbose=0):
        self.verbose = verbose
        token = None
        user = None
        auth, host = urllib.splituser(host)
        if auth:
            user, token = urllib.splitpasswd(auth)
        url = self._scheme + "://" + host + handler
        if user is not None and token is None:
            token = self.auth_backend.get_token_for_endpoint(user, url)
            if token is None:
                raise LavaCommandError(
                    "Username provided but no token found.")
        request = urllib2.Request(url, request_body)
        request.add_header("Content-Type", "text/xml")
        if token:
            auth = base64.b64encode(urllib.unquote(user + ':' + token))
            request.add_header("Authorization", "Basic " + auth)
        try:
            response = self._opener.open(request)
        except urllib2.HTTPError as e:
            raise xmlrpclib.ProtocolError(
                host + handler, e.code, e.msg, e.info())
        return self.parse_response(response)


class AuthenticatingServerProxy(xmlrpclib.ServerProxy):

    def __init__(self, uri, transport=None, encoding=None, verbose=0,
                 allow_none=0, use_datetime=0, auth_backend=None):
        if transport is None:
            scheme = urllib.splittype(uri)[0]
            transport = XMLRPCTransport(scheme, auth_backend=auth_backend)
        xmlrpclib.ServerProxy.__init__(
            self, uri, transport, encoding, verbose, allow_none, use_datetime)
