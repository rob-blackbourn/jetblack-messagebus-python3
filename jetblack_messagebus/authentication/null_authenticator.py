"""Null Authenticator"""

from ..io import DataReader, DataWriter

from .types import Authenticator


class NullAuthenticator(Authenticator):
    """Null Authenticator"""

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        return
