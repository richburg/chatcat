from asyncio import StreamWriter
from dataclasses import dataclass
from typing import Optional


@dataclass
class Client:
    nickname: str
    writer: StreamWriter
    admin: bool = False

    async def close(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()


class ClientManager:
    def __init__(self) -> None:
        self.clients: dict[StreamWriter, Client] = {}

    def add(self, client: Client) -> None:
        self.clients[client.writer] = client

    def get(self, writer: StreamWriter) -> Optional[Client]:
        return self.clients.get(writer)

    def get_by_nickname(self, nickname: str) -> Optional[Client]:
        return next(
            (client for client in self.clients.values() if client.nickname == nickname),
            None,
        )

    def remove(self, writer: StreamWriter) -> Optional[Client]:
        return self.clients.pop(writer, None)


registry = ClientManager()
