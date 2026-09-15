from __future__ import annotations

from pathlib import Path


class TkDesktopUi:
    def select_fhx_file(self) -> Path | None:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()

        try:
            selected = filedialog.askopenfilename(
                title="Select DeltaV FHX file",
                filetypes=[("DeltaV FHX files", "*.fhx"), ("All files", "*.*")],
            )
        finally:
            root.destroy()

        return Path(selected) if selected else None

    def show_success(self, title: str, message: str) -> None:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        try:
            messagebox.showinfo(title, message, parent=root)
        finally:
            root.destroy()

    def show_error(self, title: str, message: str) -> None:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()

        try:
            messagebox.showerror(title, message, parent=root)
        finally:
            root.destroy()
