from asyncio import StreamWriter

from server.types import Client

clients: dict[StreamWriter, Client] = {}
bans: set[str] = set()
