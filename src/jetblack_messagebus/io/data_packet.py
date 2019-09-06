"""DataPacket"""

from typing import Optional, Set


class DataPacket:
    """A data packet"""

    def __init__(self, entitlements: Optional[Set[int]], data: Optional[bytes]) -> None:
        self.entitlements = entitlements
        self.data = data
