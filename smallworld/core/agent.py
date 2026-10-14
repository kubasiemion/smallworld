from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .factor import Factor
from .types import AgentId


@dataclass(frozen=True)
class Outgoing:
    kind: str
    value: int
    precision: int


@dataclass(frozen=True)
class Verdict:
    """Result of receiving a message: accepted, or a fire with its discrepancy."""

    fired: bool
    cause: str = ""
    delta: Optional[int] = None
    path_other: Optional[AgentId] = None  # set when a path check was made
    object: bool = True  # a fire may be logged without sending an objection
    gained: bool = False  # the receiver learned something it did not hold


class Agent(ABC):
    """A finite head on the tape.

    An agent sees only its own readings and the messages addressed to it. It
    holds its own translation table (its W′ of each neighbour). It never holds a
    reference to the World, the Observer, the Tape, or another agent.
    """

    id: AgentId
    group: str
    factor: "Factor"  # held privately; the Observer may inspect it, peers may not

    @abstractmethod
    def begin_round(self, round: int, facts_seen: dict[str, int]) -> None:
        """Receive this round's facts (raw); read them through the factor."""

    @abstractmethod
    def compose(self, dst: AgentId) -> list[Outgoing]:
        """What to write to `dst` now, in this agent's own frame."""

    @abstractmethod
    def receive(self, src: AgentId, out: Outgoing) -> Verdict:
        """Translate, continue, and run the watchdog."""

    @abstractmethod
    def apply_objection(self, peer: AgentId, sent: Optional[int], as_objector: bool) -> None:
        """Update the translation for `peer` after an objection on that edge,
        either as the objecting listener or as the writer objected to."""

    @abstractmethod
    def estimate(self) -> tuple[Optional[int], int]:
        """Task estimate in this agent's ℤ_resolution, or None if not computable."""

    @abstractmethod
    def translation(self, peer: AgentId) -> int:
        """For the Observer only: this agent's current g for messages from `peer`."""
