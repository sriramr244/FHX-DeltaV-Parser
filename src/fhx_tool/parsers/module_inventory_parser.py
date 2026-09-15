from __future__ import annotations

import re
from typing import Sequence

from fhx_tool.domain.models import ModuleInventoryRecord
from fhx_tool.parsers.common import iter_top_level_blocks, quoted_assignments


class ModuleInventoryParser:
    _module_header = re.compile(
        r'^(MODULE_INSTANCE|MODULE|SIF_MODULE)\s+TAG="([^"]+)"'
    )

    _property = re.compile(
        r'^\s*([A-Z0-9_]+)=(?:"([^"]*)"|(.*?))\s*$'
    )

    _user = re.compile(
        r'\buser="([^"]*)"',
        re.IGNORECASE,
    )

    _time_stamp = re.compile(
        r'\btime=[^/\s]+/\*\s*"([^"]*)"\s*\*/',
        re.IGNORECASE,
    )

    def parse(
        self,
        lines: Sequence[str],
    ) -> list[ModuleInventoryRecord]:
        records: list[ModuleInventoryRecord] = []

        for header, body in iter_top_level_blocks(
            lines,
            self._module_header,
        ):
            header_match = self._module_header.match(header)

            if header_match is None:
                continue

            module_kind = header_match.group(1)
            header_values = quoted_assignments(header)

            module_name = header_values.get("TAG", "")
            plant_area = header_values.get("PLANT_AREA", "")

            if module_kind == "MODULE_INSTANCE":
                module_class = header_values.get("MODULE_CLASS", "")
            elif module_kind == "SIF_MODULE":
                module_class = "(SIS MODULE)"
            else:
                module_class = ""

            user, time_stamp = self._metadata(body)
            properties = self._direct_properties(body)

            controller = (
                properties.get("CONTROLLER")
                or properties.get("LOGIC_SOLVER")
                or ""
            )

            records.append(
                ModuleInventoryRecord(
                    module_name=module_name,
                    description=properties.get("DESCRIPTION", ""),
                    controller=controller,
                    plant_area=plant_area,
                    module_class=module_class,
                    module_type=properties.get("TYPE", ""),
                    module_subtype=properties.get("SUB_TYPE", ""),
                    primary_display=properties.get(
                        "PRIMARY_CONTROL_DISPLAY",
                        "",
                    ),
                    faceplate=properties.get(
                        "INSTRUMENT_AREA_DISPLAY",
                        "",
                    ),
                    detail_display=properties.get(
                        "DETAIL_DISPLAY",
                        "",
                    ),
                    user=user,
                    time_stamp=time_stamp,
                )
            )

        return records

    def _metadata(
        self,
        body: Sequence[str],
    ) -> tuple[str, str]:
        user = ""
        time_stamp = ""

        for line in body:
            if "{" in line:
                break

            user_match = self._user.search(line)

            if user_match:
                user = user_match.group(1)

            time_match = self._time_stamp.search(line)

            if time_match:
                time_stamp = time_match.group(1)

        return user, time_stamp

    def _direct_properties(
        self,
        body: Sequence[str],
    ) -> dict[str, str]:
        properties: dict[str, str] = {}
        depth = 0

        for line in body:
            if depth == 1:
                match = self._property.match(line)

                if match:
                    key = match.group(1)
                    quoted_value = match.group(2)
                    raw_value = match.group(3)

                    value = (
                        quoted_value
                        if quoted_value is not None
                        else (raw_value or "").strip()
                    )

                    properties[key] = value

            depth += line.count("{") - line.count("}")

        return properties