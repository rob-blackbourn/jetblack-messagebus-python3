# Authentication

The message bus currently supports the following authentication methods:

- Password File
- LDAP
- JWT

## Password File and LDAP

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
        9001,
        ssl=ssl_context,
        authenticator=authenticator
    )
    await client.add_subscription('TEST', 'FOO')
    await client.start()
```

## JWT

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
        9001,
        ssl=ssl_context,
        authenticator=authenticator
    )
    await client.add_subscription('TEST', 'FOO')
    await client.start()
```
