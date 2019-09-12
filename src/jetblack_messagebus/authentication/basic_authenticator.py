"""Basic Authenticator"""

from typing import Optional

from ..io import DataReader, DataWriter

from .types import Authenticator


class BasicAuthenticator(Authenticator):
    """Basic Authenticator"""

    def __init__(
            self,
            username: str,
            password: str,
            impersonating: Optional[str] = None,
            forwarded_for: Optional[str] = None
    ) -> None:
        self.username = username
        self.password = password
        self.impersonating = impersonating
        self.forwarded_for = forwarded_for

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        writer.write_string(self.username)
        writer.write_string(self.password)
        writer.write_string(self.impersonating)
        writer.write_string(self.forwarded_for)
        await writer.drain()
