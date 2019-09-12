"""Data Writer"""

from asyncio import StreamWriter
import struct
from typing import Optional, Set, List
from uuid import UUID

from .data_packet import DataPacket

class DataWriter:
    """Data Writer"""

    def __init__(self, writer: StreamWriter) -> None:
        self.writer = writer


    def write_boolean(self, val: bool) -> None:
        """Write a boolean"""
        buf = struct.pack('?', val)
        self.writer.write(buf)


    def write_byte(self, val: int) -> None:
        """Write a byte"""
        buf = struct.pack('b', val)
        self.writer.write(buf)


    def write_unsigned_byte(self, val: int) -> None:
        """Write an unsigned byte"""
        buf = struct.pack('B', val)
        self.writer.write(buf)


    def write_short(self, val: int) -> None:
        """Write a 2 byte short"""
        buf = struct.pack('>h', val)
        self.writer.write(buf)


    def write_unsigned_short(self, val: int) -> None:
        """Write a 2 byte unsigned short"""
        buf = struct.pack('>H', val)
        self.writer.write(buf)


    def write_int(self, val) -> None:
        """Write a 4 byte int"""
        self.writer.write(struct.pack('>i', val))


    def write_long(self, val: int) -> None:
        """Write a 4 byte long"""
        buf = struct.pack('>q', val)
        self.writer.write(buf)


    def write_float(self, val: float) -> None:
        """Write a 4 byte float"""
        buf = struct.pack('>f', val)
        self.writer.write(buf)


    def write_double(self, val: int) -> None:
        """Write an 8 byte double"""
        buf = struct.pack('>d', val)
        self.writer.write(buf)


    def write_char(self, val: str) -> None:
        """Write a 2 byte char"""
        buf = struct.pack('>H', ord(val[0]))
        self.writer.write(buf)


    def write_string(self, val: Optional[str], encoding: str = 'utf-8') -> None:
        """Write a string"""
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            buf = val.encode(encoding)
            self.writer.write(buf)

    def write_byte_array(self, val: Optional[bytes]) -> None:
        """Write a byte array"""
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            self.writer.write(val)

    def write_uuid(self, val: UUID) -> None:
        """Write a UUID"""
        self.writer.write(val.bytes_le)

    def write_int_set(self, val: Optional[Set[int]]) -> None:
        """Write a set of integers"""
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            for item in val:
                self.write_int(item)

    def write_data_packet(self, val: DataPacket) -> None:
        """Write a data packet"""
        self.write_int_set(val.entitlements)
        self.write_byte_array(val.data)

    def write_data_packet_array(self, val: Optional[List[DataPacket]]) -> None:
        """Write a list of data packets

        :param val: The list of data packets
        :type val: Optional[List[DataPacket]]
        """
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            for packet in val:
                self.write_data_packet(packet)

    async def drain(self) -> None:
        """Drain the writer"""
        await self.writer.drain()
