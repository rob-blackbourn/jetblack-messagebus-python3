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
            forwarded_for: Optional[str] = None,
            application: Optional[str] = None
    ) -> None:
        self.token = token
        self.impersonating = impersonating
        self.forwarded_for = forwarded_for
        self.application = application

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        connection_string = f'Token={self.token}'
        if self.impersonating:
            connection_string += f';Impersonating={self.impersonating}'
        if self.forwarded_for:
            connection_string += f';ForwardedFor={self.forwarded_for}'
        if self.application:
            connection_string += f';Application={self.application}'
        writer.write_string(connection_string)
        await writer.drain()
