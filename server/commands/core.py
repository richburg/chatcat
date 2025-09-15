import logging
from asyncio import StreamWriter

from server.config import ADMIN_IPS
from server.entities.client import Client, registry
from server.entities.message import Message
from server.helpers.decorators import require_args, require_identity
from server.helpers.utility import (
    broadcast_message,
    get_ip,
    is_valid_nickname,
    write,
)


@require_args(n=1)
async def handle_identify(writer: StreamWriter, message: Message):
    if registry.get(writer):
        await write("IDENTITY_ALREADY_SET", writer)
        return

    nickname: str = message.args[0]

    if not is_valid_nickname(nickname):
        await write(f"IDENTITY_INVALID|{nickname}", writer)
        return

    if registry.get_by_nickname(nickname):
        await write(f"IDENTITY_TAKEN|{nickname}", writer)
        return

    ip = get_ip(writer)
    registry.add(Client(nickname, writer, admin=True if ip in ADMIN_IPS else False))

    logging.info(f"{ip} identified as {registry.get(writer)}")
    await broadcast_message(f"CLIENT_JOIN|{nickname}")


@require_args(n=1)
@require_identity()
async def handle_message(writer: StreamWriter, message: Message):
    content: str = message.args[0]
    nickname: str = registry.get(writer).nickname  # type: ignore
    await broadcast_message(f"INCOMING_MESSAGE|{nickname}|{content}")


@require_args(n=2)
@require_identity()
async def handle_whisper(writer: StreamWriter, message: Message):
    target_nickname: str = message.args[0]
    target_client = registry.get_by_nickname(target_nickname)

    if not target_client:
        await write(f"CLIENT_UNKNOWN|{target_nickname}", writer)
        return

    sender = registry.get(writer).nickname  # type: ignore
    content = message.args[1]

    await write(f"INCOMING_WHISPER|{sender}|{content}", target_client.writer)
    await write("WHISPER_SUCCESS", writer)


@require_identity()
async def handle_list(writer: StreamWriter, _):
    nicknames = (client.nickname for client in registry.clients.values())
    client_list = " ".join(nicknames)
    await write(f"INCOMING_CLIENT_LIST|{client_list}", writer)
