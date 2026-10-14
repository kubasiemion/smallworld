from __future__ import annotations

from smallworld.core.task import Task


class Identity(Task):
    """The target is one fact, read as is. For propagation experiments."""

    def __init__(self, a: str = "z") -> None:
        self.a = a
        self.operands = (a,)

    def combine(self, values: dict[str, int], modulus: int) -> int:
        return values[self.a] % modulus
