"""Authenticated authorizer"""

import asyncio
import ssl
from typing import Optional, Set
from uuid import UUID

from jetblack_messagebus import CallbackClient, BasicAuthenticator


class Authorizer(CallbackClient):
    """Create a subsclass to gain access to the authorize method"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.authorization_handlers.append(self.on_authorization)

    async def on_authorization(
            self,
            client_id: UUID,
            host: str,
            user: str,
            feed: str,
            topic: str
    ) -> None:
        """Called when authorization is requested"""

        print(
            f'on_authorization: client_id={client_id},host={host},user={user},feed={feed},topic={topic}')

        entitlements: Optional[Set[int]] = None

        if user == "tom":
            entitlements = {1, 2}
            await self.authorize(client_id, feed, topic, True, entitlements)
        elif user == "dick":
            entitlements = {1}
            await self.authorize(client_id, feed, topic, True, {1})

        print(f'{user} can see {entitlements}')
        await self.authorize(client_id, feed, topic, True, entitlements)


async def main():
    """Start the demo"""

    print("authenticated authorizer")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tomsPassword", roles=Subscribe')
    print('  username="dick", password="dicksPassword", roles=Subscribe')
    print('  username="harry", password="harrysPassword", roles=Notify|Publish')
    print('  username="mary", password="marysPassword", roles=Authorize')
    username = input('Username: ')
    password = input('Password: ')
    authenticator = BasicAuthenticator(username, password)

    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    client = await Authorizer.create('localhost', 9001, ssl=ssl_context, authenticator=authenticator)

    print('Starting the authenticator')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
