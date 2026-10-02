from fhx_tool.parsers.history_parser import HistoryParser


def test_history_parser_builds_pi_tag_and_af_path() -> None:
    lines = [
        'PROCESS_CELL NAME="CELL_001" PLANT_AREA="AREA_001"',
        '{',
        '}',
        'BATCH_EQUIPMENT_UNIT_MODULE NAME="UNIT_001" CLASS=""',
        '{',
        '}',
        'MODULE_INSTANCE TAG="MODULE_001" PLANT_AREA="AREA_001/UNIT_001" MODULE_CLASS="CLASS_HISTORY" CATEGORY=""',
        '{',
        '  DESCRIPTION="Generic history module"',
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

    assert point.history_tag == "MODULE_001/EDC1/OUT_D.CV"
    assert point.module_name == "MODULE_001"
    assert point.module_class == "CLASS_HISTORY"
    assert point.module_description == "Generic history module"
    assert point.unit_module_name == "UNIT_001"
    assert point.process_cell_name == ""
    assert point.plant_area == "AREA_001/UNIT_001"
    assert point.properties["SAMPLE_PERIOD_SECONDS"] == "1"


def test_history_parser_identifies_direct_process_cell_parent() -> None:
    lines = [
        'PROCESS_CELL NAME="CELL_001" PLANT_AREA="AREA_001"',
        '{',
        '}',
        'MODULE_INSTANCE TAG="MODULE_002" PLANT_AREA="AREA_001/CELL_001" MODULE_CLASS="CLASS_AI" CATEGORY=""',
        '{',
        '  DESCRIPTION="Generic analog module"',
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

    assert point.process_cell_name == "CELL_001"
    assert point.unit_module_name == ""
    assert point.history_tag == "MODULE_002/AI1/PV.CV"


def test_inherited_history_merges_partial_override_and_separates_modules():
    lines = '''MODULE_CLASS NAME="AI"
{
 DESCRIPTION="Class description"
 HISTORY_DATA_POINT_INSTANCE NAME="AI1/PV"
 {
  HISTORY_DATA_POINT FIELD="CV"
  {
   ENABLED=T
   SAMPLE_PERIOD_SECONDS=5
  }
  HISTORY_DATA_POINT FIELD="ST"
  {
   ENABLED=T
  }
 }
}
MODULE_INSTANCE TAG="PT101" MODULE_CLASS="AI" PLANT_AREA="AREA"
{
 DESCRIPTION="Instance pressure"
 HISTORY_DATA_POINT_INSTANCE NAME="AI1$PV"
 {
  HISTORY_DATA_POINT FIELD="CV"
  {
   ENABLED=F
  }
 }
}
MODULE_INSTANCE TAG="PT102" MODULE_CLASS="AI" PLANT_AREA="AREA"
{
}
'''.splitlines()
    points = {point.history_tag: point for point in HistoryParser().parse(lines)}
    assert len(points) == 4
    assert points["PT101/AI1/PV.CV"].properties == {"ENABLED": "F", "SAMPLE_PERIOD_SECONDS": "5"}
    assert points["PT101/AI1/PV.CV"].module_description == "Instance pressure"
    assert points["PT102/AI1/PV.CV"].properties["ENABLED"] == "T"
    assert points["PT102/AI1/PV.CV"].module_description == "Class description"


def test_history_field_outside_instance_does_not_attach_to_previous_instance():
    lines = '''MODULE TAG="PT101" PLANT_AREA="AREA"
{
 HISTORY_DATA_POINT_INSTANCE NAME="AI1/PV"
 {
  HISTORY_DATA_POINT FIELD="CV"
  {
   ENABLED=T
  }
 }
 HISTORY_DATA_POINT FIELD="ORPHAN"
 {
  ENABLED=T
 }
}
'''.splitlines()
    assert [p.history_tag for p in HistoryParser().parse(lines)] == ["PT101/AI1/PV.CV"]


def test_history_resolves_actual_block_types_and_instance_overrides():
    lines = '''FUNCTION_BLOCK_DEFINITION NAME="SENSOR" CATEGORY=""
{
 FUNCTION_BLOCK NAME="INPUT" DEFINITION="AI"
 {
 }
}
MODULE_CLASS NAME="PRESSURE"
{
 FUNCTION_BLOCK NAME="TRANSMITTER" DEFINITION="AI"
 {
 }
 FUNCTION_BLOCK NAME="AI1" DEFINITION="CALC"
 {
 }
 FUNCTION_BLOCK NAME="COMP" DEFINITION="SENSOR"
 {
 }
'''
    for path in ('TRANSMITTER/PV', 'AI1/OUT', 'COMP$INPUT$PV', 'MISSING/PV', 'PV'):
        lines += f''' HISTORY_DATA_POINT_INSTANCE NAME="{path}"
 {{
  HISTORY_DATA_POINT FIELD="CV"
  {{
   ENABLED=T
  }}
 }}
'''
    lines += '''}
MODULE_INSTANCE TAG="PT101" MODULE_CLASS="PRESSURE"
{
 FUNCTION_BLOCK NAME="TRANSMITTER" DEFINITION="AO"
 {
 }
}
MODULE_INSTANCE TAG="PT102" MODULE_CLASS="PRESSURE"
{
}
'''
    points = {p.history_tag: p for p in HistoryParser().parse(lines.splitlines())}
    assert len(points) == 10
    assert points['PT101/TRANSMITTER/PV.CV'].block_type == 'AO'
    assert points['PT102/TRANSMITTER/PV.CV'].block_type == 'AI'
    assert points['PT101/AI1/OUT.CV'].block_type == 'CALC'
    nested = points['PT101/COMP/INPUT/PV.CV']
    assert (nested.source_block, nested.block_type, nested.field_name) == ('COMP/INPUT', 'AI', 'CV')
    assert points['PT101/MISSING/PV.CV'].block_type == ''
    assert points['PT101/PV.CV'].source_block == ''
