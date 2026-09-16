from fhx_tool.parsers.alarm_parser import AlarmParser


def test_extracts_enabled_alarms_from_originating_blocks() -> None:
    body = [
        '  FUNCTION_BLOCK NAME="AI1" DEFINITION="AI"',
        "  {",
        "  }",
        '  FUNCTION_BLOCK NAME="PID1" DEFINITION="PID"',
        "  {",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_HI_LIM"',
        "  {",
        "    VALUE { CV=95 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_HI_HYS"',
        "  {",
        "    VALUE { CV=0.5 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_HI_DELAY_ON"',
        "  {",
        "    VALUE { CV=2 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_HI_DELAY_OFF"',
        "  {",
        "    VALUE { CV=1 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/IN_SCALE"',
        "  {",
        '    VALUE { EU100=100 EU0=0 UNITS="EU" DECPT=1 }',
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="PID1/DV_HI_LIM"',
        "  {",
        "    VALUE { CV=10 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="PID1/DV_HI_HYS"',
        "  {",
        "    VALUE { CV=1.5 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="PID1/PV_SCALE"',
        "  {",
        '    VALUE { EU100=100 EU0=0 UNITS="EU" DECPT=1 }',
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="HI_HI_ALM"',
        "  {",
        "    VALUE",
        "    {",
        '      PRIORITY_NAME="CRITICAL"',
        "      ENAB=T",
        '      ALMATTR="AI1/HI_HI_ACT"',
        '      LIMATTR="AI1/HI_HI_LIM"',
        '      ALARM_DESCRIPTION="Generic high-high alarm"',
        "    }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="LO_ALM"',
        "  {",
        "    VALUE",
        "    {",
        "      ENAB=F",
        '      ALMATTR="AI1/LO_ACT"',
        '      LIMATTR="AI1/LO_LIM"',
        "    }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="DV_HI_ALM"',
        "  {",
        "    VALUE",
        "    {",
        '      PRIORITY_NAME="WARNING"',
        "      ENAB=T",
        '      ALMATTR="PID1/DV_HI_ACT"',
        '      LIMATTR="PID1/DV_HI_LIM"',
        '      ALARM_DESCRIPTION="Generic deviation alarm"',
        "    }",
        "  }",
    ]

    records = AlarmParser().parse(
        module_name="MODULE_001",
        module_class="CLASS_AI_PID",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=body,
    )

    assert len(records) == 2
    assert records[0].module_name == "MODULE_001"
    assert records[0].source_block == "AI1"
    assert records[0].alarm_type == "HI_HI"
    assert records[0].limit == "95"
    assert records[0].hysteresis == "0.5"
    assert records[0].units == "EU"
    assert records[1].source_block == "PID1"
    assert records[1].alarm_type == "DV_HI"
    assert records[1].limit == "10"
    assert records[1].hysteresis == "1.5"


def test_ignores_alarm_from_unsupported_block_type() -> None:
    body = [
        '  FUNCTION_BLOCK NAME="AO1" DEFINITION="AO"',
        "  {",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="HI_ALM"',
        "  {",
        "    VALUE",
        "    {",
        "      ENAB=T",
        '      ALMATTR="AO1/HI_ACT"',
        '      LIMATTR="AO1/HI_LIM"',
        "    }",
        "  }",
    ]

    records = AlarmParser().parse(
        module_name="MODULE_002",
        module_class="CLASS_AO",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=body,
    )

    assert records == []


def test_instance_values_override_class_values() -> None:
    class_body = [
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
    ]
    instance_body = [
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_LIM"',
        "  {",
        "    VALUE { CV=85 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_HYS"',
        "  {",
        "    VALUE { CV=2 }",
        "  }",
    ]

    records = AlarmParser().parse(
        module_name="MODULE_003",
        module_class="CLASS_AI",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=[*class_body, *instance_body],
    )

    assert len(records) == 1
    assert records[0].limit == "85"
    assert records[0].hysteresis == "2"
