import asyncio

from server import bans
from server.entities.client import registry
from server.entities.message import Message
from server.helpers.decorators import require_adminship, require_args, require_identity
from server.helpers.utility import broadcast_message, get_ip, write


@require_args(n=2)
@require_identity()
@require_adminship()
async def handle_ban(writer: asyncio.StreamWriter, message: Message):
    target_nick = message.args[0]
    reason = message.args[1]
    target_client = registry.get_by_nickname(target_nick)

    if not target_client:
        await write(f"CLIENT_UNKNOWN|{target_nick}", writer)
        return

    if target_client.admin:
        await write(f"CLIENT_PROTECTED|{target_nick}", writer)
        return

    ip = get_ip(writer)
    bans.add(ip)

    await target_client.close()
    await write(f"BAN_SUCCESS|{ip}", writer)
    await broadcast_message(f"CLIENT_BANNED|{target_nick}|{reason}")


@require_args(n=1)
@require_identity()
@require_adminship()
async def handle_unban(writer: asyncio.StreamWriter, message: Message):
    target_ip = message.args[0]

    if target_ip not in bans:
        await write(f"UNKNOWN_BANNED_IP|{target_ip}", writer)
        return

    bans.remove(target_ip)
    await write(f"UNBAN_SUCCESS|{target_ip}", writer)


@require_args(n=1)
@require_identity()
@require_adminship()
async def handle_kick(writer: asyncio.StreamWriter, message: Message):
    target_nick = message.args[0]
    target_client = registry.get_by_nickname(target_nick)

    if not target_client:
        await write(f"CLIENT_UNKNOWN|{target_nick}", writer)
        return

    if target_client.admin:
        await write(f"CLIENT_PROTECTED|{target_nick}", writer)
        return

    await target_client.close()
    await write(f"KICK_SUCCESS|{target_nick}", writer)
