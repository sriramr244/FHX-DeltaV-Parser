from __future__ import annotations


class NullProgressReporter:
    def start(self, total: int) -> None:
        pass

    def advance(self, message: str) -> None:
        pass

    def finish(self) -> None:
        pass