from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from fhx_tool.config.fhx_schema import (
    HEADER_PATTERNS,
    MC_FIELDS,
    MI_FIELDS,
    MOD_FIELDS,
    OUTPUT_FILES,
)
from fhx_tool.domain.models import ObjectTable
from fhx_tool.exporters.csv_exporter import CsvExporter
from fhx_tool.io.fhx_reader import FhxReader
from fhx_tool.parsers.attribute_parser import AttributeParser
from fhx_tool.parsers.history_parser import HistoryParser
from fhx_tool.parsers.object_parser import ObjectParseSpec, ObjectParser


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
    exported_files: tuple[Path, ...]


class FhxProcessingService:
    def __init__(
        self,
        fields: ParserFields | None = None,
        *,
        reader: FhxReader | None = None,
        object_parser: ObjectParser | None = None,
        attribute_parser: AttributeParser | None = None,
        history_parser: HistoryParser | None = None,
        exporter: CsvExporter | None = None,
    ) -> None:
        self._fields = fields or ParserFields()
        self._reader = reader or FhxReader()
        self._object_parser = object_parser or ObjectParser()
        self._attribute_parser = attribute_parser or AttributeParser()
        self._history_parser = history_parser or HistoryParser()
        self._exporter = exporter or CsvExporter()

    def process(self, source_file: Path, output_directory: Path) -> ProcessingSummary:
        source_file = Path(source_file)
        output_directory = Path(output_directory)
        lines = self._reader.read_lines(source_file)

        object_tables = self._parse_object_tables(lines)
        module_class_attributes = self._attribute_parser.parse(
            lines,
            HEADER_PATTERNS["module_class_attrib"],
            "NAME",
        )
        module_instance_attributes = self._attribute_parser.parse(
            lines,
            HEADER_PATTERNS["module_instance_attrib"],
            "TAG",
        )
        module_attributes = self._attribute_parser.parse(
            lines,
            HEADER_PATTERNS["module_attrib"],
            "TAG",
        )
        history_points = self._history_parser.parse(lines)

        exported = self._exporter.export_all(
            output_dir=output_directory,
            object_tables=object_tables,
            module_class_attributes=module_class_attributes,
            module_instance_attributes=module_instance_attributes,
            module_attributes=module_attributes,
            history_points=history_points,
        )

        return ProcessingSummary(
            source_file=source_file,
            output_directory=output_directory,
            history_point_count=len(history_points),
            exported_files=tuple(item.path for item in exported),
        )

    def _parse_object_tables(self, lines: Sequence[str]) -> list[ObjectTable]:
        specs = (
            ObjectParseSpec(
                header_pattern=HEADER_PATTERNS["module_class"],
                header_value_count=2,
                output_filename=OUTPUT_FILES["module_class"],
                fields=self._fields.module_class,
            ),
            ObjectParseSpec(
                header_pattern=HEADER_PATTERNS["module_instance"],
                header_value_count=4,
                output_filename=OUTPUT_FILES["module_instance"],
                fields=self._fields.module_instance,
            ),
            ObjectParseSpec(
                header_pattern=HEADER_PATTERNS["module"],
                header_value_count=3,
                output_filename=OUTPUT_FILES["module"],
                fields=self._fields.module,
            ),
        )

        return [
            ObjectTable(
                output_filename=spec.output_filename,
                rows=self._object_parser.parse(lines, spec),
            )
            for spec in specs
        ]
