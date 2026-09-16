from fhx_tool.services.module_resolver import ModuleResolver


def test_resolves_module_class_and_instance_body() -> None:
    lines = [
        'MODULE_CLASS NAME="CLASS_AI" CATEGORY=""',
        "{",
        '  FUNCTION_BLOCK NAME="AI1" DEFINITION="AI"',
        "  {",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_LIM"',
        "  {",
        "    VALUE { CV=80 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_HYS"',
        "  {",
        "    VALUE { CV=1 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="HI_ALM"',
        "  {",
        "    VALUE",
        "    {",
        "      ENAB=T",
        '      ALMATTR="AI1/HI_ACT"',
        '      LIMATTR="AI1/HI_LIM"',
        "    }",
        "  }",
        "}",
        (
            'MODULE_INSTANCE TAG="MODULE_001" '
            'PLANT_AREA="AREA_001/UNIT_001" '
            'MODULE_CLASS="CLASS_AI" CATEGORY=""'
        ),
        "{",
        '  CONTROLLER="CONTROLLER_001"',
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_LIM"',
        "  {",
        "    VALUE { CV=85 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_HYS"',
        "  {",
        "    VALUE { CV=2 }",
        "  }",
        "}",
    ]

    modules = ModuleResolver().resolve(lines)

    assert len(modules) == 1

    module = modules[0]

    assert module.module_name == "MODULE_001"
    assert module.module_class == "CLASS_AI"
    assert module.plant_area == "AREA_001/UNIT_001"
    assert module.controller == "CONTROLLER_001"

    assert (
        '  FUNCTION_BLOCK NAME="AI1" DEFINITION="AI"'
        in module.effective_body
    )

    assert (
        '    VALUE { CV=80 }'
        in module.effective_body
    )

    assert (
        '    VALUE { CV=85 }'
        in module.effective_body
    )


def test_resolves_classless_module() -> None:
    lines = [
        (
            'MODULE TAG="MODULE_002" '
            'PLANT_AREA="AREA_001/UNIT_002" '
            'CATEGORY=""'
        ),
        "{",
        '  CONTROLLER="CONTROLLER_002"',
        '  FUNCTION_BLOCK NAME="ALM1" DEFINITION="ALM"',
        "  {",
        "  }",
        "}",
    ]

    modules = ModuleResolver().resolve(lines)

    assert len(modules) == 1

    module = modules[0]

    assert module.module_name == "MODULE_002"
    assert module.module_class == ""
    assert module.plant_area == "AREA_001/UNIT_002"
    assert module.controller == "CONTROLLER_002"


def test_handles_missing_module_class() -> None:
    lines = [
        (
            'MODULE_INSTANCE TAG="MODULE_003" '
            'PLANT_AREA="AREA_001/UNIT_003" '
            'MODULE_CLASS="CLASS_MISSING" CATEGORY=""'
        ),
        "{",
        '  CONTROLLER="CONTROLLER_003"',
        "}",
    ]

    modules = ModuleResolver().resolve(lines)

    assert len(modules) == 1
    assert modules[0].module_name == "MODULE_003"
    assert modules[0].module_class == "CLASS_MISSING"
    assert modules[0].effective_body == (
        "{",
        '  CONTROLLER="CONTROLLER_003"',
        "}",
    )