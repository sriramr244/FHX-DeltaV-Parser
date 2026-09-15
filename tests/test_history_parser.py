from fhx_tool.parsers.history_parser import HistoryParser


def test_history_parser_builds_pi_tag_and_af_path() -> None:
    lines = [
        'PROCESS_CELL NAME="LIN-00-AIR" PLANT_AREA="00-PLT-100"',
        '{',
        '}',
        'BATCH_EQUIPMENT_UNIT_MODULE NAME="00-B510" CLASS=""',
        '{',
        '}',
        'MODULE_INSTANCE TAG="00-B510-RESD_O" PLANT_AREA="00-PLT-100/00-B510" MODULE_CLASS="APX_M_NORS_I" CATEGORY=""',
        '{',
        '  DESCRIPTION="Pilot B-510 Process Shutdown"',
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

    assert point.history_tag == "00-B510-RESD_O/EDC1/OUT_D.CV"
    assert point.module_name == "00-B510-RESD_O"
    assert point.module_class == "APX_M_NORS_I"
    assert point.module_description == "Pilot B-510 Process Shutdown"
    assert point.unit_module_name == "00-B510"
    assert point.process_cell_name == ""
    assert point.af_element_path == r"00-PLT-100\00-B510\00-B510-RESD_O"
    assert point.history_instance == "EDC1/OUT_D"
    assert point.field_name == "CV"
    assert point.properties["SAMPLE_PERIOD_SECONDS"] == "1"


def test_history_parser_identifies_direct_process_cell_parent() -> None:
    lines = [
        'PROCESS_CELL NAME="LIN-00-AIR" PLANT_AREA="00-PLT-100"',
        '{',
        '}',
        'MODULE_INSTANCE TAG="00-AI-11109" PLANT_AREA="00-PLT-100/LIN-00-AIR" MODULE_CLASS="A_AI" CATEGORY=""',
        '{',
        '  DESCRIPTION="IA Dryer A Dewpoint"',
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

    assert point.process_cell_name == "LIN-00-AIR"
    assert point.unit_module_name == ""
    assert point.history_tag == "00-AI-11109/AI1/PV.CV"
