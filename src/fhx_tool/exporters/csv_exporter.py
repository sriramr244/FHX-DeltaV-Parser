from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Sequence

from fhx_tool.config.fhx_schema import OUTPUT_FILES
from fhx_tool.domain.models import AttributeRecord, ExportedFile, HistoryPoint, ObjectTable, ModuleInventoryRecord


class CsvExportError(RuntimeError):
    pass


class CsvExporter:
    HISTORY_HEADERS = (
    "HISTORY_TAG",
    "MODULE_NAME",
    "MODULE_DESCRIPTION",
    "MODULE_CLASS",
    "PLANT_AREA",
    "UNIT_MODULE_NAME",
    "PROCESS_CELL_NAME",
        )
    MODULE_INVENTORY_HEADERS = (
        "MODULE",
        "DESCRIPTION",
        "CONTROLLER",
        "PLANT_AREA",
        "CLASS",
        "TYPE",
        "SUBTYPE",
        "PRIMARY_DISPLAY",
        "FACEPLATE",
        "DETAIL",
        "USER",
        "TIME_STAMP",
    )

    ATTRIBUTE_HEADERS = ("OBJECT", "ATTRIBUTE", "VALUE")

    def export_all(
        self,
        *,
        output_dir: Path,
        object_tables: Sequence[ObjectTable],
        module_class_attributes: Sequence[AttributeRecord],
        module_instance_attributes: Sequence[AttributeRecord],
        module_attributes: Sequence[AttributeRecord],
        history_points: Sequence[HistoryPoint],
        module_inventory: Sequence[ModuleInventoryRecord],
    ) -> list[ExportedFile]:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise CsvExportError(f"Could not create output directory: {output_dir}") from exc

        exported: list[ExportedFile] = []

        for table in object_tables:
            exported.append(self._write_rows(output_dir / table.output_filename, table.rows))

        exported.append(
            self._write_attributes(
                output_dir / OUTPUT_FILES["module_class_attrib"],
                module_class_attributes,
            )
        )
        exported.append(
            self._write_attributes(
                output_dir / OUTPUT_FILES["module_instance_attrib"],
                module_instance_attributes,
            )
        )
        exported.append(
            self._write_attributes(
                output_dir / OUTPUT_FILES["module_attrib"],
                module_attributes,
            )
        )
        exported.append(
            self._write_history(
                output_dir / OUTPUT_FILES["history"],
                history_points,
            )
        )
        exported.append(
            self._write_module_inventory(
                output_dir / OUTPUT_FILES["module_inventory"],
                module_inventory,
            )
        )

        return exported

    def _write_attributes(
        self,
        path: Path,
        records: Sequence[AttributeRecord],
    ) -> ExportedFile:
        rows: list[Sequence[str]] = [self.ATTRIBUTE_HEADERS]
        rows.extend(
            (record.object_name, record.attribute_name, record.value)
            for record in records
        )
        return self._write_rows(path, rows)

    def _write_history(
        self,
        path: Path,
        points: Sequence[HistoryPoint],
    ) -> ExportedFile:
        rows: list[Sequence[str]] = [self.HISTORY_HEADERS]
        rows.extend(
                (
                    point.history_tag,
                    point.module_name,
                    point.module_description,
                    point.module_class,
                    point.plant_area,
                    point.unit_module_name,
                    point.process_cell_name,
                )
                for point in points
            )
        return self._write_rows(path, rows)

    @staticmethod
    def _write_rows(path: Path, rows: Iterable[Sequence[str]]) -> ExportedFile:
        materialized = list(rows)

        try:
            with path.open("w", newline="", encoding="utf-8-sig") as handle:
                csv.writer(handle).writerows(materialized)
        except OSError as exc:
            raise CsvExportError(f"Could not write CSV file: {path}") from exc

        return ExportedFile(
            name=path.name,
            path=path,
            row_count=max(0, len(materialized) - 1),
        )
    def _write_module_inventory(
        self,
        path: Path,
        records: Sequence[ModuleInventoryRecord],
    ) -> ExportedFile:
        rows: list[Sequence[str]] = [
            self.MODULE_INVENTORY_HEADERS
        ]

        rows.extend(
            (
                record.module_name,
                record.description,
                record.controller,
                record.plant_area,
                record.module_class,
                record.module_type,
                record.module_subtype,
                record.primary_display,
                record.faceplate,
                record.detail_display,
                record.user,
                record.time_stamp,
            )
            for record in records
        )

        return self._write_rows(path, rows)