"""Feedbus client"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod
import asyncio
from asyncio import Queue
import logging
from typing import Optional, Set, List
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

class Client(metaclass=ABCMeta):
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
        self._read_queue: Queue = asyncio.Queue()
        self._write_queue: Queue = asyncio.Queue()
        self._token = asyncio.Event()

    @classmethod
    async def create(
            cls,
            host: str,
            port: int,
            *,
            authenticator: Optional[Authenticator] = None,
            ssl: Optional[SSLContext] = None,
            monitor_heartbeat: bool = False
    ) -> Client:
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
                raise RuntimeError(f'Invalid message type {message.message_type}')

        is_faulted = not self._token.is_set()
        if not is_faulted:
            await self._writer.close()

        await self.on_closed(is_faulted)

        LOGGER.info('Done')


    def stop(self):
        """Stop handling messages"""
        self._token.set()

    async def _read_message(self) -> Message:
        return await Message.read(self._reader)

    async def _raise_authorization_request(self, message: AuthorizationRequest) -> None:
        await self.on_authorization(
            message.client_id,
            message.host,
            message.user,
            message.feed,
            message.topic
        )

    @abstractmethod
    async def on_authorization(
            self,
            client_id: UUID,
            host: str,
            user: str,
            feed: str,
            topic: str
    ) -> None:
        """Called when authorization is requested"""

    async def _raise_multicast_data(self, message: ForwardedMulticastData) -> None:
        await self.on_data(
            message.user,
            message.host,
            message.feed,
            message.topic,
            message.data_packets,
            message.is_image
        )

    async def _raise_unicast_data(self, message: ForwardedUnicastData) -> None:
        await self.on_data(
            message.user,
            message.host,
            message.feed,
            message.topic,
            message.data_packets,
            message.is_image
        )

    @abstractmethod
    async def on_data(
            self,
            user: str,
            host: str,
            feed: str,
            topic: str,
            data_packets: Optional[List[DataPacket]],
            is_image: bool
    ) -> None:
        """Called when data is received"""

    async def _raise_forwarded_subscription_request(
            self,
            message: ForwardedSubscriptionRequest
    ) -> None:
        await self.on_forwarded_subscription_request(
            message.client_id,
            message.user,
            message.host,
            message.feed,
            message.topic,
            message.is_add
        )

    @abstractmethod
    async def on_forwarded_subscription_request(
            self,
            client_id: UUID,
            user: str,
            host: str,
            feed: str,
            topic: str,
            is_add: bool
    ) -> None:
        """Called for a notification"""

    @abstractmethod
    async def on_closed(self, is_faulted) -> None:
        """Called when the connection has been closed

        :param is_faulted: If true the connection was closed by the server
        :type is_faulted: bool
        """

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
