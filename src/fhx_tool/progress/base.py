from __future__ import annotations

from typing import Protocol


class ProgressReporter(Protocol):
    def start(self, total: int) -> None:
        ...

    def advance(self, message: str) -> None:
        ...

    def finish(self) -> None:
        ...