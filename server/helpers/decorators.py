from asyncio import StreamWriter
from typing import Callable

from server.helpers.utils import write
from server.types import Message
from server.variables import clients


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
            if writer not in clients:
                await write("IDENTITY_UNSET", writer)
                return

            return await handler(writer, message)

        return wrapper

    return decorator


def require_adminship():
    def decorator(handler: Callable):
        async def wrapper(writer: StreamWriter, message: Message):
            if not clients[writer].admin:
                await write("UNAUTHORIZED", writer)
                return

            return await handler(writer, message)

        return wrapper

    return decorator
