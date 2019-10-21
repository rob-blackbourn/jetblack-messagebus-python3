"""Feedbus client"""

from __future__ import annotations
import asyncio
from asyncio import Queue
import logging
from typing import Optional, List, Callable, Awaitable
from uuid import UUID

from .client import Client
from .io import DataReader, DataWriter, DataPacket
from .authentication import Authenticator

LOGGER = logging.getLogger(__name__)

AuthorizationHandler = Callable[
    [UUID, str, str, str, str],
    Awaitable[None]
]
DataHandler = Callable[
    [str, str, str, str, Optional[List[DataPacket]], bool],
    Awaitable[None]
]
NotificationHandler = Callable[
    [UUID, str, str, str, str, bool],
    Awaitable[None]
]
ClosedHandler = Callable[
    [bool],
    Awaitable[None]
]


class CallbackClient(Client):
    """Feedbus callback client"""

    def __init__(
            self,
            reader: DataReader,
            writer: DataWriter,
            authenticator: Optional[Authenticator],
            monitor_heartbeat: bool
    ):
        super().__init__(reader, writer, authenticator, monitor_heartbeat)
        self._authorization_handlers: List[AuthorizationHandler] = list()
        self._data_handlers: List[DataHandler] = list()
        self._notification_handlers: List[NotificationHandler] = list()
        self._closed_handlers: List[ClosedHandler] = list()
        self._read_queue: Queue = asyncio.Queue()
        self._write_queue: Queue = asyncio.Queue()
        self._token = asyncio.Event()

    @property
    def authorization_handlers(self) -> List[AuthorizationHandler]:
        """The list of handlers called when an authorization request is
        received.

        :return: The list of handlers
        :rtype: List[AuthorizationHandler]
        """
        return self._authorization_handlers

    @property
    def data_handlers(self) -> List[DataHandler]:
        """The list of handlers called when data is received.

        :return: The list of handlers
        :rtype: List[DataHandler]
        """
        return self._data_handlers

    @property
    def notification_handlers(self) -> List[NotificationHandler]:
        """The list of handlers called when a notification is received

        :return: The list of handlers
        :rtype: List[NotificationHandler]
        """
        return self._notification_handlers

    @property
    def closed_handlers(self) -> List[ClosedHandler]:
        """The list of handlers called when a connection is closed

        :return: The list of handlers
        :rtype: List[ClosedHandler]
        """
        return self._closed_handlers

    async def on_authorization(
            self,
            client_id: UUID,
            host: str,
            user: str,
            feed: str,
            topic: str
    ) -> None:
        for handler in self._authorization_handlers:
            await handler(
                client_id,
                host,
                user,
                feed,
                topic
            )

    async def on_data(
            self,
            user: str,
            host: str,
            feed: str,
            topic: str,
            data_packets: Optional[List[DataPacket]],
            is_image: bool
    ) -> None:
        for handler in self._data_handlers:
            await handler(
                user,
                host,
                feed,
                topic,
                data_packets,
                is_image
            )

    async def on_forwarded_subscription_request(
            self,
            client_id: UUID,
            user: str,
            host: str,
            feed: str,
            topic: str,
            is_add: bool
    ):
        for handler in self._notification_handlers:
            await handler(
                client_id,
                user,
                host,
                feed,
                topic,
                is_add
            )

    async def on_closed(self, is_faulted):
        for handler in self._closed_handlers:
            await handler(is_faulted)
