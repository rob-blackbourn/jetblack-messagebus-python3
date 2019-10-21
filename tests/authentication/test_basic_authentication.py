"""Test basic authentication"""

import pytest

from jetblack_messagebus.io import DataReader, DataWriter
from jetblack_messagebus.authentication import BasicAuthenticator

from tests.mock_streams import MockStreamReader, MockStreamWriter

@pytest.mark.asyncio
async def test_basic_authentication():
    """Test for BasicAuthenticator()"""
    
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)   
    stream_reader = MockStreamReader(b'')
    data_reader = DataReader(stream_reader)

    authenticator = BasicAuthenticator("username", "password", None, None, "application")
    await authenticator.authenticate(data_reader, data_writer);
    assert stream_writer.buf == b'\x00\x00\x00;Username=username;Password=password;Application=application'
