"""Utilities"""

from asyncio import Event, Future, create_task, wait, FIRST_COMPLETED
from typing import AsyncIterator, Set, Callable, Awaitable, TypeVar

# pylint: disable=invalid-name
T = TypeVar('T')

async def read_aiter(
        read: Callable[[], Awaitable[None]],
        write: Callable[[], Awaitable[None]],
        dequeue: Callable[[], Awaitable[T]],
        cancellation_event: Event
) -> AsyncIterator[T]:
    """Creates an async iterator from an action."""

    cancellation_task = create_task(cancellation_event.wait())
    read_task = create_task(read())
    write_task = create_task(write())
    dequeue_task = create_task(dequeue())

    pending: Set[Future] = set()
    pending.add(cancellation_task)
    pending.add(read_task)
    pending.add(write_task)
    pending.add(dequeue_task)

    while not cancellation_event.is_set():
        done, pending = await wait(pending, return_when=FIRST_COMPLETED)
        for task in done:
            if task == cancellation_task:
                break
            elif task == read_task:
                read_task = create_task(read())
                pending.add(read_task)
            elif task == write_task:
                write_task = create_task(write())
                pending.add(write_task)
            elif task == dequeue_task:
                yield task.result()
                dequeue_task = create_task(dequeue())
                pending.add(dequeue_task)


    for task in pending:
        task.cancel()
        await task
