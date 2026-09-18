from fhx_tool.parsers.alarm_parser import AlarmParser
from fhx_tool.parsers.composite_parser import CompositeParser


def test_extracts_alarms_from_originating_blocks() -> None:
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

    records_by_alarm = {
        record.module_alarm: record
        for record in records
    }

    assert set(records_by_alarm) == {
        "HI_HI_ALM",
        "LO_ALM",
        "DV_HI_ALM",
    }

    high_high = records_by_alarm["HI_HI_ALM"]

    assert high_high.module_name == "MODULE_001"
    assert high_high.source_block == "AI1"
    assert high_high.block_type == "AI"
    assert high_high.alarm_type == "HI_HI"
    assert high_high.limit == "95"
    assert high_high.hysteresis == "0.5"
    assert high_high.delay_on == "2"
    assert high_high.delay_off == "1"
    assert high_high.units == "EU"
    assert high_high.enabled is True

    deviation = records_by_alarm["DV_HI_ALM"]

    assert deviation.source_block == "PID1"
    assert deviation.alarm_type == "DV_HI"
    assert deviation.limit == "10"
    assert deviation.hysteresis == "1.5"


def test_disabled_alarms_are_reported_as_disabled() -> None:
    body = [
        '  FUNCTION_BLOCK NAME="AI1" DEFINITION="AI"',
        "  {",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/LO_LIM"',
        "  {",
        "    VALUE { CV=5 }",
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
    ]

    records = AlarmParser().parse(
        module_name="MODULE_002",
        module_class="CLASS_AI",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=body,
    )

    assert len(records) == 1
    assert records[0].enabled is False
    assert records[0].limit == "5"


def test_reports_alarms_from_any_block_type() -> None:
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
        module_name="MODULE_003",
        module_class="CLASS_AO",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=body,
    )

    assert len(records) == 1
    assert records[0].source_block == "AO1"
    assert records[0].block_type == "AO"


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
        module_name="MODULE_004",
        module_class="CLASS_AI",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=[*class_body, *instance_body],
    )

    assert len(records) == 1
    assert records[0].limit == "85"
    assert records[0].hysteresis == "2"


def test_instance_dollar_paths_override_class_slash_paths() -> None:
    class_body = [
        '  FUNCTION_BLOCK NAME="AI1" DEFINITION="AI"',
        "  {",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/HI_LIM"',
        "  {",
        "    VALUE { CV=80 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="HI_ALM"',
        "  {",
        "    VALUE",
        "    {",
        '      PRIORITY_NAME="WARNING"',
        "      ENAB=T",
        '      ATYP="High Alarm"',
        '      MONATTR="AI1/OUT"',
        '      ALMATTR="AI1/HI_ACT"',
        '      LIMATTR="AI1/HI_LIM"',
        "    }",
        "  }",
    ]
    instance_body = [
        '  ATTRIBUTE_INSTANCE NAME="AI1$HI_LIM"',
        "  {",
        "    VALUE { CV=20 }",
        "    EXPLICIT_OVERRIDE=T",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1$OUT_SCALE"',
        "  {",
        '    VALUE { EU100=100 EU0=0 UNITS="EU" DECPT=1 }',
        "    EXPLICIT_OVERRIDE=T",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="HI_ALM"',
        "  {",
        "    VALUE",
        "    {",
        '      PRIORITY_NAME="CRITICAL"',
        "      ENAB=T",
        '      ATYP="High Alarm"',
        "    }",
        "    EXPLICIT_OVERRIDE=T",
        "  }",
    ]

    records = AlarmParser().parse(
        module_name="MODULE_005",
        module_class="CLASS_AI",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=[*class_body, *instance_body],
    )

    assert len(records) == 1
    assert records[0].cause_parameter == "AI1/OUT"
    assert records[0].limit_parameter == "AI1/HI_LIM"
    assert records[0].limit == "20"
    assert records[0].priority == "CRITICAL"
    assert records[0].alarm_type == "High Alarm"
    assert records[0].units == "EU"


def test_alarm_without_alm_suffix_is_reported() -> None:
    body = [
        '  FUNCTION_BLOCK NAME="AI1" DEFINITION="AI"',
        "  {",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="AI1/LO_LIM"',
        "  {",
        "    VALUE { CV=-1.25 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="MAINT_REQ"',
        "  {",
        "    VALUE",
        "    {",
        '      PRIORITY_NAME="ADVISORY"',
        "      ENAB=F",
        '      ATYP="Advisory Alarm"',
        '      MONATTR="AI1/OUT"',
        '      LIMATTR="AI1/LO_LIM"',
        "    }",
        "  }",
    ]

    records = AlarmParser().parse(
        module_name="MODULE_006",
        module_class="CLASS_AI",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=body,
    )

    assert [
        record.module_alarm for record in records
    ] == ["MAINT_REQ"]
    assert records[0].alarm_type == "Advisory Alarm"
    assert records[0].limit == "-1.25"


def test_composite_paths_resolve_block_type_and_limit() -> None:
    definition_lines = [
        (
            'FUNCTION_BLOCK_DEFINITION NAME="COMPOSITE_001" '
            'CATEGORY="Library"'
        ),
        "{",
        '  FUNCTION_BLOCK NAME="ALM1" DEFINITION="ALM"',
        "  {",
        "  }",
        (
            '  WIRE SOURCE="ALM1/HI_LIM" '
            'DESTINATION="EXPOSED_HI_LIM" { }'
        ),
        "}",
    ]

    body = [
        (
            '  FUNCTION_BLOCK NAME="SD_BLK" '
            'DEFINITION="COMPOSITE_001"'
        ),
        "  {",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="SD_BLK/EXPOSED_HI_LIM"',
        "  {",
        "    VALUE { CV=60 }",
        "  }",
        '  ATTRIBUTE_INSTANCE NAME="HI_SD_ALM"',
        "  {",
        "    VALUE",
        "    {",
        '      PRIORITY_NAME="CRITICAL"',
        "      ENAB=T",
        '      ATYP="High Alarm"',
        '      MONATTR="SD_BLK/ALM1/PV"',
        '      ALMATTR="SD_BLK/ALM1/HI_ACT"',
        '      LIMATTR="SD_BLK/ALM1/HI_LIM"',
        "    }",
        "  }",
    ]

    composites = CompositeParser().parse(definition_lines)

    records = AlarmParser().parse(
        module_name="MODULE_007",
        module_class="CLASS_AI_SD",
        plant_area="AREA_001/UNIT_001",
        controller="CONTROLLER_001",
        body=body,
        composites=composites,
    )

    assert len(records) == 1
    assert records[0].source_block == "SD_BLK/ALM1"
    assert records[0].block_type == "ALM"
    assert (
        records[0].limit_parameter == "SD_BLK/ALM1/HI_LIM"
    )
    assert records[0].limit == "60"