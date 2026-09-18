from __future__ import annotations

import re
from collections.abc import Iterable, Iterator

from fhx_tool.config.fhx_schema import PATH_SEPARATORS


_QUOTED_ASSIGNMENT = re.compile(r'\b([A-Z0-9_]+)="([^"]*)"')


def quoted_assignments(line: str) -> dict[str, str]:
    return dict(_QUOTED_ASSIGNMENT.findall(line))


def first_quoted_values(line: str, count: int) -> list[str]:
    return re.findall(r'="([^"]*)"', line)[:count]


def canonical_path(path: str) -> str:
    normalized = path.strip()

    for separator in PATH_SEPARATORS:
        normalized = normalized.replace(separator, "/")

    while normalized.startswith("^/"):
        normalized = normalized[2:]

    return normalized.lstrip("/")


def leaf_name(path: str) -> str:
    parts = [part for part in path.strip("/").split("/") if part]
    return parts[-1] if parts else ""


def af_path(plant_area: str, module_name: str) -> str:
    parts = [part for part in plant_area.strip("/").split("/") if part]
    if module_name:
        parts.append(module_name)
    return "\\".join(parts)


def iter_top_level_blocks(
    lines: Iterable[str],
    header_pattern: re.Pattern[str],
) -> Iterator[tuple[str, list[str]]]:
    line_iter = iter(lines)

    for line in line_iter:
        if not header_pattern.match(line):
            continue

        body: list[str] = []
        depth = line.count("{") - line.count("}")
        started = depth > 0

        for next_line in line_iter:
            if not started and "{" in next_line:
                started = True

            depth += next_line.count("{") - next_line.count("}")
            body.append(next_line)

            if started and depth == 0:
                break

        yield line, body