from __future__ import annotations

import re
from collections.abc import Sequence

from fhx_tool.config.fhx_schema import HEADER_PATTERNS
from fhx_tool.domain.models import CompositeCatalog
from fhx_tool.parsers.common import (
    iter_top_level_blocks,
    quoted_assignments,
)


class CompositeParser:
    _function_block = re.compile(
        r'^\s*FUNCTION_BLOCK\s+'
        r'NAME="([^"]+)"\s+'
        r'DEFINITION="([^"]+)"'
    )

    _wire = re.compile(
        r'^\s*WIRE\s+'
        r'SOURCE="([^"]+)"\s+'
        r'DESTINATION="([^"]+)"'
    )

    def parse(
        self,
        lines: Sequence[str],
    ) -> CompositeCatalog:
        catalog = CompositeCatalog()

        for header, body in iter_top_level_blocks(
            lines,
            HEADER_PATTERNS[
                "function_block_definition"
            ],
        ):
            definition = quoted_assignments(header).get(
                "NAME",
                "",
            )

            if not definition:
                continue

            self._parse_definition(
                catalog,
                definition,
                body,
            )

        return catalog

    def _parse_definition(
        self,
        catalog: CompositeCatalog,
        definition: str,
        body: Sequence[str],
    ) -> None:
        blocks = catalog.blocks.setdefault(definition, {})
        aliases = catalog.aliases.setdefault(definition, {})

        for line in body:
            block_match = self._function_block.match(line)

            if block_match:
                blocks[block_match.group(1)] = (
                    block_match.group(2)
                )
                continue

            wire_match = self._wire.match(line)

            if wire_match:
                self._record_alias(
                    aliases,
                    wire_match.group(1),
                    wire_match.group(2),
                )

    def _record_alias(
        self,
        aliases: dict[str, str],
        source: str,
        destination: str,
    ) -> None:
        if "/" in source and "/" not in destination:
            aliases.setdefault(source, destination)
        elif "/" in destination and "/" not in source:
            aliases.setdefault(destination, source)