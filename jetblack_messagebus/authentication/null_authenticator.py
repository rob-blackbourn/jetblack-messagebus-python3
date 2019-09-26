"""Null Authenticator"""

from .types import Authenticator


class NullAuthenticator(Authenticator):
    """Null Authenticator"""

    async def authenticate(self, reader, writer):
        pass
