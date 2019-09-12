"""Feedbus client"""

from __future__ import annotations
import asyncio
from asyncio import Queue
import logging
from typing import Optional, Set, List, Callable, Awaitable
from ssl import SSLContext
from uuid import UUID

from .io import DataReader, DataWriter, DataPacket
from .messages import (
    MessageType,
    Message,
    SubscriptionRequest,
    NotificationRequest,
    ForwardedSubscriptionRequest,
    MulticastData,
    UnicastData,
    AuthorizationRequest,
    AuthorizationResponse,
    ForwardedMulticastData,
    ForwardedUnicastData
)
from .authentication import Authenticator
from .utils import read_aiter

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


class CallbackClient():
    """Feedbus client"""

    def __init__(
            self,
            reader: DataReader,
            writer: DataWriter,
            authenticator: Optional[Authenticator],
            monitor_heartbeat: bool
    ):
        self._reader = reader
        self._writer = writer
        self._authenticator = authenticator
        self._monitor_heartbeat = monitor_heartbeat
        self._authorization_handlers: List[AuthorizationHandler] = list()
        self._data_handlers: List[DataHandler] = list()
        self._notification_handlers: List[NotificationHandler] = list()
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

    @classmethod
    async def create(
            cls,
            host: str,
            port: int,
            *,
            authenticator: Optional[Authenticator] = None,
            ssl: Optional[SSLContext] = None,
            monitor_heartbeat: bool = False
    ) -> CallbackClient:
        """Create the client"""
        reader, writer = await asyncio.open_connection(host, port, ssl=ssl)
        return cls(DataReader(reader), DataWriter(writer), authenticator, monitor_heartbeat)

    async def start(self):
        """Start handling messages"""

        if self._authenticator:
            await self._authenticator.authenticate(self._reader, self._writer)

        if self._monitor_heartbeat:
            await self.add_subscription('__admin__', 'heartbeat')

        async for message in read_aiter(self._read, self._write, self._dequeue, self._token):
            if message.message_type == MessageType.AUTHORIZATION_REQUEST:
                await self._raise_authorization_request(message)
            elif message.message_type == MessageType.FORWARDED_MULTICAST_DATA:
                await self._raise_multicast_data(message)
            elif message.message_type == MessageType.FORWARDED_UNICAST_DATA:
                await self._raise_unicast_data(message)
            elif message.message_type == MessageType.FORWARDED_SUBSCRIPTION_REQUEST:
                await self._raise_forwarded_subscription_request(message)
            else:
                raise RuntimeError(
                    f'Invalid message type {message.message_type}')

        LOGGER.info('Done')

    def stop(self):
        """Stop handling messages"""
        self._token.set()

    async def _raise_authorization_request(self, message: AuthorizationRequest) -> None:
        for handler in self._authorization_handlers:
            await handler(
                message.client_id,
                message.host,
                message.user,
                message.feed,
                message.topic
            )

    async def _raise_multicast_data(self, message: ForwardedMulticastData) -> None:
        for handler in self._data_handlers:
            await handler(
                message.user,
                message.host,
                message.feed,
                message.topic,
                message.data_packets,
                message.is_image
            )

    async def _raise_unicast_data(self, message: ForwardedUnicastData) -> None:
        for handler in self._data_handlers:
            await handler(
                message.user,
                message.host,
                message.feed,
                message.topic,
                message.data_packets,
                message.is_image
            )

    async def _raise_forwarded_subscription_request(
            self,
            message: ForwardedSubscriptionRequest
    ) -> None:
        for handler in self._notification_handlers:
            await handler(
                message.client_id,
                message.user,
                message.host,
                message.feed,
                message.topic,
                message.is_add
            )

    async def authorize(
            self,
            client_id: UUID,
            feed: str,
            topic: str,
            is_authorization_required: bool,
            entitlements: Optional[Set[int]]
    ) -> None:
        """Send an authorization response"""
        await self._write_queue.put(
            AuthorizationResponse(
                client_id,
                feed,
                topic,
                is_authorization_required,
                entitlements
            )
        )

    async def publish(
            self,
            feed: str,
            topic: str,
            is_image: bool,
            data_packets: Optional[List[DataPacket]]
    ) -> None:
        """Publish data to subscribers"""
        await self._write_queue.put(
            MulticastData(
                feed,
                topic,
                is_image,
                data_packets
            )
        )

    async def send(
            self,
            client_id: UUID,
            feed: str,
            topic: str,
            is_image: bool,
            data_packets: Optional[List[DataPacket]]
    ) -> None:
        """Send data to a client"""
        await self._write_queue.put(
            UnicastData(
                client_id,
                feed,
                topic,
                is_image,
                data_packets
            )
        )

    async def add_subscription(self, feed: str, topic: str) -> None:
        """Add a subscription"""
        await self._write_queue.put(
            SubscriptionRequest(
                feed,
                topic,
                True
            )
        )

    async def remove_subscription(self, feed: str, topic: str) -> None:
        """Remove a subscription"""
        await self._write_queue.put(
            SubscriptionRequest(
                feed,
                topic,
                False
            )
        )

    async def add_notification(self, feed: str) -> None:
        """Add a notification"""
        await self._write_queue.put(
            NotificationRequest(
                feed,
                True
            )
        )

    async def remove_notification(self, feed: str) -> None:
        """Remove a notification"""
        await self._write_queue.put(
            NotificationRequest(
                feed,
                False
            )
        )

    async def _read(self) -> None:
        message = await Message.read(self._reader)
        await self._read_queue.put(message)

    async def _dequeue(self) -> Message:
        return await self._read_queue.get()

    async def _write(self):
        message = await self._write_queue.get()
        await message.write(self._writer)
