from __future__ import annotations

from abc import ABC, abstractmethod

from .types import AgentId


class Topology(ABC):
    """Who can talk to whom. Static, undirected."""

    @abstractmethod
    def edges(self, groups: dict[AgentId, str]) -> list[tuple[AgentId, AgentId]]:
        """Undirected edges (a, b) with a < b."""
