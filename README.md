# jetblack-messagebus-python3


## Overview

This is a Python 3.7+ client for the [jetblack-messagebus](https://github.com/rob-blackbourn/jetblack-messagebus).

It follows the publish-subscribe pattern, and includes support for "notification" of
a subscription by another client. This allows it to provide data on-demand.

See the server documentation for more detailed information.

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
    client = await CallbackClient.create('localhost', 9091)
    client.data_handlers.append(on_data)
    await client.add_subscription('TEST', 'FOO')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
```

## SSL

To create an SSL subscriber, pass in the ssl context.

```python
import ssl
from jetblack_messagebus import CallbackClient

...

async def main():
    """Start the demo"""
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    client = await CallbackClient.create('myhost.example.com', 9091, ssl=ssl_context)
    await client.add_subscription('TEST', 'FOO')
    await client.start()
```

## Authentication

The message bus currently supports the following authentication methods:

- Password File
- LDAP
- JWT

### Password File and LDAP

Both the password file and LDAP methods require a username and password. This
is provided by the basic authenticator.

```python
import ssl
from jetblack_messagebus import CallbackClient
from jetblack_messagebus.authentication import BasicAuthenticator

...

async def main():
    authenticator = BasicAuthenticator("john.doe@example.com", "pa$$word")
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    client = await CallbackClient.create(
        'myhost.example.com',
        9091,
        ssl=ssl_context,
        authenticator=authenticator
    )
    await client.add_subscription('TEST', 'FOO')
    await client.start()
```

### JWT

JWT authentication requires a valid token to be passed by the client. This
is provided by the token authenticator.

```python
import ssl
from jetblack_messagebus import CallbackClient
from jetblack_messagebus.authentication import TokenAuthenticator

...

async def main():
    authenticator = TokenAuthenticator(
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huLmRvZUBleGFtcGxlLmNvbSIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxNTE3MTgzNTAxfQ.wLSGBcNUT8r1DqQvaBrrGY4NHiiVOpoxrgeoPsSsJkY"
    )
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    client = await CallbackClient.create(
        'myhost.example.com',
        9091,
        ssl=ssl_context,
        authenticator=authenticator
    )
    await client.add_subscription('TEST', 'FOO')
    await client.start()
```

## Message handlers

There are three types of messages that can be received:

- Data
- Subscription notifications
- Authorization requests.

### Data

A data handler looks like this:

```python
# A data handler.
async def on_data(
        user: str,
        host: str,
        feed: str,
        topic: str,
        data_packets: Optional[List[DataPacket]],
        is_image: bool
) -> None:
    """Called when data is received"""
    pass

# Add the handler to the client.
client.data_handlers.append(on_data)
# Remove the handler
client.data_handlers.remove(on_data)
```

The data packets have two fields: `entitlements` and `data`.

The `entitlements` is a optional set of ints which express the entitlements that were
required for the data to have been received.

The `data` is an optional `bytes` holding the encoded data. What this represents
is agreed by the sender and receiver. For example it might be a simple string, some
JSON text, or a protocol buffer.

### Subscription notifications

A subscription notification handler looks like this:

```python
# A notification handler.
async def on_notification(
        client_id: UUID,
        user: str,
        host: str,
        feed: str,
        topic: str,
        is_add: bool
) -> None:
    """Called for a notification"""
    pass

# Add the handler to the client.
client.notification_handlers.append(on_notification)
# Remove the handler
client.notification_handlers.remove(on_notification)
```

### Authorization requests

```python
# An authorization handler.
async def on_authorization(
        client_id: UUID,
        host: str,
        user: str,
        feed: str,
        topic: str
) -> None:
    """Called when authorization is requested"""
    pass

# Add the handler to the client.
client._authorization_handlers.append(on_authorization)
# Remove the handler
client._authorization_handlers.remove(on_authorization)
```
