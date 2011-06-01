import urllib
import xmlrpclib

from lava_tool.interface import LavaCommandError


def add_token_to_uri(uri, auth_backend):
    orig_uri = uri
    type, uri = urllib.splittype(uri)
    host, handler = urllib.splithost(uri)
    user, host = urllib.splituser(host)
    if not user:
        return orig_uri
    token = auth_backend.get_token_for_host(user, host)
    if token is None:
        raise LavaCommandError("username provided but no token found")
    return "%s://%s:%s@%s%s" % (type, user, token, host, handler)


class AuthenticatingServerProxy(xmlrpclib.ServerProxy):

    def __init__(self, uri, transport=None, encoding=None, verbose=0,
                 allow_none=0, use_datetime=0, auth_backend=None):
        xmlrpclib.ServerProxy.__init__(
            self, add_token_to_uri(uri, auth_backend), transport, encoding,
            verbose, allow_none, use_datetime)
