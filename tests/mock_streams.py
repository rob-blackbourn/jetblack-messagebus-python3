"""Moks for streams"""

import asyncio
from typing import Optional, Any, Iterable, Dict

class MockTransport(asyncio.Transport):
    """A mock for asyncio.Transport"""

    def __init__(self, extra_info: Optional[Dict[str, Any]] = None) -> None:
        self.extra_info = extra_info or dict()
        self.protocol: Optional[asyncio.Protocol] = None

    def close(self):
        pass

    def is_closing(self) -> bool:
        return False

    def get_extra_info(self, name: str, default: Any = None) -> Any:
        return self.extra_info.get(name, default)

    def set_protocol(self, protocol: asyncio.Protocol) -> None:
        self.protocol = protocol

    def get_protocol(self) -> Optional[asyncio.Protocol]:
        return self.protocol

class MockStreamWriter:
    """A mock for asyncio.StreamWriter"""

    def __init__(
            self,
            can_write_eof: bool = False,
            transport: Optional[asyncio.Transport] = None,
            extra_info: Any = None,
            close_wait_time: float = 0.01
    ) -> None:
        self.buf = b''
        self._closing = False
        self._closed = False
        self._can_write_eof = can_write_eof
        self.transport = transport
        self._extra_info = extra_info
        self.close_wait_time = close_wait_time

    def can_write_eof(self) -> bool:
        """Return True if the underlying transport supports the write_eof() method, False otherwise."""
        return self._can_write_eof

    def write_eof(self) -> None:
        """Close the write end of the stream after the buffered write data is flushed."""

    def get_extra_info(self) -> Any:
        """Access optional transport information"""
        return self._extra_info

    def write(self, data: bytes) -> None:
        """Write data to the stream."""
        self.buf += data

    def writelines(self, data: Iterable[bytes]) -> None:
        for datum in data:
            self.buf += datum

    async def drain(self) -> None:
        """Wait until it is appropriate to resume writing to the stream"""

    def close(self):
        """Close the stream."""
        self._closing = True

    def is_closing(self) -> bool:
        """Return True if the stream is closed or in the process of being closed."""
        return self._closing
    
    async def wait_closed(self):
        """Wait until the stream is closed."""
        await asyncio.sleep(self.close_wait_time)
        self._closed = True

class MockStreamReader:
    """A Mock for asyncio.StreamReader"""

    def __init__(self, buf: bytes)->None:
        self.buf = buf
        self.offset = 0

    async def read(self, n: int = -1) -> bytes:
        """Read up to n bytes. If n is not provided, or set to -1, read until EOF and return all read bytes."""
        if self.at_eof():
            raise EOFError()

        if n == -1:
            data = self.buf[self.offset:]
            self.offset = len(self.buf)
        else:
            start = self.offset
            self.offset += n
            data = self.buf[start:self.offset]

        return data

    async def readline(self) -> bytes:
        """Read one line, where “line” is a sequence of bytes ending with \n."""
        if self.at_eof():
            raise EOFError()

        start = self.offset
        for c in self.buf[start:]:
            self.offset += 1
            if c == b'\n':
                break

        return self.buf[start: self.offset]

    async def readexactly(self, n: int) -> bytes:
        """Read exactly n bytes."""
        if self.at_eof():
            raise EOFError()

        start = self.offset
        self.offset += n
        if self.offset > len(self.buf):
            raise asyncio.IncompleteReadError(self.buf[start:], n)
        return self.buf[start:self.offset]

    def at_eof(self) -> bool:
        """Return True if the buffer is empty and feed_eof() was called."""
        return self.offset >= len(self.buf)

    
