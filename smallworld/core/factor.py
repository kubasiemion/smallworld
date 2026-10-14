from __future__ import annotations

from abc import ABC, abstractmethod


class Factor(ABC):
    """How one agent reads the world and holds values. Private to its agent.

    An agent's values all live in ℤ_resolution, in the agent's own frame.
    """

    resolution: int

    @abstractmethod
    def read(self, value: int) -> int:
        """Turn a world value into the agent's representation."""

    @abstractmethod
    def embed(self, value: int, precision: int, shift: int) -> int:
        """Bring a received value (sender frame, sender precision) into this
        agent's representation, applying the translation `shift`.

        This is where finiteness bites: the result is a plain element of
        ℤ_resolution, with no record of how precise it really is.
        """

    @abstractmethod
    def ground_truth_gauge(self) -> int:
        """For the Observer only. Agents never call this on each other."""
