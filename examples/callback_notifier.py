"""Notification Subscriber"""

import asyncio
from uuid import UUID

from jetblack_messagebus import CallbackClient

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
    client = await CallbackClient.create('localhost', 9091)
    client.notification_handlers.append(on_notification)
    print("Requesting notification of subscriptions on feed 'TEST'")
    await client.add_notification('TEST')
    await client.start()

if __name__ == '__main__':
    asyncio.run(main())
