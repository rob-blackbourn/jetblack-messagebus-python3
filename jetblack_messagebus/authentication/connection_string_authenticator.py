"""Authentication Types"""

from abc import abstractmethod
from typing import Optional

from ..io import DataReader, DataWriter
from .authenticator import Authenticator


class ConnectionStringAuthenticator(Authenticator):
    """The abstract base for authenticators which use connection strings"""

    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        connection_string = self.to_connection_string()
        writer.write_string(connection_string)
        await writer.drain()

    @abstractmethod
    def to_connection_string(self) -> str:
        """Get the connection string.

        Returns:
            str: The connection string.
        """
