from __future__ import annotations

import random

from smallworld.core.world import World


class LawWorld(World):
    """Facts a and b uniform on ℤ_k each round; c = a − b. The law holds in
    the world without exception."""

    def __init__(self, k: int, rng: random.Random, a: str = "x", b: str = "y", c: str = "z") -> None:
        self.k = k
        self.rng = rng
        self.a, self.b, self.c = a, b, c

    def draw(self, round: int) -> dict[str, int]:
        va, vb = self.rng.randrange(self.k), self.rng.randrange(self.k)
        return {self.a: va, self.b: vb, self.c: (va - vb) % self.k}
