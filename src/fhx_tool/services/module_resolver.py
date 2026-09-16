from __future__ import annotations

import re
from collections.abc import Sequence

from fhx_tool.domain.models import ResolvedModule
from fhx_tool.parsers.common import (
    iter_top_level_blocks,
    quoted_assignments,
)


class ModuleResolver:
    _module_class_header = re.compile(
        r'^MODULE_CLASS\s+NAME="([^"]+)"'
    )

    _module_instance_header = re.compile(
        r'^MODULE_INSTANCE\s+TAG="([^"]+)"'
    )

    _module_header = re.compile(
        r'^MODULE\s+TAG="([^"]+)"'
    )

    _property = re.compile(
        r'^\s*([A-Z0-9_]+)=(?:"([^"]*)"|(.*?))\s*$'
    )

    def resolve(
        self,
        lines: Sequence[str],
    ) -> list[ResolvedModule]:
        module_classes = self._collect_module_classes(lines)
        resolved_modules = self._resolve_instances(
            lines,
            module_classes,
        )

        resolved_modules.extend(
            self._resolve_classless_modules(lines)
        )

        return resolved_modules

    def _collect_module_classes(
        self,
        lines: Sequence[str],
    ) -> dict[str, tuple[str, ...]]:
        module_classes: dict[str, tuple[str, ...]] = {}

        for header, body in iter_top_level_blocks(
            lines,
            self._module_class_header,
        ):
            header_values = quoted_assignments(header)
            module_class = header_values.get("NAME", "")

            if module_class:
                module_classes[module_class] = tuple(body)

        return module_classes

    def _resolve_instances(
        self,
        lines: Sequence[str],
        module_classes: dict[str, tuple[str, ...]],
    ) -> list[ResolvedModule]:
        resolved_modules: list[ResolvedModule] = []

        for header, instance_body in iter_top_level_blocks(
            lines,
            self._module_instance_header,
        ):
            header_values = quoted_assignments(header)

            module_name = header_values.get("TAG", "")
            module_class = header_values.get(
                "MODULE_CLASS",
                "",
            )
            plant_area = header_values.get(
                "PLANT_AREA",
                "",
            )

            class_body = module_classes.get(
                module_class,
                (),
            )

            effective_body = (
                *class_body,
                *instance_body,
            )

            properties = self._direct_properties(
                effective_body
            )

            resolved_modules.append(
                ResolvedModule(
                    module_name=module_name,
                    module_class=module_class,
                    plant_area=plant_area,
                    controller=properties.get(
                        "CONTROLLER",
                        "",
                    ),
                    effective_body=effective_body,
                )
            )

        return resolved_modules

    def _resolve_classless_modules(
        self,
        lines: Sequence[str],
    ) -> list[ResolvedModule]:
        resolved_modules: list[ResolvedModule] = []

        for header, body in iter_top_level_blocks(
            lines,
            self._module_header,
        ):
            header_values = quoted_assignments(header)
            properties = self._direct_properties(body)

            resolved_modules.append(
                ResolvedModule(
                    module_name=header_values.get(
                        "TAG",
                        "",
                    ),
                    module_class="",
                    plant_area=header_values.get(
                        "PLANT_AREA",
                        "",
                    ),
                    controller=properties.get(
                        "CONTROLLER",
                        "",
                    ),
                    effective_body=tuple(body),
                )
            )

        return resolved_modules

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
                    unquoted_value = match.group(3)

                    properties[key] = (
                        quoted_value
                        if quoted_value is not None
                        else (unquoted_value or "").strip()
                    )

            depth += line.count("{")
            depth -= line.count("}")

        return properties