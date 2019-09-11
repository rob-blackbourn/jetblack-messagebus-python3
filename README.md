# jetblack-messagebus-python3

A Python3 client for the [jetblack-messagebus](https://github.com/rob-blackbourn/jetblack-messagebus).

## Example

The client below subscribes on feed "TEST" to topic "FOO" and prints out 
the data it receives.

```python
import asyncio

from jetblack_messagebus import CallbackClient

async def on_data(user, host, feed, topic, data_packets, is_image):
    print(f'data: user="{user}",host="{host}",feed="{feed}",topic="{topic}",is_image={is_image}')
    if not data_packets:
        print("no data")
    else:
        for packet in data_packets:
            message = packet.data.decode('utf8') if packet.data else None
            print(f'packet: entitlements={packet.entitlements},message={message}')

async def main():
    """Start the demo"""
    client = await CallbackClient.create('localhost', 9091)
    client.data_handlers.append(on_data)
    await client.add_subscription('TEST', 'FOO')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
```