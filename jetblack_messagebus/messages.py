"""Messages"""

from __future__ import annotations
from abc import ABCMeta, abstractmethod, abstractclassmethod
from enum import Enum
from typing import Optional, Set, List
from uuid import UUID
from .io import DataReader, DataWriter, DataPacket


class MessageType(Enum):
    """Message types"""
    MULTICAST_DATA = 1
    UNICAST_DATA = 2
    FORWARDED_SUBSCRIPTION_REQUEST = 3
    NOTIFICATION_REQUEST = 4
    SUBSCRIPTION_REQUEST = 5
    AUTHORIZATION_REQUEST = 6
    AUTHORIZATION_RESPONSE = 7
    FORWARDED_MULTICAST_DATA = 8
    FORWARDED_UNICAST_DATA = 9

class Message(metaclass=ABCMeta):
    """Message Base Class"""

    def __init__(self, message_type: MessageType) -> None:
        self.message_type = message_type

    @classmethod
    async def read(cls, reader: DataReader) -> Message:
        """Read a message"""
        message_type = await cls.read_header(reader)

        if message_type == MessageType.MULTICAST_DATA:
            return await MulticastData.read_body(reader)
        elif message_type == MessageType.UNICAST_DATA:
            return await UnicastData.read_body(reader)
        elif message_type == MessageType.FORWARDED_SUBSCRIPTION_REQUEST:
            return await ForwardedSubscriptionRequest.read_body(reader)
        elif message_type == MessageType.NOTIFICATION_REQUEST:
            return await NotificationRequest.read_body(reader)
        elif message_type == MessageType.SUBSCRIPTION_REQUEST:
            return await SubscriptionRequest.read_body(reader)
        elif message_type == MessageType.AUTHORIZATION_REQUEST:
            return await AuthorizationRequest.read_body(reader)
        elif message_type == MessageType.AUTHORIZATION_RESPONSE:
            return await AuthorizationResponse.read_body(reader)
        elif message_type == MessageType.FORWARDED_MULTICAST_DATA:
            return await ForwardedMulticastData.read_body(reader)
        elif message_type == MessageType.FORWARDED_UNICAST_DATA:
            return await ForwardedUnicastData.read_body(reader)
        else:
            raise RuntimeError(f'Invalid message type {message_type}')

    @classmethod
    async def read_header(cls, reader: DataReader) -> MessageType:
        """Read the message header"""
        message_type = await reader.read_byte()
        return MessageType(int(message_type))

    def write_header(self, writer: DataWriter) -> None:
        """Write the message header"""
        writer.write_byte(self.message_type.value)

    @abstractmethod
    async def write(self, writer: DataWriter) -> None:
        """Write the message"""

    @abstractclassmethod
    async def read_body(cls, reader: DataReader) -> Message:
        """Read message the body"""

class MulticastData(Message):
    """A multicast data message"""

    def __init__(
            self,
            feed: str,
            topic: str,
            is_image: bool,
            data_packets: Optional[List[DataPacket]]
    ) -> None:
        super().__init__(MessageType.MULTICAST_DATA)
        self.feed = feed
        self.topic = topic
        self.is_image = is_image
        self.data_packets = data_packets

    @classmethod
    async def read_body(cls, reader: DataReader) -> MulticastData:
        feed = await reader.read_string()
        topic = await reader.read_string()
        is_image = await reader.read_boolean()
        data_packets = await reader.read_data_packet_array()
        return MulticastData(feed, topic, is_image, data_packets)

    async def write(self, writer: DataWriter) -> None:
        self.write_header(writer)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        writer.write_boolean(self.is_image)
        writer.write_data_packet_array(self.data_packets)
        await writer.drain()

    def __str__(self) -> str:
        return 'MulticastData(feed="{}",topic="{}",is_image={},data_packets={})'.format(
            self.feed,
            self.topic,
            self.is_image,
            self.data_packets
        )

class UnicastData(Message):
    """A unicast data messsage"""

    def __init__(
            self,
            client_id: UUID,
            feed: str,
            topic: str,
            is_image: bool,
            data_packets: Optional[List[DataPacket]]
    ) -> None:
        super().__init__(MessageType.UNICAST_DATA)
        self.client_id = client_id
        self.feed = feed
        self.topic = topic
        self.is_image = is_image
        self.data_packets = data_packets


    @classmethod
    async def read_body(cls, reader: DataReader) -> UnicastData:
        client_id = await reader.read_uuid()
        feed = await reader.read_string()
        topic = await reader.read_string()
        is_image = await reader.read_boolean()
        data_packets = await reader.read_data_packet_array()
        return UnicastData(client_id, feed, topic, is_image, data_packets)

    async def write(self, writer: DataWriter) -> None:
        self.write_header(writer)
        writer.write_uuid(self.client_id)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        writer.write_boolean(self.is_image)
        writer.write_data_packet_array(self.data_packets)
        await writer.drain()

    def __str__(self) -> str:
        return 'UnicastData(client_id={},feed="{}",topic="{}",is_image={},data_packets={})'.format(
            self.client_id,
            self.feed,
            self.topic,
            self.is_image,
            self.data_packets
        )

