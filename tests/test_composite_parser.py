from fhx_tool.parsers.composite_parser import CompositeParser


def test_indexes_child_blocks_and_exposed_parameter_wires() -> None:
    lines = [
        (
            'FUNCTION_BLOCK_DEFINITION NAME="COMPOSITE_001" '
            'CATEGORY="Library"'
        ),
        "{",
        '  FUNCTION_BLOCK NAME="ALM1" DEFINITION="ALM"',
        "  {",
        "  }",
        '  FUNCTION_BLOCK NAME="CALC1" DEFINITION="CALC"',
        "  {",
        "  }",
        (
            '  WIRE SOURCE="ALM1/HI_HI_LIM" '
            'DESTINATION="EXPOSED_HI_HI_LIM" { }'
        ),
        (
            '  WIRE SOURCE="IN_SCALE" '
            'DESTINATION="ALM1/IN_SCALE" { }'
        ),
        (
            '  WIRE SOURCE="ALM1/HI_ACT" '
            'DESTINATION="CALC1/IN2" { }'
        ),
        "}",
    ]

    catalog = CompositeParser().parse(lines)

    assert catalog.blocks["COMPOSITE_001"] == {
        "ALM1": "ALM",
        "CALC1": "CALC",
    }
    assert (
        catalog.aliases["COMPOSITE_001"]["ALM1/HI_HI_LIM"]
        == "EXPOSED_HI_HI_LIM"
    )
    assert (
        catalog.aliases["COMPOSITE_001"]["ALM1/IN_SCALE"]
        == "IN_SCALE"
    )
    assert (
        "ALM1/HI_ACT"
        not in catalog.aliases["COMPOSITE_001"]
    )


def test_returns_empty_catalog_without_definitions() -> None:
    lines = [
        'MODULE_CLASS NAME="CLASS_001"',
        "{",
        "}",
    ]

    catalog = CompositeParser().parse(lines)

    assert catalog.blocks == {}
    assert catalog.aliases == {}