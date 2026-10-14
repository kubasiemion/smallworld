from __future__ import annotations

import random
from math import gcd
from typing import Optional

from smallworld.core.watchdog import Watchdog


class DefaultWatchdog(Watchdog):
    """Default-accept. Checks with probability `intensity`; compares at the gcd
    of the two resolutions, which is all the two parties can jointly resolve."""

    def __init__(self, rng: random.Random, intensity: float = 1.0, horizon: int = 1) -> None:
        self.rng = rng
        self.intensity = intensity
        self.horizon = horizon

    def _compare(self, a: int, b: int, own_res: int, precision: int) -> Optional[int]:
        if self.rng.random() >= self.intensity:
            return None
        n = gcd(own_res, precision)
        delta = (a - b) % n
        return delta or None

    def check_reading(self, own, received, own_res, precision):
        return self._compare(own, received, own_res, precision)

    def check_path(self, held, received, own_res, precision):
        return self._compare(held, received, own_res, precision)
