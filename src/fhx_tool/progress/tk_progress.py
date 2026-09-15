from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class TkProgressReporter:
    def __init__(self, root: tk.Misc) -> None:
        self._root = root
        self._window: tk.Toplevel | None = None
        self._progress_bar: ttk.Progressbar | None = None
        self._status_var = tk.StringVar(master=root, value="")
        self._detail_var = tk.StringVar(master=root, value="")
        self._total = 0
        self._current = 0

    def start(self, total: int) -> None:
        self._total = total
        self._current = 0

        window = tk.Toplevel(self._root)
        window.title("FHX Parser")
        window.resizable(False, False)
        window.protocol("WM_DELETE_WINDOW", lambda: None)

        container = ttk.Frame(window, padding=24)
        container.grid(row=0, column=0, sticky="nsew")

        title = ttk.Label(
            container,
            text="Processing FHX",
            font=("TkDefaultFont", 14, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        status = ttk.Label(
            container,
            textvariable=self._status_var,
        )
        status.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(16, 8),
        )

        progress_bar = ttk.Progressbar(
            container,
            orient="horizontal",
            mode="determinate",
            maximum=total,
            length=420,
        )
        progress_bar.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        detail = ttk.Label(
            container,
            textvariable=self._detail_var,
        )
        detail.grid(
            row=3,
            column=0,
            sticky="e",
            pady=(8, 0),
        )

        self._window = window
        self._progress_bar = progress_bar

        self._status_var.set("Starting...")
        self._detail_var.set(f"0 of {total}")

        window.update_idletasks()

        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        window.geometry(f"+{x}+{y}")
        window.lift()
        window.focus_force()

        self._refresh()

    def advance(self, message: str) -> None:
        if self._window is None or self._progress_bar is None:
            return

        self._current = min(self._current + 1, self._total)

        self._status_var.set(message)
        self._detail_var.set(
            f"{self._current} of {self._total}  "
            f"({self._percentage()}%)"
        )

        self._progress_bar["value"] = self._current

        self._refresh()

    def finish(self) -> None:
        if self._window is None:
            return

        if self._progress_bar is not None:
            self._progress_bar["value"] = self._total

        self._status_var.set("Complete")
        self._detail_var.set(
            f"{self._total} of {self._total}  (100%)"
        )

        self._refresh()

        self._window.destroy()
        self._window = None
        self._progress_bar = None

    def _percentage(self) -> int:
        if self._total == 0:
            return 0

        return round((self._current / self._total) * 100)

    def _refresh(self) -> None:
        if self._window is None:
            return

        self._window.update_idletasks()
        self._window.update()