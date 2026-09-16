from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from fhx_tool.config.fhx_schema import (
    ALARM_ATTRIBUTE_SUFFIX,
    ALARM_TYPE_BY_ACTIVE_PARAMETER,
    BLOCK_SCALE_PARAMETERS,
    SUPPORTED_ALARM_BLOCK_TYPES,
    TRUE_VALUES,
)
from fhx_tool.domain.models import AlarmRecord


class AlarmParser:
    _function_block = re.compile(
        r'^\s*FUNCTION_BLOCK\s+'
        r'NAME="([^"]+)"\s+'
        r'DEFINITION="([^"]+)"'
    )

    _attribute_instance = re.compile(
        r'^\s*ATTRIBUTE_INSTANCE\s+NAME="([^"]+)"'
    )

    _quoted_assignment = re.compile(
        r'\b([A-Z0-9_]+)="([^"]*)"'
    )

    _plain_assignment = re.compile(
        r'\b([A-Z0-9_]+)=([^\s{}]+)'
    )

    _current_value = re.compile(
        r'\bCV=(?:"([^"]*)"|([^\s{}]+))'
    )

    _units = re.compile(
        r'\bUNITS="([^"]*)"'
    )

    def parse(
        self,
        *,
        module_name: str,
        module_class: str,
        plant_area: str,
        controller: str,
        body: Sequence[str],
    ) -> list[AlarmRecord]:
        block_types = self._parse_block_types(body)
        attributes = self._parse_attributes(body)
        records: list[AlarmRecord] = []

        for module_alarm, alarm_lines in attributes.items():
            if not self._is_alarm_attribute(module_alarm):
                continue

            alarm_fields = self._parse_assignments(alarm_lines)
            cause_parameter = alarm_fields.get("ALMATTR", "")

            if not cause_parameter:
                continue

            enabled = self._to_bool(
                alarm_fields.get("ENAB", "F")
            )

            if not enabled:
                continue

            source_block, active_parameter = self._split_path(
                cause_parameter
            )

            alarm_type = ALARM_TYPE_BY_ACTIVE_PARAMETER.get(
                active_parameter.upper(),
                "",
            )

            if not alarm_type:
                continue

            block_type = self._find_block_type(
                block_types,
                source_block,
            )

            if block_type.upper() not in SUPPORTED_ALARM_BLOCK_TYPES:
                continue

            limit_parameter = self._resolve_limit_parameter(
                alarm_fields,
                source_block,
                alarm_type,
            )

            hysteresis_parameter = self._build_parameter_path(
                source_block,
                alarm_type,
                "HYS",
            )

            delay_on_parameter = self._build_parameter_path(
                source_block,
                alarm_type,
                "DELAY_ON",
            )

            delay_off_parameter = self._build_parameter_path(
                source_block,
                alarm_type,
                "DELAY_OFF",
            )

            records.append(
                AlarmRecord(
                    module_name=module_name,
                    module_class=module_class,
                    plant_area=plant_area,
                    controller=controller,
                    module_alarm=module_alarm,
                    alarm_type=alarm_type,
                    source_block=source_block,
                    block_type=block_type,
                    cause_parameter=self._normalize_path(
                        cause_parameter
                    ),
                    limit_parameter=limit_parameter,
                    limit=self._attribute_value(
                        attributes,
                        limit_parameter,
                    ),
                    hysteresis=self._attribute_value(
                        attributes,
                        hysteresis_parameter,
                    ),
                    delay_on=self._attribute_value(
                        attributes,
                        delay_on_parameter,
                    ),
                    delay_off=self._attribute_value(
                        attributes,
                        delay_off_parameter,
                    ),
                    enabled=enabled,
                    priority=alarm_fields.get(
                        "PRIORITY_NAME",
                        "",
                    ),
                    units=self._find_units(
                        attributes,
                        source_block,
                    ),
                    description=alarm_fields.get(
                        "ALARM_DESCRIPTION",
                        "",
                    ),
                )
            )

        return records

    def _parse_block_types(
        self,
        body: Sequence[str],
    ) -> dict[str, str]:
        block_types: dict[str, str] = {}

        for line in body:
            match = self._function_block.match(line)

            if match:
                block_types[match.group(1)] = match.group(2)

        return block_types

    def _parse_attributes(
        self,
        body: Sequence[str],
    ) -> dict[str, list[str]]:
        attributes: dict[str, list[str]] = {}
        index = 0

        while index < len(body):
            match = self._attribute_instance.match(body[index])

            if not match:
                index += 1
                continue

            attribute_name = self._normalize_path(
                match.group(1)
            )

            section, index = self._read_braced_section(
                body,
                index,
            )

            attributes[attribute_name] = section

        return attributes

    def _read_braced_section(
        self,
        lines: Sequence[str],
        start: int,
    ) -> tuple[list[str], int]:
        first_line = lines[start]
        section = [first_line]
        index = start + 1
        depth = first_line.count("{") - first_line.count("}")
        started = depth > 0

        while index < len(lines):
            line = lines[index]
            section.append(line)

            if not started and "{" in line:
                started = True

            depth += line.count("{") - line.count("}")
            index += 1

            if started and depth == 0:
                break

        return section, index

    def _parse_assignments(
        self,
        lines: Sequence[str],
    ) -> dict[str, str]:
        assignments: dict[str, str] = {}

        for line in lines:
            for key, value in self._quoted_assignment.findall(
                line
            ):
                assignments[key] = value

            for key, value in self._plain_assignment.findall(
                line
            ):
                assignments.setdefault(key, value)

        return assignments

    def _attribute_value(
        self,
        attributes: Mapping[str, Sequence[str]],
        attribute_name: str,
    ) -> str:
        normalized_name = self._normalize_path(
            attribute_name
        )

        lines = attributes.get(normalized_name)

        if lines is None:
            return ""

        for line in lines:
            match = self._current_value.search(line)

            if match:
                return match.group(1) or match.group(2) or ""

        return ""

    def _find_units(
        self,
        attributes: Mapping[str, Sequence[str]],
        source_block: str,
    ) -> str:
        for scale_parameter in BLOCK_SCALE_PARAMETERS:
            attribute_name = self._build_path(
                source_block,
                scale_parameter,
            )

            lines = attributes.get(attribute_name)

            if lines is None:
                continue

            for line in lines:
                match = self._units.search(line)

                if match:
                    return match.group(1)

        return ""

    def _find_block_type(
        self,
        block_types: Mapping[str, str],
        source_block: str,
    ) -> str:
        direct_match = block_types.get(source_block)

        if direct_match is not None:
            return direct_match

        block_name = source_block.rsplit("/", 1)[-1]
        return block_types.get(block_name, "")

    def _resolve_limit_parameter(
        self,
        alarm_fields: Mapping[str, str],
        source_block: str,
        alarm_type: str,
    ) -> str:
        configured_parameter = alarm_fields.get(
            "LIMATTR",
            ""
        )

        if configured_parameter:
            return self._normalize_path(
                configured_parameter
            )

        return self._build_parameter_path(
            source_block,
            alarm_type,
            "LIM",
        )

    def _split_path(
        self,
        path: str,
    ) -> tuple[str, str]:
        normalized = self._normalize_path(path)

        if "/" not in normalized:
            return "", normalized

        source_block, parameter = normalized.rsplit("/", 1)
        return source_block, parameter

    def _build_parameter_path(
        self,
        source_block: str,
        alarm_type: str,
        suffix: str,
    ) -> str:
        return self._build_path(
            source_block,
            f"{alarm_type}_{suffix}",
        )

    def _build_path(
        self,
        source_block: str,
        parameter: str,
    ) -> str:
        return f"{source_block}/{parameter}"

    def _normalize_path(
        self,
        path: str,
    ) -> str:
        normalized = path.strip()

        while normalized.startswith("^/"):
            normalized = normalized[2:]

        return normalized.lstrip("/")

    def _is_alarm_attribute(
        self,
        attribute_name: str,
    ) -> bool:
        return attribute_name.upper().endswith(
            ALARM_ATTRIBUTE_SUFFIX
        )

    def _to_bool(
        self,
        value: str,
    ) -> bool:
        return value.strip().upper() in TRUE_VALUES