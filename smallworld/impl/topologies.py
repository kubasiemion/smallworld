from __future__ import annotations

from smallworld.core.topology import Topology
from smallworld.core.types import AgentId


class Groups(Topology):
    """Dense within groups, plus explicit extra edges.

    Group names are read as sets of letters: "X" and "XY" share X, so a broker
    "XY" is dense with both sides. Group "H" (hub) is adjacent to everyone.
    `extra` lists additional edges, typically the cut.
    """

    def __init__(self, extra: list[list[int]] | None = None, dense: bool = True) -> None:
        self.extra = [tuple(sorted(e)) for e in (extra or [])]
        self.dense = dense

    def edges(self, groups: dict[AgentId, str]) -> list[tuple[AgentId, AgentId]]:
        ids = sorted(groups)
        es: set[tuple[int, int]] = set()
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                ga, gb = set(groups[a]), set(groups[b])
                if "H" in ga or "H" in gb or (self.dense and ga & gb):
                    es.add((a, b))
        es.update(self.extra)
        return sorted(es)
