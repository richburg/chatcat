import logging
from asyncio import StreamWriter

from server.config import ADMIN_IPS
from server.helpers.decorators import require_args, require_identity
from server.helpers.utils import (
    broadcast_message,
    find_client,
    get_ip,
    is_nickname_taken,
    is_valid_nickname,
    write,
)
from server.types import Client, Message
from server.variables import clients


@require_args(n=1)
async def handle_identify(writer: StreamWriter, message: Message):
    if writer in clients:
        await write("IDENTITY_ALREADY_SET", writer)
        return

    nickname: str = message.args[0]

    if not is_valid_nickname(nickname):
        await write(f"IDENTITY_INVALID|{nickname}", writer)
        return

    if is_nickname_taken(nickname):
        await write(f"IDENTITY_TAKEN|{nickname}", writer)
        return

    ip = get_ip(writer)
    clients[writer] = Client(nickname, writer, admin=True if ip in ADMIN_IPS else False)

    logging.debug(f"{ip} {clients[writer]}")
    await broadcast_message(f"CLIENT_JOIN|{nickname}")


@require_args(n=1)
@require_identity()
async def handle_message(writer: StreamWriter, message: Message):
    content: str = message.args[0]
    nickname: str = clients[writer].nickname
    await broadcast_message(f"INCOMING_MESSAGE|{nickname}|{content}")


@require_args(n=2)
@require_identity()
async def handle_whisper(writer: StreamWriter, message: Message):
    target_nickname: str = message.args[0]
    target_client = find_client(target_nickname)

    if not target_client:
        await write(f"CLIENT_UNKNOWN|{target_nickname}", writer)
        return

    sender = clients[writer].nickname
    content = message.args[1]

    await write(f"INCOMING_WHISPER|{sender}|{content}", target_client.writer)
    await write("WHISPER_SUCCESS", writer)


@require_identity()
async def handle_list(writer: StreamWriter, _):
    nicknames = (client.nickname for client in clients.values())
    client_list = " ".join(nicknames)
    await write(f"INCOMING_CLIENT_LIST|{client_list}", writer)
