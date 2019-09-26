"""Simple Subscriber"""

import asyncio

from aioconsole import ainput, aprint

from jetblack_messagebus import CallbackClient, DataPacket

async def main():
    await aprint('Example publisher')
    feed = await ainput('Feed: ')
    topic = await ainput('Topic: ')

    client = await CallbackClient.create('localhost', 9001)

    console_task = asyncio.create_task(ainput('Message: '))
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
                message = console_task.result()
                if not message:
                    client.stop()
                else:
                    print(f'Publishing to feed "{feed}" and topic "{topic}" the message "{message}"')
                    data_packets = [DataPacket({ 42 }, message.encode('utf8'))]
                    await client.publish(feed, topic, True, data_packets)
                    console_task = asyncio.create_task(ainput('Message: '))
                    pending.add(console_task)

if __name__ == '__main__':
    asyncio.run(main())
