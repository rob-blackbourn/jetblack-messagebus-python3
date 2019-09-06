"""Basic Authenticator"""

from ..io import DataReader, DataWriter

from .types import Authenticator


class BasicAuthenticator(Authenticator):
    """Basic Authenticator"""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        writer.write_string(self.username)
        writer.write_string(self.password)
        await writer.drain()
