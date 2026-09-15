from __future__ import annotations

from tqdm import tqdm


class TqdmProgressReporter:
    def __init__(self) -> None:
        self._bar: tqdm | None = None

    def start(self, total: int) -> None:
        self._bar = tqdm(
            total=total,
            unit="stage",
            dynamic_ncols=True,
        )

    def advance(self, message: str) -> None:
        if self._bar is None:
            return

        self._bar.set_description(message)
        self._bar.update(1)

    def finish(self) -> None:
        if self._bar is None:
            return

        self._bar.close()
        self._bar = None