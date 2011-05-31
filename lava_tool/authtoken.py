import urllib
import xmlrpclib


class AuthenticatingServerProxy(xmlrpclib.ServerProxy):

    def __init__(self, uri, transport=None, encoding=None, verbose=0,
                 allow_none=0, use_datetime=0, auth_backend=None):
        type, uri = urllib.splittype(uri)
        host, handler = urllib.splithost(uri)
        user, host = urllib.splituser(host)
        token = auth_backend.get_token_for_host()
        if token:
            host = 
        xmlrpclib.ServerProxy.__init__(
            self, transport, encoding, verbose, allow_none, use_datetime)
        self.auth_backend = auth_backend
