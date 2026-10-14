from __future__ import annotations

import random
from typing import Iterator

from smallworld.core.scheduler import Scheduler
from smallworld.core.types import AgentId


class RandomSweeps(Scheduler):
    """Each sweep visits every directed edge once, in random order."""

    def __init__(self, rng: random.Random, sweeps: int = 3) -> None:
        self.rng = rng
        self.sweeps = sweeps

    def exchanges(self, round: int, edges: list[tuple[AgentId, AgentId]]) -> Iterator[tuple[AgentId, AgentId]]:
        directed = [(a, b) for a, b in edges] + [(b, a) for a, b in edges]
        for _ in range(self.sweeps):
            order = directed[:]
            self.rng.shuffle(order)
            yield from order
