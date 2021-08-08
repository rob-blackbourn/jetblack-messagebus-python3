"""Authentication Types"""

from abc import abstractmethod
from typing import Optional

from ..io import DataReader, DataWriter
from .types import Authenticator


class ConnectionStringAuthenticator(Authenticator):
    """Base class for authentication"""

    def __init__(
            self,
            impersonating: Optional[str] = None,
            forwarded_for: Optional[str] = None,
            application: Optional[str] = None
    ) -> None:
        self.impersonating = impersonating
        self.forwarded_for = forwarded_for
        self.application = application

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        connection_string = self.to_connection_string()
        if connection_string:
            writer.write_string(connection_string)
            await writer.drain()

    @abstractmethod
    def to_connection_string(self) -> Optional[str]:
        """Get the connection string.

        Returns:
            Optional[str]: The connection string.
        """
