from __future__ import annotations

from pathlib import Path


class FhxReadError(RuntimeError):
    pass


class FhxReader:
    _ENCODINGS = ("utf-16", "utf-16-le")

    def read_lines(self, file_path: Path) -> list[str]:
        path = Path(file_path)

        if not path.is_file():
            raise FhxReadError(f"FHX file does not exist: {path}")

        last_decode_error: UnicodeError | None = None

        for encoding in self._ENCODINGS:
            try:
                with path.open("r", encoding=encoding) as handle:
                    return [line.rstrip("\r\n") for line in handle]
            except UnicodeError as exc:
                last_decode_error = exc
            except OSError as exc:
                raise FhxReadError(f"Could not read FHX file: {path}") from exc

        raise FhxReadError(
            f"Could not decode {path.name} using supported FHX encodings."
        ) from last_decode_error
