from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from .types import AgentId


class Scheduler(ABC):
    """Order of exchanges within a round. This is what shapes the event DAG."""

    @abstractmethod
    def exchanges(self, round: int, edges: list[tuple[AgentId, AgentId]]) -> Iterator[tuple[AgentId, AgentId]]:
        """Yield directed exchanges (src, dst)."""
