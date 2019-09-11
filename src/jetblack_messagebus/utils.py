"""Utilities"""

from asyncio import Event, Future, create_task, wait, FIRST_COMPLETED
from typing import AsyncIterator, Set, Callable, Awaitable, TypeVar

# pylint: disable=invalid-name
T = TypeVar('T')

async def read_aiter(
        read: Callable[[], Awaitable[T]],
        cancellation_event: Event
) -> AsyncIterator[T]:
    """Creates an async iterator from an action."""

    cancellation_task = create_task(cancellation_event.wait())
    read_task = create_task(read())

    pending: Set[Future] = set()
    pending.add(cancellation_task)
    pending.add(read_task)

    while not cancellation_event.is_set():
        done, pending = await wait(pending, return_when=FIRST_COMPLETED)
        for task in done:
            if task == cancellation_task:
                continue

            yield task.result()

            read_task = create_task(read())
            pending.add(read_task)

    for task in pending:
        task.cancel()
        await task
