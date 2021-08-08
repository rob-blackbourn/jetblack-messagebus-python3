"""Authentication Types"""

from abc import ABCMeta, abstractmethod

from ..io import DataReader, DataWriter


class Authenticator(metaclass=ABCMeta):

    @abstractmethod
    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        """Authenticate the client"""
