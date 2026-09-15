from fhx_tool.parsers.module_inventory_parser import ModuleInventoryParser


def test_module_inventory_parser_extracts_module_fields():
    lines = [
        'MODULE_INSTANCE TAG="TEST-101" PLANT_AREA="PLANT/UNIT-1" MODULE_CLASS="AI_CLASS"',
        ' user="TEST.USER" time=1741721346/* "11-Mar-2025 12:29:06" */',
        '{',
        '  DESCRIPTION="Test Module"',
        '  PERIOD=1',
        '  CONTROLLER="CTRL-01"',
        '  PRIMARY_CONTROL_DISPLAY="MAIN_DISPLAY"',
        '  INSTRUMENT_AREA_DISPLAY="FACEPLATE"',
        '  DETAIL_DISPLAY="DETAIL_DISPLAY"',
        '  TYPE="AI"',
        '  SUB_TYPE="AI_STANDARD"',
        '}',
    ]

    records = ModuleInventoryParser().parse(lines)

    assert len(records) == 1

    record = records[0]

    assert record.module_name == "TEST-101"
    assert record.description == "Test Module"
    assert record.controller == "CTRL-01"
    assert record.plant_area == "PLANT/UNIT-1"
    assert record.module_class == "AI_CLASS"
    assert record.module_type == "AI"
    assert record.module_subtype == "AI_STANDARD"
    assert record.primary_display == "MAIN_DISPLAY"
    assert record.faceplate == "FACEPLATE"
    assert record.detail_display == "DETAIL_DISPLAY"
    assert record.user == "TEST.USER"
    assert record.time_stamp == "11-Mar-2025 12:29:06"


def test_module_inventory_parser_uses_logic_solver_for_sif_module():
    lines = [
        'SIF_MODULE TAG="SIF-101" PLANT_AREA="PLANT/SIF-UNIT"',
        ' user="ENGINEER" time=1741721346/* "11-Mar-2025 12:29:06" */',
        '{',
        '  DESCRIPTION="SIS Test Module"',
        '  LOGIC_SOLVER="SIS-CTRL-01"',
        '  TYPE="SIF"',
        '  SUB_TYPE="SAFETY"',
        '}',
    ]

    records = ModuleInventoryParser().parse(lines)

    assert len(records) == 1

    record = records[0]

    assert record.module_name == "SIF-101"
    assert record.description == "SIS Test Module"
    assert record.controller == "SIS-CTRL-01"
    assert record.plant_area == "PLANT/SIF-UNIT"
    assert record.module_class == "(SIS MODULE)"
    assert record.module_type == "SIF"
    assert record.module_subtype == "SAFETY"


def test_module_inventory_parser_handles_unassigned_module():
    lines = [
        'MODULE TAG="CALC-101" PLANT_AREA="PLANT/UTILITIES"',
        ' user="ENGINEER" time=1741721346/* "11-Mar-2025 12:29:06" */',
        '{',
        '  DESCRIPTION="Calculation Module"',
        '  TYPE="CALC"',
        '}',
    ]

    records = ModuleInventoryParser().parse(lines)

    assert len(records) == 1

    record = records[0]

    assert record.module_name == "CALC-101"
    assert record.description == "Calculation Module"
    assert record.controller == ""
    assert record.module_class == ""