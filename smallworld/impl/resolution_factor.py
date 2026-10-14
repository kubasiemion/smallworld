from __future__ import annotations

from smallworld.core.factor import Factor


class ResolutionFactor(Factor):
    """Gauge θ ∈ ℤ_k and resolution m dividing k.

    read(v)  = (v + θ) mod m
    embed    = (value + shift) mod m, taking the received value as an exact
               integer. This is the overconfident lift: a coarse value from a
               sender becomes a full-precision value here, and nothing remembers
               that it was coarse (W-core §7: complete inside the factor).
    """

    def __init__(self, k: int, resolution: int, gauge: int) -> None:
        if k % resolution:
            raise ValueError(f"resolution {resolution} must divide k={k}")
        self.k = k
        self.resolution = resolution
        self._gauge = gauge % k

    def read(self, value: int) -> int:
        return (value + self._gauge) % self.resolution

    def embed(self, value: int, precision: int, shift: int) -> int:
        return (value + shift) % self.resolution

    def ground_truth_gauge(self) -> int:
        return self._gauge
