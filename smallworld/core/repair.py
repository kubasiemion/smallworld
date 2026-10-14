from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class RepairPolicy(ABC):
    """What a repair carries, and how each side updates its translation.

    Currently applied to Objections only (listener-initiated). Corrections
    from the original writer will use the same policy.
    """

    @abstractmethod
    def message(self, delta: int) -> Optional[int]:
        """What goes on the tape: the discrepancy (named) or None (bare)."""

    @abstractmethod
    def update_receiver(self, g: int, sent: Optional[int], k: int) -> int:
        """New translation held by the objector for messages from the writer."""

    @abstractmethod
    def update_sender(self, g: int, sent: Optional[int], k: int) -> int:
        """New translation held by the writer for messages from the objector."""
