from asyncio import StreamWriter
from typing import Callable

from server.entities.client import registry
from server.entities.message import Message
from server.helpers.utility import write


def require_args(n: int):
    def decorator(handler: Callable):
        async def wrapper(writer: StreamWriter, message: Message):
            if not message.has_exact_args(n):
                return

            return await handler(writer, message)

        return wrapper

    return decorator


def require_identity():
    def decorator(handler: Callable):
        async def wrapper(writer: StreamWriter, message: Message):
            if not registry.get(writer):
                await write("IDENTITY_UNSET", writer)
                return

            return await handler(writer, message)

        return wrapper

    return decorator


def require_adminship():
    def decorator(handler: Callable):
        async def wrapper(writer: StreamWriter, message: Message):
            if not registry.get(writer).admin:
                await write("UNAUTHORIZED", writer)
                return

            return await handler(writer, message)

        return wrapper

    return decorator
