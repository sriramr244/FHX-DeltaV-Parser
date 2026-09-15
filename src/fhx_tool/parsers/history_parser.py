from __future__ import annotations

import re
from typing import Sequence

from fhx_tool.domain.models import HistoryPoint
from .common import af_path, iter_top_level_blocks, leaf_name, quoted_assignments


class HistoryParser:
    _unit_header = re.compile(r'^BATCH_EQUIPMENT_UNIT_MODULE\s+NAME="([^"]+)"')
    _process_cell_header = re.compile(r'^PROCESS_CELL\s+NAME="([^"]+)"')
    _module_header = re.compile(r'^(MODULE_INSTANCE|MODULE)\s+TAG="([^"]+)"')
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

        for header, body in iter_top_level_blocks(lines, self._module_header):
            header_values = quoted_assignments(header)
            module_name = header_values.get("TAG", "")
            plant_area = header_values.get("PLANT_AREA", "")
            module_class = header_values.get("MODULE_CLASS", "")
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

        for line in body:
            if depth == 1:
                match = self._description.match(line)
                if match:
                    return match.group(1)

            depth += line.count("{") - line.count("}")

        return ""

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
        results: list[HistoryPoint] = []
        history_instance = ""
        index = 0

        while index < len(body):
            line = body[index]
            instance_match = self._history_instance_header.match(line)

            if instance_match:
                history_instance = instance_match.group(1)
                index += 1
                continue

            point_match = self._history_point_header.match(line)

            if not point_match or not history_instance:
                index += 1
                continue

            field_name = point_match.group(1)
            properties, index = self._history_properties(body, index + 1)
            history_tag = f"{module_name}/{history_instance}.{field_name}"

            results.append(
                HistoryPoint(
                    history_tag=history_tag,
                    module_name=module_name,
                    module_description=description,
                    module_class=module_class,
                    unit_module_name=unit_name,
                    process_cell_name=process_cell_name,
                    af_element_path=af_path(plant_area, module_name),
                    history_instance=history_instance,
                    field_name=field_name,
                    plant_area=plant_area,
                    properties=properties,
                )
            )

        return results

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
