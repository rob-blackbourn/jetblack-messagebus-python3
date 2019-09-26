"""DataPacket"""

from typing import Optional, Set


class DataPacket:
    """A data packet"""

    def __init__(self, entitlements: Optional[Set[int]], data: Optional[bytes]) -> None:
        self.entitlements = entitlements
        self.data = data

    def __str__(self) -> str:
        return f'entitlements={self.entitlements},data={self.data}'

    def __repr__(self):
        return f'DataPacket({self.entitlements}, {self.data})'
