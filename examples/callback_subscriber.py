"""Callback Subscriber"""

import asyncio
from typing import Optional, List

from aioconsole import ainput, aprint
from jetblack_messagebus import CallbackClient, DataPacket

async def on_data(
        user: str,
        host: str,
        feed: str,
        topic: str,
        data_packets: Optional[List[DataPacket]],
        is_image: bool
) -> None:
    """Handle a data message"""
    print(f'data: user="{user}",host="{host}",feed="{feed}",topic="{topic}",is_image={is_image}')
    if not data_packets:
        print("no data")
    else:
        for packet in data_packets:
            message = packet.data.decode('utf8') if packet.data else None
            print(f'packet: entitlements={packet.entitlements},message={message}')

async def main():
    """Start the demo"""
    await aprint('Example subscriber')
    feed = await ainput('Feed: ')
    topic = await ainput('Topic: ')
    client = await CallbackClient.create('localhost', 9001)
    client.data_handlers.append(on_data)
    await aprint(f"Subscribing on feed '{feed}' to topic '{topic}'")
    await client.add_subscription(feed, topic)
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
