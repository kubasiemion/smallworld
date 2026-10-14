from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class RepairPolicy(ABC):
    """What a fired watchdog sends, and how each side updates its translation."""

    @abstractmethod
    def message(self, delta: int) -> Optional[int]:
        """What goes on the tape: the discrepancy (named) or None (bare)."""

    @abstractmethod
    def update_receiver(self, g: int, sent: Optional[int], k: int) -> int:
        """New translation held by the checker for messages from the corrected peer."""

    @abstractmethod
    def update_sender(self, g: int, sent: Optional[int], k: int) -> int:
        """New translation held by the corrected peer for messages from the checker."""
