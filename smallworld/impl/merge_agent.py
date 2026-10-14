from __future__ import annotations

from math import gcd
from typing import Optional

from smallworld.core.agent import Agent, Outgoing, Verdict
from smallworld.core.factor import Factor
from smallworld.core.repair import RepairPolicy
from smallworld.core.task import Task
from smallworld.core.types import AgentId
from smallworld.core.watchdog import Watchdog


def crt(a: int, p: int, b: int, q: int) -> tuple[int, int]:
    """Combine x ≡ a (mod p) and x ≡ b (mod q), assumed compatible
    (a ≡ b mod gcd(p, q)). Returns (x, lcm(p, q))."""
    g = gcd(p, q)
    lcm = p // g * q
    # solve a + p*t ≡ b (mod q)  ->  (p/g) t ≡ (b-a)/g (mod q/g)
    qg = q // g
    t = ((b - a) // g * pow(p // g, -1, qg)) % qg if qg > 1 else 0
    return (a + p * t) % lcm, lcm


class MergeAgent(Agent):
    """Beliefs are congruence classes: (value, modulus), and the modulus is
    honest. This is the L19 control and the merge proposed after E5.

    - A reading is a class mod the agent's resolution m.
    - An incoming class (w mod n), translated by g, becomes (w + g mod n'),
      with n' = gcd(n, m): the agent can hold no more than its resolution.
    - It is merged with what is held by CRT when the two agree on their
      common modulus, giving a class mod lcm. Redundant paths now add
      information instead of only being checked.
    - When they disagree on the common modulus, that is a real conflict, not
      precision loss: the watchdog fires (cause "reading" if the held class
      contains the agent's own reading, else "path") and the held class is
      kept.
    - Messages carry the class with its true modulus as `precision`, so
      nothing is laundered.
    """

    def __init__(
        self,
        id: AgentId,
        group: str,
        factor: Factor,
        watchdog: Watchdog,
        repair: RepairPolicy,
        task: Task,
        k: int,
        neighbours: list[AgentId],
        initial_translation: int = 0,
        path_objections: bool = True,
    ) -> None:
        self.id = id
        self.group = group
        self.factor = factor
        self.watchdog = watchdog
        self.repair = repair
        self.task = task
        self.k = k
        self.path_objections = path_objections
        self.g: dict[AgentId, int] = {n: initial_translation % k for n in neighbours}
        self.readings: set[str] = set()
        self.beliefs: dict[str, tuple[int, int, AgentId]] = {}  # kind -> (value, modulus, last contributor)

    @property
    def res(self) -> int:
        return self.factor.resolution

    def begin_round(self, round: int, facts_seen: dict[str, int]) -> None:
        self.readings = set(facts_seen)
        self.beliefs = {f: (self.factor.read(v), self.res, self.id) for f, v in facts_seen.items()}

    def compose(self, dst: AgentId) -> list[Outgoing]:
        return [Outgoing(f, v, n) for f, (v, n, _) in self.beliefs.items() if n > 1]

    def receive(self, src: AgentId, out: Outgoing) -> Verdict:
        self.g.setdefault(src, 0)
        n = gcd(out.precision, self.res)
        if n <= 1:
            return Verdict(False)
        received = (out.value + self.g[src]) % n
        held = self.beliefs.get(out.kind)
        if held is None:
            self.beliefs[out.kind] = (received, n, src)
            return Verdict(False, gained=True)
        a, p, other = held
        common = gcd(p, n)
        compatible = (a - received) % common == 0
        if compatible:
            value, modulus = crt(a, p, received, n)
            self.beliefs[out.kind] = (value, modulus, src)
            return Verdict(False, path_other=other if other != self.id else None, gained=modulus > p)
        delta = self.watchdog.check_path(a, received, p, n)
        if delta is None:  # unchecked: default-accept, but nothing to merge
            return Verdict(False)
        cause = "reading" if out.kind in self.readings else "path"
        return Verdict(True, cause, delta,
                       path_other=other if other != self.id else None,
                       object=(cause == "reading" or self.path_objections))

    def apply_objection(self, peer: AgentId, sent: Optional[int], as_objector: bool) -> None:
        self.g.setdefault(peer, 0)
        if as_objector:
            self.g[peer] = self.repair.update_receiver(self.g[peer], sent, self.k)
        else:
            self.g[peer] = self.repair.update_sender(self.g[peer], sent, self.k)

    def estimate(self) -> tuple[Optional[int], int]:
        values, modulus = {}, 0
        for f in self.task.operands:
            if f not in self.beliefs:
                return None, self.res
            v, n, _ = self.beliefs[f]
            values[f] = v
            modulus = gcd(modulus, n)
        if modulus <= 1:
            return None, self.res
        return self.task.combine({f: v % modulus for f, v in values.items()}, modulus), modulus

    def translation(self, peer: AgentId) -> int:
        return self.g.get(peer, 0)
