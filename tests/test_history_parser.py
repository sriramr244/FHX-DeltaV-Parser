from fhx_tool.parsers.history_parser import HistoryParser


def test_history_parser_builds_pi_tag_and_af_path() -> None:
    lines = [
        'PROCESS_CELL NAME="CELL_001" PLANT_AREA="AREA_001"',
        '{',
        '}',
        'BATCH_EQUIPMENT_UNIT_MODULE NAME="UNIT_001" CLASS=""',
        '{',
        '}',
        'MODULE_INSTANCE TAG="MODULE_001" PLANT_AREA="AREA_001/UNIT_001" MODULE_CLASS="CLASS_HISTORY" CATEGORY=""',
        '{',
        '  DESCRIPTION="Generic history module"',
        '  HISTORY_DATA_POINT_INSTANCE NAME="EDC1/OUT_D"',
        '  {',
        '    HISTORY_DATA_POINT FIELD="CV"',
        '    {',
        '      ENABLED=T',
        '      SAMPLE_PERIOD_SECONDS=1',
        '    }',
        '  }',
        '}',
    ]

    point = HistoryParser().parse(lines)[0]

    assert point.history_tag == "MODULE_001/EDC1/OUT_D.CV"
    assert point.module_name == "MODULE_001"
    assert point.module_class == "CLASS_HISTORY"
    assert point.module_description == "Generic history module"
    assert point.unit_module_name == "UNIT_001"
    assert point.process_cell_name == ""
    assert point.plant_area == "AREA_001/UNIT_001"
    assert point.properties["SAMPLE_PERIOD_SECONDS"] == "1"


def test_history_parser_identifies_direct_process_cell_parent() -> None:
    lines = [
        'PROCESS_CELL NAME="CELL_001" PLANT_AREA="AREA_001"',
        '{',
        '}',
        'MODULE_INSTANCE TAG="MODULE_002" PLANT_AREA="AREA_001/CELL_001" MODULE_CLASS="CLASS_AI" CATEGORY=""',
        '{',
        '  DESCRIPTION="Generic analog module"',
        '  HISTORY_DATA_POINT_INSTANCE NAME="AI1/PV"',
        '  {',
        '    HISTORY_DATA_POINT FIELD="CV"',
        '    {',
        '      ENABLED=T',
        '    }',
        '  }',
        '}',
    ]

    point = HistoryParser().parse(lines)[0]

    assert point.process_cell_name == "CELL_001"
    assert point.unit_module_name == ""
    assert point.history_tag == "MODULE_002/AI1/PV.CV"
