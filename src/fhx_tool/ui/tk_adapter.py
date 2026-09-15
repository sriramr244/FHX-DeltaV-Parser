from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox


class TkDesktopUi:
    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.withdraw()

    @property
    def root(self) -> tk.Tk:
        return self._root

    def select_fhx_file(self) -> Path | None:
        selected = filedialog.askopenfilename(
            parent=self._root,
            title="Select DeltaV FHX file",
            filetypes=[
                ("DeltaV FHX files", "*.fhx"),
                ("All files", "*.*"),
            ],
        )

        return Path(selected) if selected else None

    def show_success(self, title: str, message: str) -> None:
        messagebox.showinfo(
            title,
            message,
            parent=self._root,
        )

    def show_error(self, title: str, message: str) -> None:
        messagebox.showerror(
            title,
            message,
            parent=self._root,
        )

    def close(self) -> None:
        self._root.destroy()