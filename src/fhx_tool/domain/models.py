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
    unit_module_name: str
    process_cell_name: str
    af_element_path: str
    history_instance: str
    field_name: str
    plant_area: str
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
