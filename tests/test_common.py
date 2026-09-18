from fhx_tool.parsers.common import af_path, leaf_name, quoted_assignments


def test_path_helpers() -> None:
    assert leaf_name("AREA_001/UNIT_001") == "UNIT_001"
    assert af_path("AREA_001/UNIT_001", "MODULE_001") == r"AREA_001\UNIT_001\MODULE_001"


def test_quoted_assignments() -> None:
    header = 'MODULE_INSTANCE TAG="MODULE_001" PLANT_AREA="AREA_001/UNIT_001" MODULE_CLASS="CLASS_AI" CATEGORY=""'
    values = quoted_assignments(header)
    assert values["TAG"] == "MODULE_001"
    assert values["MODULE_CLASS"] == "CLASS_AI"
