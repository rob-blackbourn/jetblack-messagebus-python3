"""Token Authenticator"""

from typing import Optional

from .connection_string_authenticator import ConnectionStringAuthenticator


class TokenAuthenticator(ConnectionStringAuthenticator):
    """Token Authenticator"""

    def __init__(
            self,
            token: str,
            impersonating: Optional[str] = None,
            forwarded_for: Optional[str] = None,
            application: Optional[str] = None
    ) -> None:
        super().__init__(impersonating, forwarded_for, application)
        self.token = token

    def to_connection_string(self) -> str:
        connection_string = f'Token={self.token}'
        if self.impersonating:
            connection_string += f';Impersonating={self.impersonating}'
        if self.forwarded_for:
            connection_string += f';ForwardedFor={self.forwarded_for}'
        if self.application:
            connection_string += f';Application={self.application}'
        return connection_string
