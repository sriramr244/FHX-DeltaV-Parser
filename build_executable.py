from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
ENTRY = SRC / "fhx_tool" / "__main__.py"


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller>=6.0"]
        )


def main() -> None:
    ensure_pyinstaller()
    from PyInstaller.__main__ import run

    run(
        [
            str(ENTRY),
            "--name=FHXParser",
            "--onefile",
            "--windowed",
            f"--paths={SRC}",
            "--clean",
            "--noconfirm",
            f"--distpath={ROOT / 'dist'}",
            f"--workpath={ROOT / 'build'}",
            f"--specpath={ROOT}",
        ]
    )


if __name__ == "__main__":
    main()
