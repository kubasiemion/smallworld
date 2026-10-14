from __future__ import annotations

import random

from smallworld.core.world import World


class UniformZk(World):
    """Each fact uniform on ℤ_k, resampled every round."""

    def __init__(self, k: int, facts: list[str], rng: random.Random) -> None:
        self.k = k
        self.facts = list(facts)
        self.rng = rng

    def draw(self, round: int) -> dict[str, int]:
        return {f: self.rng.randrange(self.k) for f in self.facts}
