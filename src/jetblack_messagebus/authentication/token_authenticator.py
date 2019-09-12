"""Token Authenticator"""

from typing import Optional

from ..io import DataReader, DataWriter

from .types import Authenticator


class TokenAuthenticator(Authenticator):
    """Token Authenticator"""

    def __init__(
            self,
            token: str,
            impersonating: Optional[str] = None,
            forwarded_for: Optional[str] = None
    ) -> None:
        self.token = token
        self.impersonating = impersonating
        self.forwarded_for = forwarded_for

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        writer.write_string(self.token)
        writer.write_string(self.impersonating)
        writer.write_string(self.forwarded_for)
        await writer.drain()
