from __future__ import annotations

import logging

from fhx_tool.progress.base import ProgressReporter
from fhx_tool.progress.tk_progress import (
    TkProgressReporter,
)
from fhx_tool.services.fhx_service import (
    FhxProcessingService,
    ProcessingSummary,
)
from fhx_tool.ui.ports import DesktopUi
from fhx_tool.ui.tk_adapter import TkDesktopUi


logger = logging.getLogger(__name__)


def build_service(
    progress: ProgressReporter | None = None,
) -> FhxProcessingService:
    return FhxProcessingService(
        progress=progress,
    )


def _success_message(
    summary: ProcessingSummary,
) -> str:
    return (
        f"Processed: {summary.source_file.name}\n\n"
        f"Modules: "
        f"{summary.module_inventory_count}\n"
        f"History points: "
        f"{summary.history_point_count}\n"
        f"Modules with enabled alarms: "
        f"{summary.alarm_module_count}\n"
        f"Enabled alarms: "
        f"{summary.alarm_count}\n"
        f"Files exported: "
        f"{len(summary.exported_files)}\n\n"
        f"Alarm report:\n"
        f"{summary.alarm_report}\n\n"
        f"Output folder:\n"
        f"{summary.output_directory}"
    )


def run(
    ui: DesktopUi,
    service: FhxProcessingService,
) -> int:
    source_file = ui.select_fhx_file()

    if source_file is None:
        return 0

    output_directory = (
        source_file.parent / "output"
    )

    try:
        summary = service.process(
            source_file,
            output_directory,
        )
    except Exception as exc:
        logger.exception(
            "FHX processing failed"
        )

        ui.show_error(
            "FHX Parser",
            str(exc),
        )

        return 1

    ui.show_success(
        "FHX Parser",
        _success_message(summary),
    )

    return 0


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "%(name)s: "
            "%(message)s"
        ),
    )

    ui = TkDesktopUi()

    try:
        progress = TkProgressReporter(
            ui.root
        )

        service = build_service(
            progress
        )

        return run(
            ui,
            service,
        )

    finally:
        ui.close()