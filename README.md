# jetblack-messagebus-python3

A Python3 client for the [jetblack-messagebus](https://github.com/rob-blackbourn/jetblack-messagebus).

## Example

The client below subscribes on feed "TEST" to topic "FOO" and prints out 
the data it receives.

```python
import asyncio
from typing import Optional, List

from jetblack_messagebus import Client, DataPacket

class SimpleSubscriber(Client):
    """A simple subscriber"""

    async def on_authorization(self, client_id, host, user, feed, topic):
        print(f'authorization: client={client_id}, host="{host}", user="{user}", feed="{feed}"",topic="{topic}"')

    async def on_data(self, user, host, feed, topic, data_packets, is_image):
        print(f'data: user="{user}",host="{host}",feed="{feed}",topic="{topic}"')
        if not data_packets:
            print("no data")
        else:
            for packet in data_packets:
                message = packet.data.decode('utf8') if packet.data else None
                print(f'received: entitlements={packet.entitlements},message={message}')

    async def on_forwarded_subscription_request(self, client_id, user, host, feed, topic, is_add):
        print(f'notification: client_id={client_id},user={user},host={host}, feed={feed},topic={topic},is_add={is_add}')

async def main():
    client = await SimpleSubscriber.create('localhost', 9091)
    await client.add_subscription('TEST', 'FOO')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
```