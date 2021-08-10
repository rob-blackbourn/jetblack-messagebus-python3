"""DataPacket"""

from typing import Optional, Set


class DataPacket:
    """A data packet"""

    def __init__(
            self,
            entitlements: Optional[Set[int]],
            data: Optional[bytes]
    ) -> None:
        """Initialise a data packet.

        Args:
            entitlements (Optional[Set[int]]): An optional set of entitlements.
            data (Optional[bytes]): The data.
        """
        self.entitlements = entitlements
        self.data = data

    def __str__(self) -> str:
        return f'entitlements={self.entitlements},data={self.data!r}'

    def __repr__(self):
        return f'DataPacket({self.entitlements}, {self.data})'

    def __eq__(self, value):
        return (
            isinstance(value, DataPacket) and
            self.entitlements == value.entitlements and
            self.data == value.data
        )
