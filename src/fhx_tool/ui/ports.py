from __future__ import annotations

from pathlib import Path
from typing import Protocol


class DesktopUi(Protocol):
    def select_fhx_file(self) -> Path | None: ...

    def show_success(self, title: str, message: str) -> None: ...

    def show_error(self, title: str, message: str) -> None: ...
