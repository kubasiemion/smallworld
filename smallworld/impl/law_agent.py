from __future__ import annotations

from dataclasses import replace
from math import gcd

from smallworld.core.agent import Outgoing, Verdict
from smallworld.core.types import AgentId

from .merge_agent import MergeAgent, crt


def prime_powers(n: int) -> list[int]:
    """The maximal prime powers dividing n."""
    out, p = [], 2
    while p * p <= n:
        if n % p == 0:
            q = 1
            while n % p == 0:
                n //= p
                q *= p
            out.append(q)
        p += 1
    if n > 1:
        out.append(n)
    return out


def strip(n: int, suspended: set[int]) -> int:
    """n with every prime of the suspended prime powers divided out."""
    for q in suspended:
        g = gcd(n, q)
        while g > 1:
            n //= g
            g = gcd(n, q)
    return n


class LawAgent(MergeAgent):
    """MergeAgent that also holds a law, c = a − b, which it never revises.

    After every arrival it applies the law prime power by prime power q of
    its own resolution:
      - two of a, b, c known mod q: the third is derived and merged in;
      - all three known mod q and c ≢ a − b, or an arrival contradicting a
        residue the agent derived from the law: the law is violated. The agent
        cannot tell which fact is wrong, so it suspends judgment: q is
        dropped from every fact involved that is not its own reading, and
        stays dropped for the rest of the round (so the closure terminates).
        It reports a Dispute, mod q, to everyone who contributed to those
        facts this round. A bare report: that, not where.
    Own readings are observations and are never suspended. The law is
    frame-bound (its coefficients do not sum to 0), so it holds in an agent's
    frame only with gauge 0 (LOG L37).
    """

    def __init__(self, id, group, factor, watchdog, repair, task, k, neighbours,
                 initial_translation: int = 0, path_objections: bool = True,
                 law: dict | None = None) -> None:
        # explicit signature: the runner injects components by parameter name
        super().__init__(id, group, factor, watchdog, repair, task, k, neighbours,
                         initial_translation=initial_translation, path_objections=path_objections)
        law = law or {"a": "x", "b": "y", "c": "z"}
        self.la, self.lb, self.lc = law["a"], law["b"], law["c"]
        self.contributors: dict[str, set[AgentId]] = {}
        self.suspended: dict[str, set[int]] = {}
        self.derived: dict[str, set[int]] = {}
        self.disputes_received = 0

    def begin_round(self, round: int, facts_seen: dict[str, int]) -> None:
        super().begin_round(round, facts_seen)
        self.contributors = {f: set() for f in (self.la, self.lb, self.lc)}
        self.suspended = {f: set() for f in (self.la, self.lb, self.lc)}
        self.derived = {f: set() for f in (self.la, self.lb, self.lc)}
        self._close()  # a source seeing two facts derives the third at once

    def receive(self, src: AgentId, out: Outgoing) -> Verdict:
        if out.kind not in self.contributors:
            return super().receive(src, out)
        if self.suspended[out.kind]:
            out = Outgoing(out.kind, out.value, strip(out.precision, self.suspended[out.kind]))
        # An arrival that contradicts a *derived* residue is a law violation,
        # not a path conflict: the derived value is the law speaking. Handle
        # it here (suspend, dispute) and strip that prime from the arrival,
        # so the merge below never sees it as a conflict to object to.
        disputes: list[tuple[AgentId, int]] = []
        changed = False
        self.g.setdefault(src, 0)
        n_in = gcd(out.precision, self.res)
        held = self.beliefs.get(out.kind)
        if held is not None and n_in > 1:
            received = (out.value + self.g[src]) % n_in
            for q in list(self.derived[out.kind]):
                if n_in % q == 0 and held[1] % q == 0 and (held[0] - received) % q:
                    disputes += self._violate(q, extra={out.kind: src})
                    out = Outgoing(out.kind, out.value, strip(out.precision, {q}))
                    changed = True
        verdict = super().receive(src, out)
        if not verdict.fired and gcd(out.precision, self.res) > 1:
            self.contributors[out.kind].add(src)
        closed, more = self._close()
        for d in more:
            if d not in disputes:
                disputes.append(d)
        return replace(verdict, gained=verdict.gained or changed or closed, disputes=tuple(disputes))

    def _violate(self, q: int, extra: dict | None = None) -> list[tuple[AgentId, int]]:
        """Suspend judgment on q for every fact of the law that is not an own
        reading, and return the Dispute targets: everyone who contributed to
        those facts this round (plus `extra`, a contributor not yet recorded)."""
        targets: list[tuple[AgentId, int]] = []
        for f in (self.la, self.lb, self.lc):
            if f in self.readings:
                continue
            held = self.beliefs.get(f)
            if held is not None and held[1] % q == 0:
                v, n, who = held
                self.beliefs[f] = (v % (n // q), n // q, who)
            self.suspended[f].add(q)
            self.derived[f].discard(q)
            suppliers = set(self.contributors[f])
            if extra and f in extra:
                suppliers.add(extra[f])
            for s in sorted(suppliers):
                if s != self.id and (s, q) not in targets:
                    targets.append((s, q))
        return targets

    def _class(self, f: str):
        b = self.beliefs.get(f)
        return None if b is None else (b[0], b[1])

    def _close(self) -> tuple[bool, list[tuple[AgentId, int]]]:
        changed, disputes = False, []
        for q in prime_powers(self.res):
            known = {}
            for f in (self.la, self.lb, self.lc):
                c = self._class(f)
                if c is not None and c[1] % q == 0 and q not in self.suspended[f]:
                    known[f] = c[0] % q
            if len(known) == 3:
                if (known[self.lc] - (known[self.la] - known[self.lb])) % q:
                    for d in self._violate(q):
                        if d not in disputes:
                            disputes.append(d)
                    changed = True
            elif len(known) == 2:
                missing = next(f for f in (self.la, self.lb, self.lc) if f not in known)
                if q in self.suspended[missing]:
                    continue
                if missing == self.lc:
                    r = (known[self.la] - known[self.lb]) % q
                elif missing == self.la:
                    r = (known[self.lc] + known[self.lb]) % q
                else:
                    r = (known[self.la] - known[self.lc]) % q
                held = self.beliefs.get(missing)
                if held is None:
                    self.beliefs[missing] = (r, q, self.id)
                else:
                    v, n, who = held
                    if n % q == 0:
                        continue
                    v, n = crt(v, n, r, q)
                    self.beliefs[missing] = (v, n, who)
                self.derived[missing].add(q)
                changed = True
        return changed, disputes

    def receive_dispute(self, src: AgentId, prime: int) -> None:
        self.disputes_received += 1

    def held(self) -> dict:
        return {f: (v, n) for f, (v, n, _) in self.beliefs.items()}
