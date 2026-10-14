from __future__ import annotations

import random
from typing import Optional

from smallworld.core.repair import RepairPolicy


class NamedRepair(RepairPolicy):
    """The correction carries the discrepancy δ: it says where, not only that."""

    def message(self, delta: int) -> Optional[int]:
        return delta

    def update_receiver(self, g: int, sent: Optional[int], k: int) -> int:
        return (g + sent) % k

    def update_sender(self, g: int, sent: Optional[int], k: int) -> int:
        return (g - sent) % k


class BareRepair(RepairPolicy):
    """The correction says only "wrong". Each side re-guesses its translation."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng

    def message(self, delta: int) -> Optional[int]:
        return None

    def update_receiver(self, g: int, sent: Optional[int], k: int) -> int:
        return self.rng.randrange(k)

    def update_sender(self, g: int, sent: Optional[int], k: int) -> int:
        return self.rng.randrange(k)
