"""Basic Authenticator"""

import os
from typing import Optional

from .connection_string_authenticator import ConnectionStringAuthenticator


class SspiAuthenticator(ConnectionStringAuthenticator):
    """A client authenticator for SSPI."""

    def __init__(
            self,
            username: Optional[str] = None,
            impersonating: Optional[str] = None,
            forwarded_for: Optional[str] = None,
            application: Optional[str] = None
    ) -> None:
        """Initialise the authenticator.

        Args:
            username (Optional[str], optional): The username. Defaults to None.
            impersonating (Optional[str], optional): For a proxy, the user that is being impersonated. Defaults to None.
            forwarded_for (Optional[str], optional): For a proxy, the host on which the actual client is situated. Defaults to None.
            application (Optional[str], optional): The name of the application. Defaults to None.
        """
        super().__init__(impersonating, forwarded_for, application)

        if username:
            self.username = username
        else:
            domain = os.environ['USERDOMAIN']
            username = os.environ['USERNAME']
            self.username = f"{domain}\\{username}"



    def to_connection_string(self) -> str:
        connection_string = f'Username={self.username}'
        if self.impersonating:
            connection_string += f';Impersonating={self.impersonating}'
        if self.forwarded_for:
            connection_string += f';ForwardedFor={self.forwarded_for}'
        if self.application:
            connection_string += f';Application={self.application}'
        return connection_string
