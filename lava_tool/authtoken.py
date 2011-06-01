import urllib
import xmlrpclib


def add_token_to_uri(uri, auth_backend):
    orig_uri = uri
    type, uri = urllib.splittype(uri)
    host, handler = urllib.splithost(uri)
    user, host = urllib.splituser(host)
    if user:
        token = auth_backend.get_token_for_host(user, host)
    else:
        token = None
    if token is None:
        return orig_uri
    return orig_uri


class AuthenticatingServerProxy(xmlrpclib.ServerProxy):

    def __init__(self, uri, transport=None, encoding=None, verbose=0,
                 allow_none=0, use_datetime=0, auth_backend=None):
        xmlrpclib.ServerProxy.__init__(
            self, add_token_to_uri(uri, auth_backend), transport, encoding,
            verbose, allow_none, use_datetime)
