"""Data Reader"""

from asyncio import StreamReader
import struct
from typing import Optional, Set, List
from uuid import UUID

from .data_packet import DataPacket


class DataReader:
    """A data reader class"""

    def __init__(self, reader: StreamReader) -> None:
        self.reader = reader

    async def read_boolean(self) -> bool:
        """Read a boolean.

        Returns:
            bool: The boolean.
        """
        buf = await self.reader.readexactly(1)
        return struct.unpack('?', buf)[0]

    async def read_byte(self) -> int:
        """Read a byte.

        Returns:
            int: The byte.
        """
        buf = await self.reader.readexactly(1)
        return struct.unpack('b', buf)[0]

    async def read_int(self) -> int:
        """Read an int.

        Returns:
            int: The int.
        """
        buf = await self.reader.readexactly(4)
        return struct.unpack('>i', buf)[0]

    async def read_string(self, encoding: str = 'utf-8') -> str:
        """Read a string.

        Args:
            encoding (str, optional): The encoding. Defaults to 'utf-8'.

        Returns:
            str: The string.
        """
        count = await self.read_int()
        buf = await self.reader.readexactly(count)
        return buf.decode(encoding)

    async def read_byte_array(self) -> Optional[bytes]:
        """Read an array of bytes.

        Returns:
            Optional[bytes]: The bytes or None.
        """
        count = await self.read_int()
        if count == 0:
            return None
        buf = await self.reader.readexactly(count)
        return buf

    async def read_uuid(self) -> UUID:
        """Read a UUID.

        Returns:
            UUID: The UUID.
        """
        buf = await self.reader.readexactly(16)
        return UUID(bytes_le=buf)

    async def read_int_set(self) -> Optional[Set[int]]:
        """Read a set of ints

        Returns:
            Optional[Set[int]]: The set of ints or None.
        """
        count = await self.read_int()
        if count == 0:
            return None
        data = set()
        for _ in range(count):
            value = await self.read_int()
            data.add(value)
        return data

    async def read_data_packet(self) -> DataPacket:
        """Read a data packet

        Returns:
            DataPacket: The data packet.
        """
        entitlements = await self.read_int_set()
        data = await self.read_byte_array()
        return DataPacket(entitlements, data)

    async def read_data_packet_array(self) -> Optional[List[DataPacket]]:
        """Read an array of data packets.

        Returns:
            Optional[List[DataPacket]]: The data packets or None.
        """
        count = await self.read_int()
        if count == 0:
            return None
        packets: List[DataPacket] = list()
        for _ in range(count):
            packet = await self.read_data_packet()
            packets.append(packet)
        return packets
