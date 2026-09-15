from __future__ import annotations

import re
from typing import Sequence

from fhx_tool.domain.models import AttributeRecord
from .common import iter_top_level_blocks


class AttributeParser:
    _attribute_header = re.compile(r'^\s*ATTRIBUTE_INSTANCE\s+NAME="([^"]+)"')

    def parse(
        self,
        lines: Sequence[str],
        object_pattern: re.Pattern[str],
        identity_key: str,
    ) -> list[AttributeRecord]:
        records: list[AttributeRecord] = []

        for header, body in iter_top_level_blocks(lines, object_pattern):
            object_name = self._extract_identity(header, identity_key)
            records.extend(self._parse_object_attributes(object_name, body))

        return records

    @staticmethod
    def _extract_identity(header: str, identity_key: str) -> str:
        match = re.search(rf'\b{re.escape(identity_key)}="([^"]+)"', header)
        return match.group(1) if match else ""

    def _parse_object_attributes(
        self,
        object_name: str,
        body: Sequence[str],
    ) -> list[AttributeRecord]:
        records: list[AttributeRecord] = []
        index = 0

        while index < len(body):
            match = self._attribute_header.match(body[index])
            if not match:
                index += 1
                continue

            attribute_name = match.group(1)
            attribute_indent = self._indent(body[index])
            index += 1

            while index < len(body) and "VALUE" not in body[index]:
                if body[index].strip() == "}" and self._indent(body[index]) <= attribute_indent:
                    break
                index += 1

            if index >= len(body) or "VALUE" not in body[index]:
                continue

            value_lines, index = self._read_value(body, index)
            records.append(
                AttributeRecord(
                    object_name=object_name,
                    attribute_name=attribute_name,
                    value=" ".join(value_lines).strip(),
                )
            )

        return records

    @staticmethod
    def _indent(line: str) -> int:
        return len(line) - len(line.lstrip())

    @staticmethod
    def _read_value(body: Sequence[str], start: int) -> tuple[list[str], int]:
        line = body[start]
        value_lines: list[str] = []

        if "{" in line and "}" in line and line.find("{") < line.rfind("}"):
            inner = line.split("{", 1)[1].rsplit("}", 1)[0].strip()
            if inner:
                value_lines.append(inner)
            return value_lines, start + 1

        depth = line.count("{") - line.count("}")
        started = "{" in line
        index = start + 1

        while index < len(body):
            current = body[index]

            if not started and "{" in current:
                started = True

            depth += current.count("{") - current.count("}")

            if started and depth <= 0:
                return value_lines, index + 1

            cleaned = current.strip()
            if cleaned and cleaned not in {"{", "}"}:
                value_lines.append(cleaned)

            index += 1

        return value_lines, index
