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


class Flood(Scheduler):
    """An information wave. Sources are informed first. Each informed node,
    when its turn comes, informs every neighbour except the one that informed
    it; a neighbour not yet informed joins the frontier. Each node takes one
    turn per round. Already informed neighbours still receive, which is where
    two fronts meet and cross.

    `mode = "queue"` gives breadth-first waves; `"stack"` depth-first.
    `sources` defaults to every node (one wave from everywhere at once).
    Neighbours are visited in id order unless `shuffle` is set.
    """

    def __init__(self, sources: list[int] | None = None, mode: str = "queue",
                 shuffle: bool = False, rng: random.Random | None = None) -> None:
        if mode not in ("queue", "stack"):
            raise ValueError("mode must be 'queue' or 'stack'")
        self.sources = sources
        self.mode = mode
        self.shuffle = shuffle
        self.rng = rng

    def exchanges(self, round: int, edges: list[tuple[AgentId, AgentId]]) -> Iterator[tuple[AgentId, AgentId]]:
        nbrs: dict[int, list[int]] = {}
        for a, b in edges:
            nbrs.setdefault(a, []).append(b)
            nbrs.setdefault(b, []).append(a)
        for n in nbrs.values():
            n.sort()
        sources = sorted(nbrs) if self.sources is None else list(self.sources)
        informed_by: dict[int, int | None] = {s: None for s in sources}
        frontier = list(sources)
        while frontier:
            node = frontier.pop(0) if self.mode == "queue" else frontier.pop()
            order = list(nbrs.get(node, []))
            if self.shuffle and self.rng is not None:
                self.rng.shuffle(order)
            for nb in order:
                if nb == informed_by[node]:
                    continue
                yield node, nb
                if nb not in informed_by:
                    informed_by[nb] = node
                    frontier.append(nb)


class Fixed(Scheduler):
    """The same directed exchanges, in the same order, every round. `order` is
    a list of [src, dst] pairs; the topology is not consulted."""

    def __init__(self, order: list[list[int]]) -> None:
        self.order = [(a, b) for a, b in order]

    def exchanges(self, round: int, edges: list[tuple[AgentId, AgentId]]) -> Iterator[tuple[AgentId, AgentId]]:
        yield from self.order
