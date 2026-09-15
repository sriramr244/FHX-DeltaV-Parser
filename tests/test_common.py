from fhx_tool.parsers.common import af_path, leaf_name, quoted_assignments


def test_path_helpers() -> None:
    assert leaf_name("00-PLT-100/00-B510") == "00-B510"
    assert af_path("00-PLT-100/00-B510", "M1") == r"00-PLT-100\00-B510\M1"


def test_quoted_assignments() -> None:
    header = 'MODULE_INSTANCE TAG="M1" PLANT_AREA="A/U" MODULE_CLASS="AI" CATEGORY=""'
    values = quoted_assignments(header)
    assert values["TAG"] == "M1"
    assert values["MODULE_CLASS"] == "AI"
