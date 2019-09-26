"""Data Reader"""

from asyncio import StreamReader
import struct
from typing import Optional, Set, List
from uuid import UUID

from .data_packet import DataPacket

class DataReader:
    """A portable data reader class"""

    def __init__(self, reader: StreamReader) -> None:
        self.reader = reader


    async def read_boolean(self) -> bool:
        """Read a boolean"""
        buf = await self.reader.readexactly(1)
        return struct.unpack('?', buf)[0]


    async def read_byte(self) -> int:
        """RRead a byte"""
        buf = await self.reader.readexactly(1)
        return struct.unpack('b', buf)[0]


    async def read_unsigned_byte(self) -> int:
        """Read an unsigned byte"""
        buf = await self.reader.readexactly(1)
        return struct.unpack('B', buf)[0]


    async def read_short(self) -> int:
        """Read a 2 byte short"""
        buf = await self.reader.readexactly(2)
        return struct.unpack('>h', buf)[0]


    async def read_unsigned_short(self) -> int:
        """Read a 2 byte unsigned short"""
        buf = await self.reader.readexactly(2)
        return struct.unpack('>H', buf)[0]


    async def read_int(self) -> int:
        """Read a 4 byte int"""
        buf = await self.reader.readexactly(4)
        return struct.unpack('>i', buf)[0]


    async def read_long(self) -> int:
        """Read an 8 byte long"""
        buf = await self.reader.readexactly(8)
        return struct.unpack('>q', buf)[0]


    async def read_char(self) -> str:
        """Read a 2 byte char"""
        buf = await self.reader.readexactly(2)
        return chr(struct.unpack('>H', buf)[0])


    async def read_float(self) -> float:
        """Read a 4 byte float"""
        buf = await self.reader.readexactly(4)
        return struct.unpack('>f', buf)[0]


    async def read_double(self) -> float:
        """Read an 8 byte double"""
        buf = await self.reader.readexactly(8)
        return struct.unpack('>d', buf)[0]


    async def read_string(self, encoding: str = 'utf-8') -> str:
        """Read a string"""
        utf_len = await self.read_int()
        buf = await self.reader.readexactly(utf_len)
        return buf.decode(encoding)

    async def read_byte_array(self) -> Optional[bytes]:
        """Read a byte array"""
        count = await self.read_int()
        if count == 0:
            return None
        buf = await self.reader.readexactly(count)
        return buf

    async def read_uuid(self) -> UUID:
        """Read a UUID"""
        buf = await self.reader.readexactly(16)
        return UUID(bytes_le=buf)


    async def read_int_set(self) -> Optional[Set[int]]:
        """Read a set of ints"""
        count = await self.read_int()
        if count == 0:
            return None
        data = set()
        for _ in range(count):
            value = await self.read_int()
            data.add(value)
        return data

    async def read_data_packet(self) -> DataPacket:
        """Read a data packet"""
        entitlements = await self.read_int_set()
        data = await self.read_byte_array()
        return DataPacket(entitlements, data)

    async def read_data_packet_array(self) -> Optional[List[DataPacket]]:
        """Read a list of data packets

        :return: A list of data packets
        :rtype: Optional[List[DataPacket]]
        """
        count = await self.read_int()
        if count == 0:
            return None
        packets: List[DataPacket] = list()
        for _ in range(count):
            packet = await self.read_data_packet()
            packets.append(packet)
        return packets
