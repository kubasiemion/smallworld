from __future__ import annotations

from smallworld.core.task import Task


class Difference(Task):
    """d = a − b. Gauge-invariant within one frame."""

    def __init__(self, a: str = "x", b: str = "y") -> None:
        self.a, self.b = a, b
        self.operands = (a, b)

    def combine(self, values: dict[str, int], modulus: int) -> int:
        return (values[self.a] - values[self.b]) % modulus
