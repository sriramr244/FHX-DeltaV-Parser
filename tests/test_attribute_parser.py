import re

from fhx_tool.parsers.attribute_parser import AttributeParser


def test_attribute_parser_supports_multiline_value_blocks() -> None:
    lines = [
        'MODULE_INSTANCE TAG="M1" PLANT_AREA="AREA" MODULE_CLASS="X" CATEGORY=""',
        '{',
        '  ATTRIBUTE_INSTANCE NAME="TEST"',
        '  {',
        '    VALUE',
        '    {',
        '      REF="//M2/PV.CV"',
        '      CHANGEABLE=T',
        '    }',
        '  }',
        '}',
    ]

    records = AttributeParser().parse(
        lines,
        re.compile(r'^MODULE_INSTANCE TAG="([^"]+)"'),
        "TAG",
    )

    assert len(records) == 1
    assert records[0].object_name == "M1"
    assert records[0].attribute_name == "TEST"
    assert records[0].value == 'REF="//M2/PV.CV" CHANGEABLE=T'


def test_attribute_parser_supports_inline_value_blocks() -> None:
    lines = [
        'MODULE TAG="M1" PLANT_AREA="AREA" CATEGORY=""',
        '{',
        '  ATTRIBUTE_INSTANCE NAME="BAD_ACTIVE"',
        '  {',
        '    VALUE { CV=F }',
        '  }',
        '}',
    ]

    records = AttributeParser().parse(
        lines,
        re.compile(r'^MODULE TAG="([^"]+)"'),
        "TAG",
    )

    assert records[0].value == "CV=F"
