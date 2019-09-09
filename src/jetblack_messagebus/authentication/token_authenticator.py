"""Token Authenticator"""

from ..io import DataReader, DataWriter

from .types import Authenticator


class TokenAuthenticator(Authenticator):
    """Token Authenticator"""

    def __init__(self, token: str) -> None:
        self.token = token

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        writer.write_string(self.token)
        await writer.drain()
