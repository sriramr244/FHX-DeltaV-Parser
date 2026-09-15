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

OUTPUT_FILES: Final[dict[str, str]] = {
    "module_class": "_module_class.csv",
    "module_class_attrib": "_module_class_attrib.csv",
    "module_instance": "_module_class_inst.csv",
    "module_instance_attrib": "_module_class_inst_attrib.csv",
    "module": "_classless_module.csv",
    "module_attrib": "_classless_module_attrib.csv",
    "history": "_history_tags.csv",
}
