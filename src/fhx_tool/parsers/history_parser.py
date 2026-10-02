from __future__ import annotations

import re
from dataclasses import replace
from typing import Sequence

from fhx_tool.domain.models import HistoryPoint
from .common import canonical_path, iter_top_level_blocks, leaf_name
from fhx_tool.services.module_resolver import ModuleResolver


class HistoryParser:
    _unit_header = re.compile(r'^BATCH_EQUIPMENT_UNIT_MODULE\s+NAME="([^"]+)"')
    _process_cell_header = re.compile(r'^PROCESS_CELL\s+NAME="([^"]+)"')
    _history_instance_header = re.compile(
        r'^\s*HISTORY_DATA_POINT_INSTANCE\s+NAME="([^"]+)"'
    )
    _history_point_header = re.compile(
        r'^\s*HISTORY_DATA_POINT\s+FIELD="([^"]+)"'
    )
    _property = re.compile(r'^\s*([A-Z0-9_]+)=(.*)$')
    _description = re.compile(r'^\s*DESCRIPTION="(.*)"\s*$')

    def parse(self, lines: Sequence[str]) -> list[HistoryPoint]:
        unit_modules = self._collect_names(lines, self._unit_header)
        process_cells = self._collect_names(lines, self._process_cell_header)
        points: list[HistoryPoint] = []

        for module in ModuleResolver().resolve(lines):
            body = module.effective_body
            module_name = module.module_name
            plant_area = module.plant_area
            module_class = module.module_class
            description = self._module_description(body)
            area_leaf = leaf_name(plant_area)
            unit_name = area_leaf if area_leaf in unit_modules else ""
            process_cell_name = area_leaf if area_leaf in process_cells else ""

            points.extend(
                self._parse_history_points(
                    body=body,
                    module_name=module_name,
                    description=description,
                    module_class=module_class,
                    plant_area=plant_area,
                    unit_name=unit_name,
                    process_cell_name=process_cell_name,
                )
            )

        return points

    @staticmethod
    def _collect_names(lines: Sequence[str], pattern: re.Pattern[str]) -> set[str]:
        return {
            match.group(1)
            for line in lines
            if (match := pattern.match(line)) is not None
        }

    def _module_description(self, body: Sequence[str]) -> str:
        depth = 0
        description = ""

        for line in body:
            if depth == 1:
                match = self._description.match(line)
                if match:
                    description = match.group(1)

            depth += line.count("{") - line.count("}")

        return description

    def _parse_history_points(
        self,
        *,
        body: Sequence[str],
        module_name: str,
        description: str,
        module_class: str,
        plant_area: str,
        unit_name: str,
        process_cell_name: str,
    ) -> list[HistoryPoint]:
        # The resolver orders class before instance. Merge partial overrides
        # by canonical instance path and field, retaining inherited properties.
        results: dict[str, HistoryPoint] = {}
        for header, instance_body in iter_top_level_blocks(body, self._history_instance_header):
            match = self._history_instance_header.match(header)
            assert match is not None
            history_instance = canonical_path(match.group(1))
            for point_header, point_body in iter_top_level_blocks(instance_body, self._history_point_header):
                point_match = self._history_point_header.match(point_header)
                assert point_match is not None
                field_name = point_match.group(1)
                properties, _ = self._history_properties(point_body, 0)
                history_tag = f"{module_name}/{history_instance}.{field_name}"
                key = history_tag.upper()
                if key in results:
                    previous = results[key]
                    results[key] = replace(previous, properties={**previous.properties, **properties})
                else:
                    results[key] = HistoryPoint(
                        history_tag=history_tag,
                        module_name=module_name,
                        module_description=description,
                        module_class=module_class,
                        plant_area=plant_area,
                        unit_module_name=unit_name,
                        process_cell_name=process_cell_name,
                        properties=properties,
                    )
        return list(results.values())

    def _history_properties(
        self,
        body: Sequence[str],
        start: int,
    ) -> tuple[dict[str, str], int]:
        properties: dict[str, str] = {}
        depth = 0
        started = False
        index = start

        while index < len(body):
            line = body[index]

            if "{" in line:
                started = True

            depth += line.count("{") - line.count("}")

            if started and depth <= 0:
                return properties, index + 1

            match = self._property.match(line)
            if match:
                properties[match.group(1)] = match.group(2).strip().strip('"')

            index += 1

        return properties, index
