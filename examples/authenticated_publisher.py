"""Simple Subscriber"""

import asyncio
import ssl
from typing import Set, Tuple, Optional, List

from aioconsole import ainput, aprint

from jetblack_messagebus import CallbackClient, DataPacket, BasicAuthenticator

async def read_console() -> List[DataPacket]:
    """Read the data packets"""
    await aprint('Enter an empty message finish the data packet. Entitlements can be empty')
    await aprint('or a comma separated list of ints, e.g.: 1, 2, 3')
    data_packets: List[DataPacket] = list()
    while True:
        message = await ainput('Message: ')
        if not message:
            break
        line = await ainput('Entitlements: ')
        entitlements = None if not line else {int(item.strip()) for item in line.split(',')}
        data_packets.append(DataPacket(entitlements, message.encode('utf8')))
    return data_packets

async def main():
    print("authenticated publisher")

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

    print('starting the client')
    console_task = asyncio.create_task(read_console())
    client_task = asyncio.create_task(client.start())
    pending = {
        client_task,
        console_task
    }

    while pending:

        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        for task in done:
            if task == client_task:
                break
            elif task == console_task:
                data_packets = console_task.result()
                if not data_packets:
                    client.stop()
                else:
                    print(f'Publishing to feed "{feed}" and topic "{topic}" the data packets "{data_packets}"')
                    await client.publish(feed, topic, True, data_packets)
                    console_task = asyncio.create_task(read_console())
                    pending.add(console_task)

if __name__ == '__main__':
    asyncio.run(main())
