from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator

from .types import AgentId


class Scheduler(ABC):
    """Order of exchanges within a round. This is what shapes the event DAG."""

    @abstractmethod
    def exchanges(self, round: int, edges: list[tuple[AgentId, AgentId]]) -> Iterator[tuple[AgentId, AgentId]]:
        """Yield directed exchanges (src, dst)."""

    def delivered(self, src: AgentId, dst: AgentId, gained: bool, objected: bool) -> None:
        """Outcome of the exchange just yielded, as reported by dst itself:
        whether dst gained anything, and whether it objected. Called before
        the generator resumes. Schedulers that ignore outcomes need not
        override it."""
