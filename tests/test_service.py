from pathlib import Path

from openpyxl import load_workbook

from fhx_tool.config.fhx_schema import OUTPUT_FILES
from fhx_tool.services.fhx_service import (
    FhxProcessingService,
)


def test_service_processes_fhx_and_exports_alarm_report(
    tmp_path: Path,
) -> None:
    source = tmp_path / "generic.fhx"

    source.write_text(
        "\n".join(
            [
                (
                    'MODULE_CLASS NAME="CLASS_AI" '
                    'CATEGORY=""'
                ),
                "{",
                '  DESCRIPTION="Generic class"',
                (
                    '  FUNCTION_BLOCK NAME="AI1" '
                    'DEFINITION="AI"'
                ),
                "  {",
                '    DESCRIPTION="Analog input block"',
                "  }",
                (
                    '  ATTRIBUTE_INSTANCE '
                    'NAME="AI1/HI_LIM"'
                ),
                "  {",
                "    VALUE { CV=80 }",
                "  }",
                (
                    '  ATTRIBUTE_INSTANCE '
                    'NAME="AI1/HI_HYS"'
                ),
                "  {",
                "    VALUE { CV=1 }",
                "  }",
                (
                    '  ATTRIBUTE_INSTANCE '
                    'NAME="AI1/HI_DELAY_ON"'
                ),
                "  {",
                "    VALUE { CV=2 }",
                "  }",
                (
                    '  ATTRIBUTE_INSTANCE '
                    'NAME="AI1/HI_DELAY_OFF"'
                ),
                "  {",
                "    VALUE { CV=0 }",
                "  }",
                (
                    '  ATTRIBUTE_INSTANCE '
                    'NAME="AI1/IN_SCALE"'
                ),
                "  {",
                (
                    '    VALUE { EU100=100 EU0=0 '
                    'UNITS="EU" DECPT=1 }'
                ),
                "  }",
                (
                    '  ATTRIBUTE_INSTANCE '
                    'NAME="HI_ALM"'
                ),
                "  {",
                "    VALUE",
                "    {",
                '      PRIORITY_NAME="WARNING"',
                "      ENAB=T",
                '      ALMATTR="AI1/HI_ACT"',
                '      LIMATTR="AI1/HI_LIM"',
                (
                    '      ALARM_DESCRIPTION='
                    '"Generic high alarm"'
                ),
                "    }",
                "  }",
                "}",
                (
                    'BATCH_EQUIPMENT_UNIT_MODULE '
                    'NAME="UNIT_001" CLASS=""'
                ),
                "{",
                "}",
                (
                    'MODULE_INSTANCE '
                    'TAG="MODULE_001" '
                    'PLANT_AREA="AREA_001/UNIT_001" '
                    'MODULE_CLASS="CLASS_AI" '
                    'CATEGORY=""'
                ),
                "{",
                '  DESCRIPTION="Generic module"',
                '  CONTROLLER="CONTROLLER_001"',
                (
                    '  ATTRIBUTE_INSTANCE '
                    'NAME="AI1/HI_LIM"'
                ),
                "  {",
                "    VALUE { CV=85 }",
                "  }",
                (
                    '  HISTORY_DATA_POINT_INSTANCE '
                    'NAME="AI1/PV"'
                ),
                "  {",
                '    HISTORY_DATA_POINT FIELD="CV"',
                "    {",
                "      ENABLED=T",
                "    }",
                "  }",
                "}",
            ]
        ),
        encoding="utf-16",
    )

    output_directory = tmp_path / "output"

    summary = FhxProcessingService().process(
        source,
        output_directory,
    )

    assert summary.history_point_count == 1
    assert summary.module_inventory_count == 1
    assert summary.alarm_count == 1
    assert summary.alarm_module_count == 1
    assert summary.alarm_report.is_file()

    history_path = (
        output_directory
        / OUTPUT_FILES["history"]
    )

    assert history_path.is_file()

    history_content = history_path.read_text(
        encoding="utf-8-sig"
    )

    assert (
        "MODULE_001/AI1/PV.CV"
        in history_content
    )

    workbook = load_workbook(
        summary.alarm_report
    )

    worksheet = workbook["Module Alarms"]

    assert worksheet["A2"].value == "MODULE_001"
    assert worksheet["B2"].value == "CLASS_AI"
    assert (
        worksheet["C2"].value
        == "AREA_001/UNIT_001"
    )
    assert (
        worksheet["D2"].value
        == "CONTROLLER_001"
    )
    assert worksheet["E2"].value == "HI_ALM"
    assert worksheet["F2"].value == "HI"
    assert worksheet["G2"].value == "AI1"
    assert worksheet["H2"].value == "AI"
    assert (
        worksheet["I2"].value
        == "AI1/HI_ACT"
    )
    assert (
        worksheet["J2"].value
        == "AI1/HI_LIM"
    )
    assert worksheet["K2"].value == 85
    assert worksheet["L2"].value == 1
    assert worksheet["M2"].value == 2
    assert worksheet["N2"].value == 0
    assert worksheet["O2"].value is True
    assert worksheet["P2"].value == "WARNING"
    assert worksheet["Q2"].value == "EU"
    assert (
        worksheet["R2"].value
        == "Generic high alarm"
    )