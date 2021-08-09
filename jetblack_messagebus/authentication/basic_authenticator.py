"""Basic Authenticator"""

from typing import Optional

from .connection_string_authenticator import ConnectionStringAuthenticator


class BasicAuthenticator(ConnectionStringAuthenticator):
    """A client authenticator which uses usernames and passwords."""

    def __init__(
            self,
            username: str,
            password: str,
            impersonating: Optional[str] = None,
            forwarded_for: Optional[str] = None,
            application: Optional[str] = None
    ) -> None:
        """Initialise the authenticator.

        Args:
            username (str): The username.
            password (str): The password.
            impersonating (Optional[str], optional): For a proxy, the user that is being impersonated. Defaults to None.
            forwarded_for (Optional[str], optional): For a proxy, the host on which the actual client is situated. Defaults to None.
            application (Optional[str], optional): The name of the application. Defaults to None.
        """
        super().__init__(impersonating, forwarded_for, application)
        self.username = username
        self.password = password

    def to_connection_string(self) -> str:
        connection_string = f'Username={self.username};Password={self.password}'
        if self.impersonating:
            connection_string += f';Impersonating={self.impersonating}'
        if self.forwarded_for:
            connection_string += f';ForwardedFor={self.forwarded_for}'
        if self.application:
            connection_string += f';Application={self.application}'
        return connection_string
