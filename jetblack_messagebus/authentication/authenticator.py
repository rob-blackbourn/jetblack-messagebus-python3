"""Authenticator"""

from abc import ABCMeta, abstractmethod
from typing import Optional

from ..io import DataReader, DataWriter


class Authenticator(metaclass=ABCMeta):

    def __init__(
            self,
            impersonating: Optional[str] = None,
            forwarded_for: Optional[str] = None,
            application: Optional[str] = None
    ) -> None:
        self.impersonating = impersonating
        self.forwarded_for = forwarded_for
        self.application = application

    @abstractmethod
    async def authenticate(self, reader: DataReader, writer: DataWriter) -> None:
        """Authenticate the client"""
