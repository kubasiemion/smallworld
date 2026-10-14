from __future__ import annotations

from typing import Optional

from smallworld.core.agent import Agent, Outgoing, Verdict
from smallworld.core.factor import Factor
from smallworld.core.repair import RepairPolicy
from smallworld.core.task import Task
from smallworld.core.types import AgentId
from smallworld.core.watchdog import Watchdog


class RelayAgent(Agent):
    """Reads what it is shown, relays what it holds, checks what it can.

    Own readings are checked against incoming values of the same fact. For
    facts it does not see, it keeps the first value received this round (the
    ratchet: first come holds) and path-checks later arrivals against it.
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
        path_repairs: bool = True,
    ) -> None:
        """`path_repairs`: whether a path-check fire sends a repair. The agent
        cannot tell a translation error from a precision loss upstream, so a
        path repair may move the wrong variable."""
        self.path_repairs = path_repairs
        self.id = id
        self.group = group
        self.factor = factor
        self.watchdog = watchdog
        self.repair = repair
        self.task = task
        self.k = k
        self.g: dict[AgentId, int] = {n: initial_translation % k for n in neighbours}
        self.readings: dict[str, int] = {}
        self.beliefs: dict[str, tuple[int, AgentId]] = {}

    @property
    def res(self) -> int:
        return self.factor.resolution

    def begin_round(self, round: int, facts_seen: dict[str, int]) -> None:
        self.readings = {f: self.factor.read(v) for f, v in facts_seen.items()}
        self.beliefs = {}

    def compose(self, dst: AgentId) -> list[Outgoing]:
        out = [Outgoing(f, v, self.res) for f, v in self.readings.items()]
        for f, (v, src) in self.beliefs.items():
            if f not in self.readings and src != dst:
                out.append(Outgoing(f, v, self.res))
        return out

    def receive(self, src: AgentId, out: Outgoing) -> Verdict:
        received = self.factor.embed(out.value, out.precision, self.g[src])
        if out.kind in self.readings:
            delta = self.watchdog.check_reading(self.readings[out.kind], received, self.res, out.precision)
            return Verdict(True, "reading", delta) if delta is not None else Verdict(False)
        held = self.beliefs.get(out.kind)
        if held is None or held[1] == src:
            self.beliefs[out.kind] = (received, src)
            return Verdict(False)
        delta = self.watchdog.check_path(held[0], received, self.res, out.precision)
        if delta is not None:
            return Verdict(True, "path", delta, path_other=held[1], repair=self.path_repairs)
        return Verdict(False, path_other=held[1])

    def corrected(self, peer: AgentId, sent: Optional[int], as_checker: bool) -> None:
        if as_checker:
            self.g[peer] = self.repair.update_receiver(self.g[peer], sent, self.k)
        else:
            self.g[peer] = self.repair.update_sender(self.g[peer], sent, self.k)

    def estimate(self) -> tuple[Optional[int], int]:
        values = {}
        for f in self.task.operands:
            if f in self.readings:
                values[f] = self.readings[f]
            elif f in self.beliefs:
                values[f] = self.beliefs[f][0]
            else:
                return None, self.res
        return self.task.combine(values, self.res), self.res

    def translation(self, peer: AgentId) -> int:
        return self.g[peer]
