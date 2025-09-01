from asyncio import StreamWriter
from dataclasses import dataclass


@dataclass
class Message:
    type: str
    args: list[str]

    def has_exact_args(self, count: int) -> bool:
        return len(self.args) == count


@dataclass
class Client:
    nickname: str
    writer: StreamWriter
    admin: bool = False

    async def close(self) -> None:
        self.writer.close()
        await self.writer.wait_closed()
