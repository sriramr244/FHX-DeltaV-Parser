from __future__ import annotations

import re
from typing import Final

MC_FIELDS: Final[tuple[str, ...]] = (
    "MODULE_CLASS",
    "CATEGORY",
    "DESCRIPTION",
    "PERIOD",
    "PRIMARY_CONTROL_DISPLAY",
    "INSTRUMENT_AREA_DISPLAY",
    "DETAIL_DISPLAY",
    "TYPE",
    "SUB_TYPE",
    "NVM",
    "ELECTRONIC_SIGNATURE_POLICY",
)

MI_FIELDS: Final[tuple[str, ...]] = (
    "MODULE_INSTANCE",
    "PLANT_AREA",
    "MODULE_CLASS",
    "CATEGORY",
    "DESCRIPTION",
    "WORK_IN_PROGRESS",
    "PERIOD",
    "CONTROLLER",
    "PRIMARY_CONTROL_DISPLAY",
    "INSTRUMENT_AREA_DISPLAY",
    "DETAIL_DISPLAY",
    "TYPE",
    "SUB_TYPE",
    "NVM",
    "PRINT_BANNER_TITLE1",
    "PRINT_BANNER_TITLE2",
    "PERSIST",
    "USES_CLASS_SIGNATURE_POLICY",
)

MOD_FIELDS: Final[tuple[str, ...]] = (
    "MODULE",
    "PLANT_AREA",
    "CATEGORY",
    "DESCRIPTION",
    "PERIOD",
    "CONTROLLER",
    "PRIMARY_CONTROL_DISPLAY",
    "INSTRUMENT_AREA_DISPLAY",
    "DETAIL_DISPLAY",
    "TYPE",
    "SUB_TYPE",
    "ASSIGN_BLOCKS_TO_H1_CARD",
)

MC_ATTRIBUTES: Final[tuple[str, ...]] = (
    "MODULE_CLASS",
    "ATTRIBUTE_INSTANCE",
    "VALUE",
)

MI_ATTRIBUTES: Final[tuple[str, ...]] = (
    "MODULE_INSTANCE",
    "ATTRIBUTE_INSTANCE",
    "VALUE",
)

MOD_ATTRIBUTES: Final[tuple[str, ...]] = (
    "MODULE",
    "ATTRIBUTE_INSTANCE",
    "VALUE",
)

HEADER_PATTERNS: Final[dict[str, re.Pattern[str]]] = {
    "module_class": re.compile(r'^MODULE_CLASS NAME="([^"]+)"'),
    "module_class_attrib": re.compile(r'^MODULE_CLASS NAME="([^"]+)"'),
    "module_instance": re.compile(r'^MODULE_INSTANCE TAG="([^"]+)"'),
    "module_instance_attrib": re.compile(r'^MODULE_INSTANCE TAG="([^"]+)"'),
    "module": re.compile(r'^MODULE TAG="([^"]+)"'),
    "module_attrib": re.compile(r'^MODULE TAG="([^"]+)"'),
}

SUPPORTED_ALARM_BLOCK_TYPES: Final[frozenset[str]] = frozenset(
    {
        "AI",
        "ALM",
        "PID",
    }
)

ALARM_TYPES: Final[tuple[str, ...]] = (
    "HI_HI",
    "HI",
    "LO_LO",
    "LO",
    "DV_HI",
    "DV_LO",
)

ALARM_TYPE_BY_ACTIVE_PARAMETER: Final[dict[str, str]] = {
    "HI_HI_ACT": "HI_HI",
    "HI_ACT": "HI",
    "LO_LO_ACT": "LO_LO",
    "LO_ACT": "LO",
    "DV_HI_ACT": "DV_HI",
    "DV_LO_ACT": "DV_LO",
}

ALARM_PARAMETER_SUFFIXES: Final[dict[str, str]] = {
    "active": "ACT",
    "limit": "LIM",
    "hysteresis": "HYS",
    "enable": "ENAB",
    "enable_delay": "ENAB_DELAY",
    "delay_on": "DELAY_ON",
    "delay_off": "DELAY_OFF",
}

BLOCK_SCALE_PARAMETERS: Final[tuple[str, ...]] = (
    "IN_SCALE",
    "PV_SCALE",
    "OUT_SCALE",
    "XD_SCALE",
)

TRUE_VALUES: Final[frozenset[str]] = frozenset(
    {
        "T",
        "TRUE",
        "1",
    }
)

ALARM_ATTRIBUTE_SUFFIX: Final[str] = "_ALM"

ALARM_REPORT_HEADERS: Final[tuple[str, ...]] = (
    "Module",
    "Module Class",
    "Plant Area",
    "Controller",
    "Module Alarm",
    "Alarm Type",
    "Source Block",
    "Block Type",
    "Cause Parameter",
    "Limit Parameter",
    "Limit",
    "Hysteresis",
    "Delay On",
    "Delay Off",
    "Enabled",
    "Priority",
    "Units",
    "Description",
)

ALARM_REPORT_COLUMN_WIDTHS: Final[dict[str, float]] = {
    "A": 24,
    "B": 24,
    "C": 24,
    "D": 18,
    "E": 20,
    "F": 14,
    "G": 18,
    "H": 14,
    "I": 30,
    "J": 30,
    "K": 14,
    "L": 14,
    "M": 14,
    "N": 14,
    "O": 12,
    "P": 18,
    "Q": 14,
    "R": 40,
}

ALARM_TYPE_COLORS: Final[dict[str, str]] = {
    "HI_HI": "F4CCCC",
    "HI": "FCE5CD",
    "LO": "D9EAF7",
    "LO_LO": "C9DAF8",
    "DV_HI": "FFF2CC",
    "DV_LO": "D9D2E9",
}

OUTPUT_FILES: Final[dict[str, str]] = {
    "module_class": "_module_class.csv",
    "module_class_attrib": "_module_class_attrib.csv",
    "module_instance": "_module_class_inst.csv",
    "module_instance_attrib": "_module_class_inst_attrib.csv",
    "module": "_classless_module.csv",
    "module_attrib": "_classless_module_attrib.csv",
    "history": "_history_tags.csv",
    "module_inventory": "_module_inventory.csv",
    "alarm_report": "_module_alarm_report.xlsx",
}
