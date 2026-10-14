"""The append-only tape. The only shared state. Deliberately not polymorphic."""
from __future__ import annotations

import json
from typing import Iterable

from .types import Event


class Tape:
    def __init__(self) -> None:
        self._events: list[Event] = []

    def append(self, event: Event) -> int:
        """Append and return the event's sequence id."""
        self._events.append(event)
        return len(self._events) - 1

    def __len__(self) -> int:
        return len(self._events)

    def events(self, round: int | None = None) -> Iterable[tuple[int, Event]]:
        for seq, e in enumerate(self._events):
            if round is None or e.round == round:
                yield seq, e

    def dump(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for seq, e in enumerate(self._events):
                d = e.to_dict()
                d["seq"] = seq
                f.write(json.dumps(d) + "\n")