class ForwardedSubscriptionRequest(Message):
    """A forwarded subscription request"""

    def __init__(
            self,
            user: str,
            host: str,
            client_id: UUID,
            feed: str,
            topic: str,
            is_add: bool
    ) -> None:
        super().__init__(MessageType.FORWARDED_SUBSCRIPTION_REQUEST)
        self.user = user
        self.host = host
        self.client_id = client_id
        self.feed = feed
        self.topic = topic
        self.is_add = is_add

    @classmethod
    async def read_body(cls, reader: DataReader) -> ForwardedSubscriptionRequest:
        user = await reader.read_string()
        host = await reader.read_string()
        client_id = await reader.read_uuid()
        feed = await reader.read_string()
        topic = await reader.read_string()
        is_add = await reader.read_boolean()
        return ForwardedSubscriptionRequest(user, host, client_id, feed, topic, is_add)

    async def write(self, writer: DataWriter) -> None:
        self.write_header(writer)
        writer.write_string(self.user)
        writer.write_string(self.host)
        writer.write_uuid(self.client_id)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        writer.write_boolean(self.is_add)
        await writer.drain()

    def __str__(self) -> str:
        # pylint: disable=line-too-long
        return 'ForwardedSubscriptionRequest(user="{}",host="{}",client_id={},feed="{}",topic="{}",is_add={})'.format(
            self.user,
            self.host,
            self.client_id,
            self.feed,
            self.topic,
            self.is_add
        )

class NotificationRequest(Message):
    """A notification request message"""

    def __init__(self, feed: str, is_add: bool) -> None:
        super().__init__(MessageType.NOTIFICATION_REQUEST)
        self.feed = feed
        self.is_add = is_add

    @classmethod
    async def read_body(cls, reader: DataReader) -> NotificationRequest:
        feed = await reader.read_string()
        is_add = await reader.read_boolean()
        return NotificationRequest(feed, is_add)

    async def write(self, writer: DataWriter) -> None:
        self.write_header(writer)
        writer.write_string(self.feed)
        writer.write_boolean(self.is_add)
        await writer.drain()

    def __str__(self) -> str:
        return 'NotificationRequest(feed="{}",is_add={})'.format(
            self.feed,
            self.is_add
        )

class SubscriptionRequest(Message):
    """A subscription request message"""

    def __init__(self, feed: str, topic: str, is_add: bool) -> None:
        super().__init__(MessageType.SUBSCRIPTION_REQUEST)
        self.feed = feed
        self.topic = topic
        self.is_add = is_add

    @classmethod
    async def read_body(cls, reader: DataReader) -> Message:
        feed = await reader.read_string()
        topic = await reader.read_string()
        is_add = await reader.read_boolean()
        return SubscriptionRequest(feed, topic, is_add)

    async def write(self, writer: DataWriter) -> None:
        self.write_header(writer)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        writer.write_boolean(self.is_add)
        await writer.drain()

    def __str__(self) -> str:
        return 'SubscriptionRequest(feed="{}",topic="{}",is_add={})'.format(
            self.feed,
            self.topic,
            self.is_add
        )

class AuthorizationRequest(Message):
    """An authorization request message"""

    def __init__(self, client_id: UUID, host: str, user: str, feed: str, topic: str) -> None:
        super().__init__(MessageType.AUTHORIZATION_REQUEST)
        self.client_id = client_id
        self.host = host
        self.user = user
        self.feed = feed
        self.topic = topic

    @classmethod
    async def read_body(cls, reader: DataReader) -> Message:
        client_id = await reader.read_uuid()
        host = await reader.read_string()
        user = await reader.read_string()
        feed = await reader.read_string()
        topic = await reader.read_string()
        return AuthorizationRequest(client_id, host, user, feed, topic)

    async def write(self, writer: DataWriter) -> None:
        self.write_header(writer)
        writer.write_uuid(self.client_id)
        writer.write_string(self.host)
        writer.write_string(self.user)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        await writer.drain()

    def __str__(self):
        return 'AuthorizationRequest(client_id={},host="{}",user="{}",feed="{}",topic="{}"'.format(
            self.client_id,
            self.host,
            self.user,
            self.feed,
            self.topic
        )

