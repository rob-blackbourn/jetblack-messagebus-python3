"""Notification Subscriber"""

import asyncio
import ssl
from uuid import UUID

from aioconsole import ainput, aprint

from jetblack_messagebus import CallbackClient, BasicAuthenticator

async def on_notification(
        client_id: UUID,
        user: str,
        host: str,
        feed: str,
        topic: str,
        is_add: bool
) -> None:
    """Handle a notification"""
    print(f"on_notification: client_id={client_id},user='{user}',host='{host}',feed='{feed}'',topic='{topic}'',is_add={is_add}")

async def main():
    """Start the demo"""
    print("authenticted notifier")

    print('Enter a username and password.')
    print('Known users are:')
    print('  username="tom", password="tomsPassword", roles=Subscribe')
    print('  username="dick", password="dicksPassword", roles=Subscribe')
    print('  username="harry", password="harrysPassword", roles=Notify|Publish')
    print('  username="mary", password="marysPassword", roles=Authorize')

    username = input('Username: ')
    password = input('Password: ')
    feed = input('Feed: ')

    authenticator = BasicAuthenticator(username, password)
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    client = await CallbackClient.create('localhost', 9091, ssl=ssl_context, authenticator=authenticator)

    print(f"Requesting notification of subscriptions on feed '{feed}'")
    client.notification_handlers.append(on_notification)
    await client.add_notification(feed)

    print('Starting the client')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
