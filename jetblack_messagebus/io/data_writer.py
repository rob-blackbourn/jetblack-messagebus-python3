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
        """Write a boolean

        Args:
            val (bool): Th boolean value.
        """
        buf = struct.pack('?', val)
        self.writer.write(buf)

    def write_byte(self, val: int) -> None:
        """Write a byte

        Args:
            val (int): The value to write.
        """
        buf = struct.pack('b', val)
        self.writer.write(buf)

    def write_int(self, val) -> None:
        """Write an int

        Args:
            val ([type]): The int value.
        """
        self.writer.write(struct.pack('>i', val))

    def write_string(self, val: Optional[str], encoding: str = 'utf-8') -> None:
        """Writ a string.

        Args:
            val (Optional[str]): The string to write.
            encoding (str, optional): The encoding. Defaults to 'utf-8'.
        """
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            buf = val.encode(encoding)
            self.writer.write(buf)

    def write_byte_array(self, val: Optional[bytes]) -> None:
        """Write an array of bytes.

        Args:
            val (Optional[bytes]): The bytes to write.
        """
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            self.writer.write(val)

    def write_uuid(self, val: UUID) -> None:
        """Write a UUID

        Args:
            val (UUID): The id to write.
        """
        self.writer.write(val.bytes_le)

    def write_int_set(self, val: Optional[Set[int]]) -> None:
        """Writ a set of ints

        Args:
            val (Optional[Set[int]]): The set or None.
        """
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            for item in val:
                self.write_int(item)

    def write_data_packet(self, val: DataPacket) -> None:
        """Write a data packet.

        Args:
            val (DataPacket): The data packets.
        """
        self.write_int_set(val.entitlements)
        self.write_byte_array(val.data)

    def write_data_packet_array(self, val: Optional[List[DataPacket]]) -> None:
        """Write an array of data packets.

        Args:
            val (Optional[List[DataPacket]]): The data packets or None.
        """
        if val is None:
            self.write_int(0)
        else:
            self.write_int(len(val))
            for packet in val:
                self.write_data_packet(packet)

    async def drain(self) -> None:
        """Drain the writer.
        """
        await self.writer.drain()

    async def close(self) -> None:
        """Close the connection
        """
        if self.writer.can_write_eof():
            self.writer.write_eof()
            await self.writer.drain()
        self.writer.close()
        await self.writer.wait_closed()
