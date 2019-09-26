"""Authenticated Subscriber"""

import asyncio
import ssl
from typing import Optional, List

from aioconsole import ainput
from jetblack_messagebus import CallbackClient, DataPacket, BasicAuthenticator

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

    print("authenticated subscriber")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tomsPassword", roles=Subscribe')
    print('  username="dick", password="dicksPassword", roles=Subscribe')
    print('  username="harry", password="harrysPassword", roles=Notify|Publish')
    print('  username="mary", password="marysPassword", roles=Authorize')
    username = input('Username: ')
    password = input('Password: ')

    feed = input('Feed: ')
    topic = input('Topic: ')

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    authenticator = BasicAuthenticator(username, password)
    client = await CallbackClient.create('localhost', 9001, ssl=ssl_context, authenticator=authenticator)

    print(f"Subscribing on feed '{feed}' to topic '{topic}'")
    client.data_handlers.append(on_data)
    await client.add_subscription(feed, topic)

    print('Starting the client')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
