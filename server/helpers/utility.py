import asyncio
import re
from typing import Optional

from server.entities.client import registry
from server.entities.message import Message


async def convert_to_message(data: bytes) -> Optional[Message]:
    message: str = data.decode().strip()
    if not message:
        return None

    parts: list[str] = message.split("|")
    if not parts:
        return None

    type: str = parts[0].upper()
    args: list[str] = parts[1:] if len(parts) >= 2 else []

    return Message(type=type, args=args)


async def write(message: str, writer: asyncio.StreamWriter) -> None:
    writer.write((message + "\n").encode())
    await writer.drain()


async def broadcast_message(message: str) -> None:
    await asyncio.gather(*(write(message, client) for client in registry.clients))


def get_ip(writer: asyncio.StreamWriter) -> str:
    return writer.get_extra_info("peername")[0]


def is_valid_nickname(nickname: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]+", nickname))
