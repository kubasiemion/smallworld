"""Plain immutable records. Everything that goes on the tape is one of these."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

AgentId = int


@dataclass(frozen=True)
class Event:
    """Base for tape entries. `seq` is assigned by the Tape on append."""

    round: int

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = type(self).__name__
        return d


@dataclass(frozen=True)
class Truth(Event):
    """Facts and task value for a round. Observer-only."""

    facts: dict = field(default_factory=dict)
    target: int = 0


@dataclass(frozen=True)
class Message(Event):
    """A write. `value` is in the sender's frame, at the sender's resolution.

    `precision` is the sender's resolution, sent as an honest tag (DESIGN §3).
    `parents` are the tape seq ids this write depends on (the DAG).
    """

    src: AgentId = -1
    dst: AgentId = -1
    kind: str = ""
    value: int = 0
    precision: int = 0
    parents: tuple = ()


@dataclass(frozen=True)
class Arm(Event):
    """Writer arms a watchdog on its write."""

    writer: AgentId = -1
    on: int = -1  # seq of the Message


@dataclass(frozen=True)
class Fire(Event):
    """A watchdog found a continuation inadmissible."""

    checker: AgentId = -1
    src: AgentId = -1
    kind: str = ""
    cause: str = ""  # "reading" (own reading disagrees) or "path" (two paths disagree)
    delta: Optional[int] = None
    on: int = -1


@dataclass(frozen=True)
class Check(Event):
    """A path check: `checker` compared values of `kind` received from `a` and `b`.
    Logged whether or not it fired; this is what fills a triangle."""

    checker: AgentId = -1
    a: AgentId = -1
    b: AgentId = -1
    kind: str = ""


@dataclass(frozen=True)
class Objection(Event):
    """Listener-initiated repair: the receiver of a message objects to it,
    because it contradicts the receiver's own reading or a held belief.
    `delta` is None for a bare objection.

    Not to be confused with a Correction (not yet implemented), which comes
    from the original writer after seeing the listener's continuation:
    message -> continuation -> correction.
    """

    src: AgentId = -1  # the objecting listener
    dst: AgentId = -1  # the writer objected to
    delta: Optional[int] = None
    on: int = -1  # seq of the Fire


@dataclass(frozen=True)
class Expire(Event):
    """A watchdog's horizon passed without firing."""

    writer: AgentId = -1
    on: int = -1


@dataclass(frozen=True)
class Estimate(Event):
    """An agent's answer to the task at the end of a round, in ℤ_modulus."""

    agent: AgentId = -1
    value: Optional[int] = None
    modulus: int = 0
