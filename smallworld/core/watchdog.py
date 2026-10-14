from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class Watchdog(ABC):
    """Decides whether to check a continuation, and whether it is admissible.

    Default-accept: returning None means accept, whether because no check was
    made or because the check passed.
    """

    horizon: int

    @abstractmethod
    def check_reading(self, own: int, received: int, own_res: int, precision: int) -> Optional[int]:
        """Compare a received, translated value against the agent's own reading
        of the same fact. Return the discrepancy (own − received) at the
        comparison modulus, or None to accept."""

    @abstractmethod
    def check_path(self, held: int, received: int, own_res: int, precision: int) -> Optional[int]:
        """Compare a value already held from another path with a newly received
        one. Return the discrepancy (held − received), or None to accept."""
