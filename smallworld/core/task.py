from __future__ import annotations

from abc import ABC, abstractmethod


class Task(ABC):
    """The target as a function of facts.

    `combine` must be well defined on values that share one frame, i.e. it must
    be gauge-invariant per frame (LOG L4).
    """

    operands: tuple[str, ...]

    @abstractmethod
    def combine(self, values: dict[str, int], modulus: int) -> int:
        """Combine operand values (all in one frame) in ℤ_modulus."""

    def truth(self, facts: dict[str, int], k: int) -> int:
        return self.combine(facts, k)
