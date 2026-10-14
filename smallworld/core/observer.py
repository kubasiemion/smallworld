from __future__ import annotations

from abc import ABC, abstractmethod

from .tape import Tape


class Observer(ABC):
    """The experimenter. The only component that sees truth and agent internals."""

    @abstractmethod
    def end_round(self, round: int, tape: Tape) -> dict:
        """Compute this round's measures."""
