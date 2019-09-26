"""Simple Subscriber"""

import asyncio
from typing import Optional, List
from uuid import UUID

from jetblack_messagebus import Client, DataPacket

class SimpleSubscriber(Client):
    """A simple subscriber"""

    async def on_authorization(
            self,
            client_id: UUID,
            host: str,
            user: str,
            feed: str,
            topic: str
    ) -> None:
        print(f'authorization: client={client_id}, host="{host}", user="{user}", feed="{feed}"",topic="{topic}"')

    async def on_data(
            self,
            user: str,
            host: str,
            feed: str,
            topic: str,
            data_packets: Optional[List[DataPacket]],
            is_image: bool
    ) -> None:
        print(f'data: user="{user}",host="{host}",feed="{feed}",topic="{topic}"')
        if not data_packets:
            print("no data - closing")
            self.stop()
        else:
            for packet in data_packets:
                message = packet.data.decode('utf8') if packet.data else None
                print(f'received: entitlements={packet.entitlements},message={message}')

    async def on_forwarded_subscription_request(
            self,
            client_id: UUID,
            user: str,
            host: str,
            feed: str,
            topic: str,
            is_add: bool
    ) -> None:
        print(f'notification: client_id={client_id},user={user},host={host}, feed={feed},topic={topic},is_add={is_add}')

    async def on_closed(self, is_faulted):
        print(f'closed: is_faulted={is_faulted}')

async def main():
    client = await SimpleSubscriber.create('localhost', 9001)
    await client.add_subscription('TEST', 'FOO')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
