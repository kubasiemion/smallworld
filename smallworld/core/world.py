from __future__ import annotations

from abc import ABC, abstractmethod


class World(ABC):
    """Draws the facts for a round and holds the truth. Seen only by the Observer."""

    k: int

    @abstractmethod
    def draw(self, round: int) -> dict[str, int]:
        """Return {fact name: value in ℤ_k} for this round."""
