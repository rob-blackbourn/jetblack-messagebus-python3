"""Simple Subscriber"""

import asyncio
from typing import Optional, List
from uuid import UUID

from aioconsole import ainput

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
            print("no data")
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

async def main():
    client = await SimpleSubscriber.create('localhost', 9091)

    prompt = 'Enter feed and topic (e.g. LSE SBRY)\n'
    console_task = asyncio.create_task(ainput(prompt))
    pending = {
        asyncio.create_task(client.start()),
        console_task
    }

    while pending:

        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            if task == console_task:
                line = console_task.result()
                if not line:
                    client.stop()
                else:
                    feed, topic = line.split(' ')
                    print(f'Subscribing to feed "{feed}" and topic "{topic}"')
                    await client.add_subscription(feed, topic)
                    console_task = asyncio.create_task(ainput(prompt))
                    pending.add(console_task)

if __name__ == '__main__':
    asyncio.run(main())
