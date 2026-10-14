from __future__ import annotations

from smallworld.core.disclosure import Disclosure
from smallworld.core.types import AgentId


class GroupDisclosure(Disclosure):
    """Facts are disclosed by group: `groups` maps a group name to its facts.

    Brokers are just a group whose list contains both operands; common ground is
    a fact listed for every group.
    """

    def __init__(self, groups: dict[str, list[str]]) -> None:
        self.groups = {g: list(fs) for g, fs in groups.items()}

    def visible(self, agent: AgentId, group: str, facts: dict[str, int]) -> dict[str, int]:
        return {f: facts[f] for f in self.groups.get(group, []) if f in facts}
