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
    """An information wave. Sources are informed first. A node, on its turn,
    informs every neighbour except the one that told it this time. Already
    informed neighbours still receive, which is where two fronts meet and
    cross.

    `mode`: "queue" gives breadth-first waves, "stack" depth-first.
    `sources`: default every node (one wave from everywhere at once).

    `retell` decides who gets a turn after hearing something:
      "first"  - only on first being informed (one turn per node per round;
                 the original flood, and the default).
      "always" - after every delivery, unless damped by `stop_on`:
          "none"      - never damped; only the limits stop the wave.
          "agreement" - not if dst already held state and did not object
                        ("I already know about it").
          "no_gain"   - not if dst gained nothing ("nothing I can add").
        `retell_on_objection`: whether a delivery dst objected to gives dst
        a turn anyway (the conflict itself spreads). Applies under "always".

    Limits (None = off): `ttl` hops from a source; `max_turns` per node per
    round; `budget` exchanges per round. Under retell = "always" a budget of
    10000 applies if none is given, so an undamped wave terminates.

    Outcomes come from `delivered`, i.e. from dst's own report; the scheduler
    never looks inside an agent.
    """

    SAFETY_BUDGET = 10000

    def __init__(self, sources: list[int] | None = None, mode: str = "queue",
                 shuffle: bool = False, rng: random.Random | None = None,
                 retell: str = "first", stop_on: str = "none",
                 retell_on_objection: bool = True,
                 ttl: int | None = None, max_turns: int | None = None,
                 budget: int | None = None) -> None:
        if mode not in ("queue", "stack"):
            raise ValueError("mode must be 'queue' or 'stack'")
        if retell not in ("first", "always"):
            raise ValueError("retell must be 'first' or 'always'")
        if stop_on not in ("none", "agreement", "no_gain"):
            raise ValueError("stop_on must be 'none', 'agreement' or 'no_gain'")
        self.sources = sources
        self.mode = mode
        self.shuffle = shuffle
        self.rng = rng
        self.retell = retell
        self.stop_on = stop_on
        self.retell_on_objection = retell_on_objection
        self.ttl = ttl
        self.max_turns = max_turns
        self.budget = budget if budget is not None or retell == "first" else self.SAFETY_BUDGET
        self._outcome = (False, False)

    def delivered(self, src, dst, gained, objected):
        self._outcome = (gained, objected)

    def _retells(self, had_state: bool) -> bool:
        gained, objected = self._outcome
        if self.retell == "first":
            return not had_state
        if objected:
            return self.retell_on_objection
        if self.stop_on == "agreement":
            return not had_state
        if self.stop_on == "no_gain":
            return gained
        return True

    def exchanges(self, round: int, edges: list[tuple[AgentId, AgentId]]) -> Iterator[tuple[AgentId, AgentId]]:
        nbrs: dict[int, list[int]] = {}
        for a, b in edges:
            nbrs.setdefault(a, []).append(b)
            nbrs.setdefault(b, []).append(a)
        for n in nbrs.values():
            n.sort()
        sources = sorted(nbrs) if self.sources is None else list(self.sources)
        informed: set[int] = set(sources)
        turns: dict[int, int] = {}
        frontier: list[tuple[int, int | None, int]] = [(s, None, 0) for s in sources]
        used = 0
        while frontier:
            node, told_by, hops = frontier.pop(0) if self.mode == "queue" else frontier.pop()
            if self.max_turns is not None and turns.get(node, 0) >= self.max_turns:
                continue
            turns[node] = turns.get(node, 0) + 1
            order = list(nbrs.get(node, []))
            if self.shuffle and self.rng is not None:
                self.rng.shuffle(order)
            for nb in order:
                if nb == told_by:
                    continue
                if self.budget is not None and used >= self.budget:
                    return
                self._outcome = (False, False)
                yield node, nb
                used += 1
                had_state = nb in informed
                informed.add(nb)
                if self._retells(had_state) and (self.ttl is None or hops + 1 <= self.ttl):
                    frontier.append((nb, node, hops + 1))


class Fixed(Scheduler):
    """The same directed exchanges, in the same order, every round. `order` is
    a list of [src, dst] pairs; the topology is not consulted."""

    def __init__(self, order: list[list[int]]) -> None:
        self.order = [(a, b) for a, b in order]

    def exchanges(self, round: int, edges: list[tuple[AgentId, AgentId]]) -> Iterator[tuple[AgentId, AgentId]]:
        yield from self.order
