from __future__ import annotations

from abc import ABC, abstractmethod

from .types import AgentId


class Disclosure(ABC):
    """Decides which agent sees which facts."""

    @abstractmethod
    def visible(self, agent: AgentId, group: str, facts: dict[str, int]) -> dict[str, int]:
        """Return the subset of facts this agent sees this round."""
