"""Tests for messages"""

import uuid
import pytest

from jetblack_messagebus.io import (
    DataReader,
    DataWriter,
    DataPacket
)
from jetblack_messagebus.messages import (
    Message,
    MulticastData,
    UnicastData,
    ForwardedSubscriptionRequest,
    NotificationRequest,
    SubscriptionRequest,
    AuthorizationRequest,
    AuthorizationResponse,
    ForwardedMulticastData,
    ForwardedUnicastData
)

from tests.mock_streams import MockStreamReader, MockStreamWriter

@pytest.mark.asyncio
async def test_multicast_data():
    """Test multicast data message"""
    source = MulticastData(
        'feed',
        'topic',
        True,
            [
            DataPacket({1, 2}, b'first'),
            DataPacket(None, b'second'),
        ]
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_unicast_data():
    """Test unicast data message"""
    source = UnicastData(
        uuid.UUID('12345678123456781234567812345678'),
        'feed',
        'topic',
        True,
            [
            DataPacket({1, 2}, b'first'),
            DataPacket(None, b'second'),
        ]
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_forwarded_subscription_request():
    """Test forwarded subscription request"""
    source = ForwardedSubscriptionRequest(
        'user',
        'host',
        uuid.UUID('12345678123456781234567812345678'),
        'feed',
        'topic',
        True
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_notification_request():
    """Test notification request"""
    source = NotificationRequest(
        'feed',
        True
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_subscription_request():
    """Test subscription request"""
    source = SubscriptionRequest(
        'feed',
        'topic',
        True
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_authorization_request():
    """Test forwarded subscription request"""
    source = AuthorizationRequest(
        uuid.UUID('12345678123456781234567812345678'),
        'host',
        'user',
        'feed',
        'topic'
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_authorization_response():
    """Test forwarded subscription response"""
    source = AuthorizationResponse(
        uuid.UUID('12345678123456781234567812345678'),
        'feed',
        'topic',
        True,
        {1, 2, 3}
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_forwarded_multicast_data():
    """Test forwarded multicast data message"""
    source = ForwardedMulticastData(
        'user',
        'host',
        'feed',
        'topic',
        True,
            [
            DataPacket({1, 2}, b'first'),
            DataPacket(None, b'second'),
        ]
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest

@pytest.mark.asyncio
async def test_forwarded_unicast_data():
    """Test forwarded unicast data message"""
    source = ForwardedUnicastData(
        'user',
        'host',
        uuid.UUID('12345678123456781234567812345678'),
        'feed',
        'topic',
        True,
            [
            DataPacket({1, 2}, b'first'),
            DataPacket(None, b'second'),
        ]
    )
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    await source.write(data_writer)
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    dest = await Message.read(data_reader)
    assert source == dest
