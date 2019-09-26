"""Test Serialization"""

import uuid
import pytest

from jetblack_messagebus.io import DataReader, DataWriter

from tests.mock_streams import MockStreamReader, MockStreamWriter

@pytest.mark.asyncio
async def test_roundtrip():
    """Test round trip serialization"""
    stream_writer = MockStreamWriter()
    data_writer = DataWriter(stream_writer)
    data_writer.write_boolean(True)
    data_writer.write_boolean(False)
    data_writer.write_byte(32)
    data_writer.write_int(42)
    data_writer.write_string('This is not a test')
    data_writer.write_uuid(uuid.UUID('12345678123456781234567812345678'))
    stream_reader = MockStreamReader(stream_writer.buf)
    data_reader = DataReader(stream_reader)
    assert await data_reader.read_boolean() == True
    assert await data_reader.read_boolean() == False
    assert await data_reader.read_byte() == 32
    assert await data_reader.read_int() == 42
    assert await data_reader.read_string() == 'This is not a test'
    assert await data_reader.read_uuid() == uuid.UUID('12345678123456781234567812345678')
    print("Done")    

