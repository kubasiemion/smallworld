from __future__ import annotations

from math import log2

from smallworld.core.tape import Tape
from smallworld.core.types import Dispute, Truth

from .zk_observer import ZkObserver


class LawObserver(ZkObserver):
    """ZkObserver plus per-fact measures for agents that report `held()`.

    For every (agent, fact) the agent holds: right if the held class contains
    the fact's value in the agent's frame. `knowledge` is log2 of the held
    modulus over log2 of the agent's resolution, averaged over (agent, fact):
    0 = knows nothing, 1 = knows the fact at full resolution.
    `dissidents`: agents that sent at least one Dispute this round.
    `silent_wrong_facts`: wrong held facts at agents that sent no Dispute.
    """

    def end_round(self, round: int, tape: Tape) -> dict:
        m = super().end_round(round, tape)
        facts, dissidents, disputes = {}, set(), 0
        for _, e in tape.events(round):
            if isinstance(e, Truth):
                facts = e.facts
            elif isinstance(e, Dispute):
                disputes += 1
                dissidents.add(e.src)
        held = right = silent_wrong = 0
        knowledge, pairs = 0.0, 0
        for i, a in self.agents.items():
            beliefs = a.held()
            res = self._res(i)
            th = self._theta(i)
            for f, truth in facts.items():
                pairs += 1
                if f not in beliefs or beliefs[f][1] <= 1:
                    continue
                v, n = beliefs[f]
                held += 1
                knowledge += log2(n) / log2(res) if res > 1 else 0.0
                if (v - (truth + th)) % n == 0:
                    right += 1
                elif i not in dissidents:
                    silent_wrong += 1
        m.update({
            "fact_coverage": held / max(1, pairs),
            "fact_right": right / max(1, held),
            "knowledge": knowledge / max(1, pairs),
            "dissidents": len(dissidents),
            "disputes": disputes,
            "silent_wrong_facts": silent_wrong,
        })
        return m
