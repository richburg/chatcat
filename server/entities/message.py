from dataclasses import dataclass


@dataclass
class Message:
    type: str
    args: list[str]

    def has_exact_args(self, count: int) -> bool:
        return len(self.args) == count