class AuthorizationResponse(Message):
    """An authorization response"""

    def __init__(
            self,
            client_id: UUID,
            feed: str,
            topic: str,
            is_authorization_required: bool,
            entitlements: Optional[Set[int]]
    ) -> None:
        super().__init__(MessageType.AUTHORIZATION_RESPONSE)
        self.client_id = client_id
        self.feed = feed
        self.topic = topic
        self.is_authorization_required = is_authorization_required
        self.entitlements = entitlements

    @classmethod
    async def read_body(cls, reader: DataReader) -> Message:
        client_id = await reader.read_uuid()
        feed = await reader.read_string()
        topic = await reader.read_string()
        is_authorization_required = await reader.read_boolean()
        entitlements = await reader.read_int_set()
        return AuthorizationResponse(
            client_id,
            feed,
            topic,
            is_authorization_required,
            entitlements
        )

    async def write(self, writer: DataWriter) -> None:
        self.write_header(writer)
        writer.write_uuid(self.client_id)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        writer.write_boolean(self.is_authorization_required)
        writer.write_int_set(self.entitlements)
        await writer.drain()

    def __str__(self):
        # pylint: disable=line-too-long
        return 'AuthorizationResponse(client_id={},feed="{}",topic="{}",is_authorization_required={},entitlements={}'.format(
            self.client_id,
            self.feed,
            self.topic,
            self.is_authorization_required,
            self.entitlements
        )

class ForwardedMulticastData(Message):
    """A forwarded multicast data message"""

    def __init__(
            self,
            user: str,
            host: str,
            feed: str,
            topic: str,
            is_image: bool,
            data_packets: Optional[List[DataPacket]]
    ) -> None:
        super().__init__(MessageType.FORWARDED_MULTICAST_DATA)
        self.user = user
        self.host = host
        self.feed = feed
        self.topic = topic
        self.is_image = is_image
        self.data_packets = data_packets

    @classmethod
    async def read_body(cls, reader: DataReader) -> Message:
        user = await reader.read_string()
        host = await reader.read_string()
        feed = await reader.read_string()
        topic = await reader.read_string()
        is_image = await reader.read_boolean()
        data_packets = await reader.read_data_packet_array()
        return ForwardedMulticastData(user, host, feed, topic, is_image, data_packets)

    async def write(self, writer: DataWriter) -> None:
        writer.write_string(self.user)
        writer.write_string(self.host)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        writer.write_boolean(self.is_image)
        writer.write_data_packet_array(self.data_packets)
        await writer.drain()

    def __str__(self):
        # pylint: disable=line-too-long
        return 'ForwardedMulticastData(user="{}",host="{}",feed="{}",topic="{}",is_image={},data_packets={}'.format(
            self.user,
            self.host,
            self.feed,
            self.topic,
            self.is_image,
            self.data_packets
        )

class ForwardedUnicastData(Message):
    """A forwarded unicast message"""

    def __init__(
            self,
            user: str,
            host: str,
            client_id: UUID,
            feed: str,
            topic: str,
            is_image: bool,
            data_packets: Optional[List[DataPacket]]
    ):
        super().__init__(MessageType.FORWARDED_MULTICAST_DATA)
        self.user = user
        self.host = host
        self.client_id = client_id
        self.feed = feed
        self.topic = topic
        self.is_image = is_image
        self.data_packets = data_packets

    @classmethod
    async def read_body(cls, reader: DataReader) -> Message:
        user = await reader.read_string()
        host = await reader.read_string()
        client_id = await reader.read_uuid()
        feed = await reader.read_string()
        topic = await reader.read_string()
        is_image = await reader.read_boolean()
        data_packets = await reader.read_data_packet_array()
        return ForwardedUnicastData(user, host, client_id, feed, topic, is_image, data_packets)

    async def write(self, writer: DataWriter) -> None:
        writer.write_string(self.user)
        writer.write_string(self.host)
        writer.write_uuid(self.client_id)
        writer.write_string(self.feed)
        writer.write_string(self.topic)
        writer.write_boolean(self.is_image)
        writer.write_data_packet_array(self.data_packets)
        await writer.drain()

    def __str__(self):
        # pylint: disable=line-too-long
        return 'ForwardedUnicastData(user="{}",host="{}",client_id={},feed="{}",topic="{}",is_image={},data_packets={}'.format(
            self.user,
            self.host,
            self.client_id,
            self.feed,
            self.topic,
            self.is_image,
            self.data_packets
        )
