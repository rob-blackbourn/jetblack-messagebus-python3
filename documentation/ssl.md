# SSL

To create an SSL subscriber, pass in the ssl context.

```python
import ssl
from jetblack_messagebus import CallbackClient

...

async def main():
    """Start the demo"""
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    client = await CallbackClient.create('myhost.example.com', 9001, ssl=ssl_context)
    await client.add_subscription('TEST', 'FOO')
    await client.start()
```
