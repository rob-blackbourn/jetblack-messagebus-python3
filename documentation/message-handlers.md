# Message handlers

There are three types of messages that can be received:

- Data
- Subscription notifications
- Authorization requests.

## Data

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

## Subscription notifications

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

## Authorization requests

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
