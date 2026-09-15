from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence


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