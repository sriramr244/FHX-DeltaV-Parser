import re

from fhx_tool.parsers.object_parser import ObjectParseSpec, ObjectParser


def test_object_parser_keeps_columns_aligned_when_optional_field_is_missing() -> None:
    lines = [
        'MODULE TAG="M1" PLANT_AREA="AREA/UNIT" CATEGORY="CAT"',
        '{',
        '  DESCRIPTION="Description"',
        '  PERIOD=1',
        '}',
    ]
    fields = ("MODULE", "PLANT_AREA", "CATEGORY", "DESCRIPTION", "PERIOD", "CONTROLLER")
    spec = ObjectParseSpec(
        header_pattern=re.compile(r'^MODULE TAG="([^"]+)"'),
        header_value_count=3,
        output_filename="module.csv",
        fields=fields,
    )

    rows = ObjectParser().parse(lines, spec)

    assert rows[0] == list(fields)
    assert rows[1] == ["M1", "AREA/UNIT", "CAT", "Description", "1", ""]
