from pathlib import Path

from fhx_tool.services.fhx_service import FhxProcessingService


def test_service_processes_utf16_fhx_and_exports_history(tmp_path: Path) -> None:
    source = tmp_path / "small.fhx"
    source.write_text(
        "\n".join(
            [
                'BATCH_EQUIPMENT_UNIT_MODULE NAME="UNIT-1" CLASS=""',
                '{',
                '}',
                'MODULE_INSTANCE TAG="M1" PLANT_AREA="AREA/UNIT-1" MODULE_CLASS="AI" CATEGORY=""',
                '{',
                '  DESCRIPTION="Test module"',
                '  HISTORY_DATA_POINT_INSTANCE NAME="AI1/PV"',
                '  {',
                '    HISTORY_DATA_POINT FIELD="CV"',
                '    {',
                '      ENABLED=T',
                '    }',
                '  }',
                '}',
            ]
        ),
        encoding="utf-16",
    )

    output = tmp_path / "output"
    summary = FhxProcessingService().process(source, output)

    assert summary.history_point_count == 1
    history_csv = output / "_history_tags.csv"
    assert history_csv.is_file()
    assert "M1/AI1/PV.CV" in history_csv.read_text(encoding="utf-8-sig")
