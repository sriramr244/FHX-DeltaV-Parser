from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from fhx_tool.config.fhx_schema import (
    HEADER_PATTERNS,
    OUTPUT_FILES,
)
from fhx_tool.domain.models import ObjectTable, ProcessingSummary, ParserFields
from fhx_tool.exporters.csv_exporter import CsvExporter
from fhx_tool.exporters.excel_exporter import ExcelExporter
from fhx_tool.io.fhx_reader import FhxReader
from fhx_tool.parsers.alarm_parser import AlarmParser
from fhx_tool.parsers.attribute_parser import AttributeParser
from fhx_tool.parsers.history_parser import HistoryParser
from fhx_tool.parsers.module_inventory_parser import (
    ModuleInventoryParser,
)
from fhx_tool.parsers.object_parser import (
    ObjectParseSpec,
    ObjectParser,
)
from fhx_tool.progress.base import ProgressReporter
from fhx_tool.progress.null import NullProgressReporter
from fhx_tool.services.module_resolver import ModuleResolver
from fhx_tool.parsers.composite_parser import CompositeParser


class FhxProcessingService:
    def __init__(
        self,
        fields: ParserFields | None = None,
        *,
        reader: FhxReader | None = None,
        object_parser: ObjectParser | None = None,
        attribute_parser: AttributeParser | None = None,
        history_parser: HistoryParser | None = None,
        module_inventory_parser: (
            ModuleInventoryParser | None
        ) = None,
        module_resolver: ModuleResolver | None = None,
        alarm_parser: AlarmParser | None = None,
        composite_parser: CompositeParser | None = None,
        exporter: CsvExporter | None = None,
        excel_exporter: ExcelExporter | None = None,
        progress: ProgressReporter | None = None,
    ) -> None:
        self._fields = fields or ParserFields()
        self._reader = reader or FhxReader()
        self._object_parser = (
            object_parser or ObjectParser()
        )
        self._attribute_parser = (
            attribute_parser or AttributeParser()
        )
        self._history_parser = (
            history_parser or HistoryParser()
        )
        self._module_inventory_parser = (
            module_inventory_parser
            or ModuleInventoryParser()
        )
        self._module_resolver = (
            module_resolver or ModuleResolver()
        )
        self._alarm_parser = (
            alarm_parser or AlarmParser()
        )
        self._composite_parser = (
            composite_parser or CompositeParser()
        )
        self._exporter = exporter or CsvExporter()
        self._excel_exporter = (
            excel_exporter or ExcelExporter()
        )
        self._progress = (
            progress or NullProgressReporter()
        )

    def process(
        self,
        source_file: Path,
        output_directory: Path,
    ) -> ProcessingSummary:
        source_file = Path(source_file)
        output_directory = Path(output_directory)

        self._progress.start(11)

        try:
            lines = self._reader.read_lines(source_file)
            self._progress.advance("Reading FHX")

            object_tables = self._parse_object_tables(
                lines
            )
            self._progress.advance("Parsing objects")

            module_class_attributes = (
                self._attribute_parser.parse(
                    lines,
                    HEADER_PATTERNS[
                        "module_class_attrib"
                    ],
                    "NAME",
                )
            )
            self._progress.advance(
                "Parsing module class attributes"
            )

            module_instance_attributes = (
                self._attribute_parser.parse(
                    lines,
                    HEADER_PATTERNS[
                        "module_instance_attrib"
                    ],
                    "TAG",
                )
            )
            self._progress.advance(
                "Parsing module instance attributes"
            )

            module_attributes = (
                self._attribute_parser.parse(
                    lines,
                    HEADER_PATTERNS[
                        "module_attrib"
                    ],
                    "TAG",
                )
            )
            self._progress.advance(
                "Parsing module attributes"
            )

            module_inventory = (
                self._module_inventory_parser.parse(
                    lines
                )
            )
            self._progress.advance(
                "Parsing module inventory"
            )

            history_points = (
                self._history_parser.parse(lines)
            )
            self._progress.advance(
                "Parsing history points"
            )

            resolved_modules = (
                self._module_resolver.resolve(lines)
            )
            self._progress.advance(
                "Resolving modules"
            )

            composites = (
                self._composite_parser.parse(lines)
            )

            alarm_records = [
                record
                for module in resolved_modules
                for record in self._alarm_parser.parse(
                    module_name=module.module_name,
                    module_class=module.module_class,
                    plant_area=module.plant_area,
                    controller=module.controller,
                    body=module.effective_body,
                    composites=composites,
                )
            ]
            
            self._progress.advance(
                "Parsing module alarms"
            )

            exported = self._exporter.export_all(
                output_dir=output_directory,
                object_tables=object_tables,
                module_class_attributes=(
                    module_class_attributes
                ),
                module_instance_attributes=(
                    module_instance_attributes
                ),
                module_attributes=module_attributes,
                module_inventory=module_inventory,
                history_points=history_points,
            )
            self._progress.advance(
                "Writing CSV output"
            )

            alarm_export = (
                self._excel_exporter
                .export_alarm_report(
                    output_directory,
                    alarm_records,
                )
            )
            self._progress.advance(
                "Writing alarm report"
            )

            exported_files = (
                tuple(
                    item.path
                    for item in exported
                )
                + (alarm_export.path,)
            )

            alarm_module_count = len(
                {
                    record.module_name
                    for record in alarm_records
                }
            )

            return ProcessingSummary(
                source_file=source_file,
                output_directory=output_directory,
                history_point_count=len(
                    history_points
                ),
                module_inventory_count=len(
                    module_inventory
                ),
                alarm_count=len(alarm_records),
                alarm_module_count=(
                    alarm_module_count
                ),
                alarm_report=alarm_export.path,
                exported_files=exported_files,
            )

        finally:
            self._progress.finish()

    def _parse_object_tables(
        self,
        lines: Sequence[str],
    ) -> list[ObjectTable]:
        specs = (
            ObjectParseSpec(
                header_pattern=(
                    HEADER_PATTERNS[
                        "module_class"
                    ]
                ),
                header_value_count=2,
                output_filename=(
                    OUTPUT_FILES[
                        "module_class"
                    ]
                ),
                fields=(
                    self._fields.module_class
                ),
            ),
            ObjectParseSpec(
                header_pattern=(
                    HEADER_PATTERNS[
                        "module_instance"
                    ]
                ),
                header_value_count=4,
                output_filename=(
                    OUTPUT_FILES[
                        "module_instance"
                    ]
                ),
                fields=(
                    self._fields.module_instance
                ),
            ),
            ObjectParseSpec(
                header_pattern=(
                    HEADER_PATTERNS["module"]
                ),
                header_value_count=3,
                output_filename=(
                    OUTPUT_FILES["module"]
                ),
                fields=self._fields.module,
            ),
        )

        return [
            ObjectTable(
                output_filename=(
                    spec.output_filename
                ),
                rows=self._object_parser.parse(
                    lines,
                    spec,
                ),
            )
            for spec in specs
        ]