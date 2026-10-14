from __future__ import annotations

from itertools import combinations
from math import gcd

import networkx as nx

from smallworld.core.agent import Agent
from smallworld.core.observer import Observer
from smallworld.core.tape import Tape
from smallworld.core.types import Check, Estimate, Fire, Message, Objection, Truth


class ZkObserver(Observer):
    """Measures for the ℤ_k model (DESIGN §5).

    Edge error e(i→j) = g_j[i] − (θ_j − θ_i) mod k: the error in j's translation
    of messages from i. It is "visible" if nonzero mod gcd(m_i, m_j), the most
    the two can jointly check, and "invisible" if zero there but nonzero mod k.
    Holonomy of a cycle is Σ e along it; for a correct table it is 0.
    """

    def __init__(self, agents: dict[int, Agent], edges: list[tuple[int, int]], k: int, cut: set[tuple[int, int]],
                 task=None) -> None:
        """With `task`, correctness is judged in each agent's own frame: the
        task evaluated on facts shifted by that agent's gauge. Without it, in
        the world's frame (the same thing for gauge-invariant tasks)."""
        self.task = task
        self.agents = agents
        self.edges = edges
        self.k = k
        self.cut = cut
        self.graph = nx.Graph(edges)
        self.cycles = nx.cycle_basis(self.graph)
        self.triangles = [t for t in combinations(sorted(self.graph.nodes), 3)
                          if all(self.graph.has_edge(a, b) for a, b in combinations(t, 2))]

    def _theta(self, i: int) -> int:
        return self.agents[i].factor.ground_truth_gauge()

    def _res(self, i: int) -> int:
        return self.agents[i].factor.resolution

    def edge_error(self, i: int, j: int) -> int:
        return (self.agents[j].translation(i) - (self._theta(j) - self._theta(i))) % self.k

    def holonomy(self, cycle: list[int]) -> int:
        return sum(self.edge_error(a, b) for a, b in zip(cycle, cycle[1:] + cycle[:1])) % self.k

    def _crosses_cut(self, cycle: list[int]) -> bool:
        return any(tuple(sorted(e)) in self.cut for e in zip(cycle, cycle[1:] + cycle[:1]))

    def end_round(self, round: int, tape: Tape) -> dict:
        truth = None
        facts = {}
        estimates: list[Estimate] = []
        fires = {"reading": 0, "path": 0}
        objections, objection_size = 0, 0
        filled: set[frozenset] = set()
        involved: set[int] = set()
        messages = 0
        for _, e in tape.events(round):
            if isinstance(e, Truth):
                truth = e.target
                facts = e.facts
            elif isinstance(e, Message):
                messages += 1
            elif isinstance(e, Estimate):
                estimates.append(e)
            elif isinstance(e, Fire):
                fires[e.cause] += 1
                involved.update((e.checker, e.src))
            elif isinstance(e, Objection):
                objections += 1
                if e.delta is not None:
                    objection_size += min(e.delta, self.k - e.delta)
            elif isinstance(e, Check):
                filled.add(frozenset((e.checker, e.a, e.b)))

        est = [e for e in estimates if e.value is not None]
        def frame_truth(agent: int) -> int:
            if self.task is None:
                return truth
            th = self._theta(agent)
            return self.task.combine({f: (v + th) % self.k for f, v in facts.items()}, self.k)

        correct = [((e.value - frame_truth(e.agent)) % e.modulus) == 0 for e in est]
        silent_wrong = sum(1 for e, c in zip(est, correct) if not c and e.agent not in involved)
        chance = sum(1 / e.modulus for e in est) / max(1, len(est))
        pairs = list(combinations(est, 2))
        agree = wrong_agree = 0
        for a, b in pairs:
            n = gcd(a.modulus, b.modulus)
            if (a.value - b.value) % n == 0:
                agree += 1
                if (a.value - truth) % n != 0:
                    wrong_agree += 1

        directed = self.edges + [(b, a) for a, b in self.edges]
        vis = invis = 0
        cut_err = 0
        for i, j in directed:
            e = self.edge_error(i, j)
            if e == 0:
                continue
            if e % gcd(self._res(i), self._res(j)):
                vis += 1
            else:
                invis += 1
            if tuple(sorted((i, j))) in self.cut:
                cut_err += 1

        hol_cut = hol_in = hol_invis = 0
        for c in self.cycles:
            h = self.holonomy(c)
            if h:
                if self._crosses_cut(c):
                    hol_cut += 1
                else:
                    hol_in += 1
                n = 0
                for a in c:
                    n = gcd(n, self._res(a))
                if h % n == 0:
                    hol_invis += 1

        tri_filled = tri_unfilled = 0
        for t in self.triangles:
            if self.holonomy(list(t)):
                if frozenset(t) in filled:
                    tri_filled += 1
                else:
                    tri_unfilled += 1

        return {
            "round": round,
            "coverage": len(est) / max(1, len(estimates)),
            "correct": sum(correct) / max(1, len(est)),
            "correct_chance": chance,
            "silent_wrong": silent_wrong / max(1, len(est)),
            "agree": agree / max(1, len(pairs)),
            "wrong_agree": wrong_agree / max(1, len(pairs)),
            "fires_reading": fires["reading"],
            "fires_path": fires["path"],
            "messages": messages,
            "objections": objections,
            "objection_size": objection_size / max(1, objections),
            "edge_err_visible": vis,
            "edge_err_invisible": invis,
            "cut_edge_err": cut_err,
            "holonomy_cut_cycles": hol_cut,
            "holonomy_inner_cycles": hol_in,
            "holonomy_invisible": hol_invis,
            "cycles": len(self.cycles),
            "holonomy_tri_filled": tri_filled,
            "holonomy_tri_unfilled": tri_unfilled,
            "triangles_filled": sum(1 for t in self.triangles if frozenset(t) in filled),
            "triangles": len(self.triangles),
        }
