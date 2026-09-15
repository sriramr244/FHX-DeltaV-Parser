from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from .common import first_quoted_values, iter_top_level_blocks


@dataclass(frozen=True, slots=True)
class ObjectParseSpec:
    header_pattern: re.Pattern[str]
    header_value_count: int
    output_filename: str
    fields: Sequence[str]


class ObjectParser:
    def parse(self, lines: Sequence[str], spec: ObjectParseSpec) -> list[list[str]]:
        rows: list[list[str]] = [list(spec.fields)]

        for header, body in iter_top_level_blocks(lines, spec.header_pattern):
            row = [""] * len(spec.fields)
            header_values = first_quoted_values(header, spec.header_value_count)

            for index, value in enumerate(header_values):
                if index < len(row):
                    row[index] = value

            field_indexes = {name: index for index, name in enumerate(spec.fields)}
            depth = 0

            for body_line in body:
                if depth == 1:
                    stripped = body_line.strip()
                    for field_name, field_index in field_indexes.items():
                        prefix = f"{field_name}="
                        if stripped.startswith(prefix):
                            row[field_index] = stripped[len(prefix):].strip().strip('"')
                            break

                depth += body_line.count("{") - body_line.count("}")

            rows.append(row)

        return rows
