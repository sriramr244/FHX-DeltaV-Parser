from __future__ import annotations

import logging

from fhx_tool.services.fhx_service import FhxProcessingService, ProcessingSummary
from fhx_tool.ui.ports import DesktopUi
from fhx_tool.ui.tk_adapter import TkDesktopUi


logger = logging.getLogger(__name__)


def build_service() -> FhxProcessingService:
    return FhxProcessingService()


def _success_message(summary: ProcessingSummary) -> str:
    return (
        f"Processed: {summary.source_file.name}\n\n"
        f"History points: {summary.history_point_count}\n"
        f"CSV files exported: {len(summary.exported_files)}\n\n"
        f"Output folder:\n{summary.output_directory}"
    )


def run(ui: DesktopUi, service: FhxProcessingService) -> int:
    source_file = ui.select_fhx_file()

    if source_file is None:
        return 0

    output_directory = source_file.parent / "output"

    try:
        summary = service.process(source_file, output_directory)
    except Exception as exc:
        logger.exception("FHX processing failed")
        ui.show_error("FHX Parser", str(exc))
        return 1

    ui.show_success("FHX Parser", _success_message(summary))
    return 0


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    return run(TkDesktopUi(), build_service())
