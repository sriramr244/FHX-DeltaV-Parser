from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence
from fhx_tool.config.fhx_schema import (
    MC_FIELDS,
    MI_FIELDS,
    MOD_FIELDS,
)


@dataclass(frozen=True, slots=True)
class HistoryPoint:
    history_tag: str
    module_name: str
    module_description: str
    module_class: str
    plant_area: str
    unit_module_name: str
    process_cell_name: str
    properties: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AttributeRecord:
    object_name: str
    attribute_name: str
    value: str


@dataclass(frozen=True, slots=True)
class ObjectTable:
    output_filename: str
    rows: Sequence[Sequence[str]]


@dataclass(frozen=True, slots=True)
class ExportedFile:
    name: str
    path: Path
    row_count: int

    
@dataclass(frozen=True, slots=True)
class ModuleInventoryRecord:
    module_name: str
    description: str
    controller: str
    plant_area: str
    module_class: str
    module_type: str
    module_subtype: str
    primary_display: str
    faceplate: str
    detail_display: str
    user: str
    time_stamp: str

@dataclass(frozen=True, slots=True)
class AlarmRecord:
    module_name: str
    module_class: str
    plant_area: str
    controller: str

    module_alarm: str
    alarm_type: str

    source_block: str
    block_type: str
    cause_parameter: str

    limit_parameter: str
    limit: str
    hysteresis: str
    delay_on: str
    delay_off: str

    enabled: bool
    priority: str
    units: str
    description: str

@dataclass(frozen=True, slots=True)
class ResolvedModule:
    module_name: str
    module_class: str
    plant_area: str
    controller: str
    effective_body: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class CompositeCatalog:
    blocks: dict[str, dict[str, str]] = field(
        default_factory=dict
    )

    aliases: dict[str, dict[str, str]] = field(
        default_factory=dict
    )

@dataclass(frozen=True, slots=True)
class ParserFields:
    module_class: Sequence[str] = MC_FIELDS
    module_instance: Sequence[str] = MI_FIELDS
    module: Sequence[str] = MOD_FIELDS


@dataclass(frozen=True, slots=True)
class ProcessingSummary:
    source_file: Path
    output_directory: Path
    history_point_count: int
    module_inventory_count: int
    alarm_count: int
    alarm_module_count: int
    alarm_report: Path
    exported_files: tuple[Path, ...]