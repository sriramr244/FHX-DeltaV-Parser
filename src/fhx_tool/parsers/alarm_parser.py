from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from fhx_tool.config.fhx_schema import (
    ALARM_PARAMETER_SUFFIXES,
    ALARM_TYPE_BY_ACTIVE_PARAMETER,
    ALARM_VALUE_KEY,
    BLOCK_SCALE_PARAMETERS,
    TRUE_VALUES,
)
from fhx_tool.domain.models import AlarmRecord
from fhx_tool.parsers.common import canonical_path
from fhx_tool.parsers.composite_parser import (
    CompositeCatalog,
)


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
        r'\b([A-Z0-9_]+)=([^\s{}"]+)'
    )

    _cause_fields = (
        "MONATTR",
        "PARAM1",
        "ALMATTR",
    )

    _limit_fields = (
        "PARAM2",
        "PARAM1",
    )

    _limit_suffix = ALARM_PARAMETER_SUFFIXES["limit"]

    _hysteresis_suffix = ALARM_PARAMETER_SUFFIXES[
        "hysteresis"
    ]

    _delay_on_suffix = ALARM_PARAMETER_SUFFIXES[
        "delay_on"
    ]

    _delay_off_suffix = ALARM_PARAMETER_SUFFIXES[
        "delay_off"
    ]

    _block_hysteresis_parameter = "ALARM_HYS"

    def parse(
        self,
        *,
        module_name: str,
        module_class: str,
        plant_area: str,
        controller: str,
        body: Sequence[str],
        composites: CompositeCatalog | None = None,
    ) -> list[AlarmRecord]:
        catalog = composites or CompositeCatalog()
        block_types = self._parse_block_types(body)
        attributes = self._parse_attributes(body)
        records: list[AlarmRecord] = []

        for module_alarm, fields in attributes.items():
            if not self._is_alarm(fields):
                continue

            limit_parameter = self._limit_parameter(
                fields
            )

            cause_parameter = self._cause_parameter(
                fields
            )

            source_block = self._source_block(
                limit_parameter,
                cause_parameter,
            )

            records.append(
                AlarmRecord(
                    module_name=module_name,
                    module_class=module_class,
                    plant_area=plant_area,
                    controller=controller,
                    module_alarm=module_alarm,
                    alarm_type=self._alarm_type(
                        fields
                    ),
                    source_block=source_block,
                    block_type=self._block_type(
                        block_types,
                        catalog,
                        source_block,
                    ),
                    cause_parameter=cause_parameter,
                    limit_parameter=limit_parameter,
                    limit=self._value(
                        attributes,
                        block_types,
                        catalog,
                        limit_parameter,
                    ),
                    hysteresis=self._hysteresis(
                        attributes,
                        block_types,
                        catalog,
                        limit_parameter,
                        source_block,
                    ),
                    delay_on=self._value(
                        attributes,
                        block_types,
                        catalog,
                        self._sibling_parameter(
                            limit_parameter,
                            self._delay_on_suffix,
                        ),
                    ),
                    delay_off=self._value(
                        attributes,
                        block_types,
                        catalog,
                        self._sibling_parameter(
                            limit_parameter,
                            self._delay_off_suffix,
                        ),
                    ),
                    enabled=self._to_bool(
                        fields.get("ENAB", "F")
                    ),
                    priority=fields.get(
                        "PRIORITY_NAME",
                        "",
                    ),
                    units=self._find_units(
                        attributes,
                        source_block,
                    ),
                    description=fields.get(
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
    ) -> dict[str, dict[str, str]]:
        attributes: dict[str, dict[str, str]] = {}
        index = 0

        while index < len(body):
            match = self._attribute_instance.match(body[index])

            if not match:
                index += 1
                continue

            attribute_name = canonical_path(
                match.group(1)
            )

            section, index = self._read_braced_section(
                body,
                index,
            )

            self._merge_assignments(
                attributes.setdefault(
                    attribute_name,
                    {},
                ),
                self._parse_assignments(section),
            )

        return attributes

    def _merge_assignments(
        self,
        target: dict[str, str],
        source: Mapping[str, str],
    ) -> None:
        for key, value in source.items():
            if value != "" or key not in target:
                target[key] = value

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

    def _is_alarm(
        self,
        fields: Mapping[str, str],
    ) -> bool:
        if fields.get(ALARM_VALUE_KEY, "").strip():
            return True

        if not fields.get("ALMATTR", "").strip():
            return False

        return bool(
            fields.get("ENAB", "").strip()
            or fields.get("PRIORITY_NAME", "").strip()
        )

    def _alarm_type(
        self,
        fields: Mapping[str, str],
    ) -> str:
        alarm_type = fields.get(
            ALARM_VALUE_KEY,
            "",
        ).strip()

        if alarm_type:
            return alarm_type

        active_parameter = canonical_path(
            fields.get("ALMATTR", "")
        ).rsplit("/", 1)[-1]

        return ALARM_TYPE_BY_ACTIVE_PARAMETER.get(
            active_parameter.upper(),
            "",
        )

    def _limit_parameter(
        self,
        fields: Mapping[str, str],
    ) -> str:
        configured_parameter = canonical_path(
            fields.get("LIMATTR", "")
        )

        if configured_parameter:
            return configured_parameter

        for field_name in self._limit_fields:
            candidate = canonical_path(
                fields.get(field_name, "")
            )

            if self._is_limit_parameter(candidate):
                return candidate

        return ""

    def _cause_parameter(
        self,
        fields: Mapping[str, str],
    ) -> str:
        for field_name in self._cause_fields:
            candidate = canonical_path(
                fields.get(field_name, "")
            )

            if candidate:
                return candidate

        return ""

    def _source_block(
        self,
        *parameters: str,
    ) -> str:
        for parameter in parameters:
            if "/" in parameter:
                return parameter.rsplit("/", 1)[0]

        return ""

    def _block_type(
        self,
        block_types: Mapping[str, str],
        catalog: CompositeCatalog,
        source_block: str,
    ) -> str:
        if not source_block:
            return ""

        definition = ""
        children: Mapping[str, str] = block_types

        for segment in source_block.split("/"):
            definition = children.get(segment, "")

            if not definition:
                return block_types.get(
                    source_block.rsplit("/", 1)[-1],
                    "",
                )

            children = catalog.blocks.get(definition, {})

        return definition

    def _hysteresis(
        self,
        attributes: Mapping[str, Mapping[str, str]],
        block_types: Mapping[str, str],
        catalog: CompositeCatalog,
        limit_parameter: str,
        source_block: str,
    ) -> str:
        hysteresis = self._value(
            attributes,
            block_types,
            catalog,
            self._sibling_parameter(
                limit_parameter,
                self._hysteresis_suffix,
            ),
        )

        if hysteresis or not source_block:
            return hysteresis

        return self._value(
            attributes,
            block_types,
            catalog,
            (
                f"{source_block}/"
                f"{self._block_hysteresis_parameter}"
            ),
        )

    def _sibling_parameter(
        self,
        limit_parameter: str,
        suffix: str,
    ) -> str:
        if not self._is_limit_parameter(limit_parameter):
            return ""

        stem = limit_parameter[
            : -len(self._limit_suffix)
        ]

        return f"{stem}{suffix}"

    def _is_limit_parameter(
        self,
        parameter: str,
    ) -> bool:
        return parameter.upper().endswith(
            self._limit_suffix
        )

    def _value(
        self,
        attributes: Mapping[str, Mapping[str, str]],
        block_types: Mapping[str, str],
        catalog: CompositeCatalog,
        parameter: str,
    ) -> str:
        if not parameter:
            return ""

        path = canonical_path(parameter)
        value = attributes.get(path, {}).get("CV", "")

        if value:
            return value

        exposed_parameter = self._exposed_parameter(
            block_types,
            catalog,
            path,
        )

        if not exposed_parameter:
            return value

        return attributes.get(
            exposed_parameter,
            {},
        ).get("CV", value)

    def _exposed_parameter(
        self,
        block_types: Mapping[str, str],
        catalog: CompositeCatalog,
        parameter: str,
    ) -> str:
        if parameter.count("/") < 2:
            return ""

        source_block, inner_parameter = parameter.split(
            "/",
            1,
        )

        definition = block_types.get(source_block, "")

        if not definition:
            return ""

        exposed = catalog.aliases.get(
            definition,
            {},
        ).get(inner_parameter, "")

        return (
            f"{source_block}/{exposed}"
            if exposed
            else ""
        )

    def _find_units(
        self,
        attributes: Mapping[str, Mapping[str, str]],
        source_block: str,
    ) -> str:
        for parameter in self._scale_parameters(
            source_block
        ):
            units = attributes.get(
                parameter,
                {},
            ).get("UNITS", "").strip()

            if units:
                return units

        return self._module_units(attributes)

    def _scale_parameters(
        self,
        source_block: str,
    ) -> list[str]:
        if not source_block:
            return list(BLOCK_SCALE_PARAMETERS)

        root_block = source_block.split("/", 1)[0]
        blocks = [source_block]

        if root_block != source_block:
            blocks.append(root_block)

        scoped = [
            f"{block}/{parameter}"
            for block in blocks
            for parameter in BLOCK_SCALE_PARAMETERS
        ]

        return scoped + list(BLOCK_SCALE_PARAMETERS)

    def _module_units(
        self,
        attributes: Mapping[str, Mapping[str, str]],
    ) -> str:
        for parameter in BLOCK_SCALE_PARAMETERS:
            units = {
                fields.get("UNITS", "").strip()
                for name, fields in attributes.items()
                if name.rsplit("/", 1)[-1] == parameter
                and fields.get("UNITS", "").strip()
            }

            if len(units) == 1:
                return units.pop()

        return ""

    def _to_bool(
        self,
        value: str,
    ) -> bool:
        return value.strip().upper() in TRUE_VALUES