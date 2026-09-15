from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Sequence

from fhx_tool.config.fhx_schema import OUTPUT_FILES
from fhx_tool.domain.models import AttributeRecord, ExportedFile, HistoryPoint, ObjectTable


class CsvExportError(RuntimeError):
    pass


class CsvExporter:
    HISTORY_HEADERS = (
        "HISTORY_TAG",
        "MODULE_NAME",
        "MODULE_DESCRIPTION",
        "MODULE_CLASS",
        "UNIT_MODULE_NAME",
        "PROCESS_CELL_NAME",
        "AF_ELEMENT_PATH",
        "HISTORY_INSTANCE",
        "FIELD",
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
                point.unit_module_name,
                point.process_cell_name,
                point.af_element_path,
                point.history_instance,
                point.field_name,
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
