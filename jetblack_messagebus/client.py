"""Feedbus client"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod
import asyncio
from asyncio import Queue
import logging
from typing import Optional, Set, List, cast
from ssl import SSLContext
from uuid import UUID

try:
    from jetblack_negotiate_stream import open_negotiate_stream
except ImportError:
    pass

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
from .authentication import Authenticator, NullAuthenticator, SspiAuthenticator
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
        """Create the client

        Args:
            host (str): The host name of the distributor.
            port (int): The distributor port
            authenticator (Optional[Authenticator], optional): An authenticator. Defaults to None.
            ssl (Optional[SSLContext], optional): The context for an ssl connection. Defaults to None.
            monitor_heartbeat (bool, optional): If true use the monitor heartbeat. Defaults to False.

        Returns:
            Client: The connected client.
        """
        if authenticator is None:
            authenticator = NullAuthenticator()

        reader, writer = await asyncio.open_connection(host, port, ssl=ssl)

        return cls(
            DataReader(reader),
            DataWriter(writer),
            authenticator,
            monitor_heartbeat
        )


    @classmethod
    async def create_sspi(
            cls,
            host: str,
            port: int,
            *,
            authenticator: Optional[Authenticator] = None,
            monitor_heartbeat: bool = False
    ) -> Client:
        """Create the client using SSPI authentication.

        Args:
            host (str): The host name of the distributor.
            port (int): The distributor port
            authenticator (Optional[Authenticator], optional): An authenticator. Defaults to None.
            monitor_heartbeat (bool, optional): If true use the monitor heartbeat. Defaults to False.

        Returns:
            Client: The connected client.
        """
        if authenticator is None:
            authenticator = SspiAuthenticator()

        reader, writer = await open_negotiate_stream(host, port)

        return cls(
            DataReader(reader), # type: ignore
            DataWriter(writer), # type: ignore
            authenticator,
            monitor_heartbeat
        )

    async def start(self) -> None:
        """Start handling messages"""

        if self._authenticator:
            await self._authenticator.authenticate(self._reader, self._writer)

        if self._monitor_heartbeat:
            await self.add_subscription('__admin__', 'heartbeat')

        async for message in read_aiter(self._read, self._write, self._dequeue, self._token):
            if message.message_type == MessageType.AUTHORIZATION_REQUEST:
                await self._raise_authorization_request(
                    cast(AuthorizationRequest, message)
                )
            elif message.message_type == MessageType.FORWARDED_MULTICAST_DATA:
                await self._raise_multicast_data(
                    cast(ForwardedMulticastData, message)
                )
            elif message.message_type == MessageType.FORWARDED_UNICAST_DATA:
                await self._raise_unicast_data(
                    cast(ForwardedUnicastData, message)
                )
            elif message.message_type == MessageType.FORWARDED_SUBSCRIPTION_REQUEST:
                await self._raise_forwarded_subscription_request(
                    cast(ForwardedSubscriptionRequest, message)
                )
            else:
                raise RuntimeError(
                    f'Invalid message type {message.message_type}')

        is_faulted = not self._token.is_set()
        if not is_faulted:
            await self._writer.close()

        await self.on_closed(is_faulted)

        LOGGER.info('Done')

    def stop(self) -> None:
        """Stop handling messages"""
        self._token.set()

    async def _read_message(self) -> Message:
        return await Message.read(self._reader)

    async def _raise_authorization_request(
            self,
            message: AuthorizationRequest
    ) -> None:
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

    async def _raise_multicast_data(
            self,
            message: ForwardedMulticastData
    ) -> None:
        await self.on_data(
            message.user,
            message.host,
            message.feed,
            message.topic,
            message.data_packets,
            message.content_type
        )

    async def _raise_unicast_data(
            self,
            message: ForwardedUnicastData
    ) -> None:
        await self.on_data(
            message.user,
            message.host,
            message.feed,
            message.topic,
            message.data_packets,
            message.content_type
        )

    @abstractmethod
    async def on_data(
            self,
            user: str,
            host: str,
            feed: str,
            topic: str,
            data_packets: Optional[List[DataPacket]],
            content_type: str
    ) -> None:
        """Called when data is received

        Args:
            user (str): The user name of the sender.
            host (str): The host from which the data was sent.
            feed (str): The feed name.
            topic (str): The topic name.
            data_packets (Optional[List[DataPacket]]): The data packets.
            content_type (str): The type of the message contents.
        """

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
        """Called for a notification.

        Args:
            client_id (UUID): An identifier for the client.
            user (str): The name of the user that requested the subscription.
            host (str): The host from which the subscription was requested.
            feed (str): The feed name.
            topic (str): The topic name.
            is_add (bool): If true the request was to add a subscription.
        """

    @abstractmethod
    async def on_closed(self, is_faulted: bool) -> None:
        """Called when the connection has been closed

        Args:
            is_faulted (bool): If true the connection was closed by the server
        """

    async def authorize(
            self,
            client_id: UUID,
            feed: str,
            topic: str,
            is_authorization_required: bool,
            entitlements: Optional[Set[int]]
    ) -> None:
        """Send an authorization response.

        Args:
            client_id (UUID): An identifier for the client.
            feed (str): The feed name.
            topic (str): The topic name.
            is_authorization_required (bool): If True, authorization is required.
            entitlements (Optional[Set[int]]): The entitlements of the user.
        """
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
            content_type: str,
            data_packets: Optional[List[DataPacket]]
    ) -> None:
        """Publish data to subscribers

        Args:
            feed (str): The feed name.
            topic (str): The topic name.
            content_type (str): The type of the message contents.
            data_packets (Optional[List[DataPacket]]): Th data packets.
        """
        await self._write_queue.put(
            MulticastData(
                feed,
                topic,
                content_type,
                data_packets
            )
        )

    async def send(
            self,
            client_id: UUID,
            feed: str,
            topic: str,
            content_type: str,
            data_packets: Optional[List[DataPacket]]
    ) -> None:
        """Send data to a client

        Args:
            client_id (UUID): The clint id.
            feed (str): The feed name.
            topic (str): The topic name.
            content_type (str): The type of the message contents.
            data_packets (Optional[List[DataPacket]]): Th data packets.
        """
        await self._write_queue.put(
            UnicastData(
                client_id,
                feed,
                topic,
                content_type,
                data_packets
            )
        )

    async def add_subscription(self, feed: str, topic: str) -> None:
        """Add a subscription

        Args:
            feed (str): The feed name.
            topic (str): The topic name.
        """
        await self._write_queue.put(
            SubscriptionRequest(
                feed,
                topic,
                True
            )
        )

    async def remove_subscription(self, feed: str, topic: str) -> None:
        """Remove a subscription

        Args:
            feed (str): The feed name.
            topic (str): The topic name.
        """
        await self._write_queue.put(
            SubscriptionRequest(
                feed,
                topic,
                False
            )
        )

    async def add_notification(self, feed: str) -> None:
        """Add a notification

        Args:
            feed (str): The feed name.
        """
        await self._write_queue.put(
            NotificationRequest(
                feed,
                True
            )
        )

    async def remove_notification(self, feed: str) -> None:
        """Remove a notification

        Args:
            feed (str): The feed name.
        """
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
