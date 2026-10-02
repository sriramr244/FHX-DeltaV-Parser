from dataclasses import replace

import pytest

from fhx_tool.domain.models import ModuleInventoryRecord
from fhx_tool.services.module_filter import ModuleFilter


def module(name, description="", module_class=""):
    return ModuleInventoryRecord(name, description, "C1", "AREA", module_class, "", "", "", "", "", "", "")


@pytest.mark.parametrize("name,description,expected", [
    ("10-PT-101", "Wellhead pressure", "KEEP"),
    ("10-TT-101", "", "KEEP"),
    ("10-FIC-101", "", "KEEP"),
    ("10-LIT-101", "", "KEEP"),
    ("10-XV-101", "", "KEEP"),
    ("M1", "Power monitoring", "KEEP"),
    ("M1", "Pressure signal select", "REMOVE"),
    ("M1", "Temperature trip", "REMOVE"),
    ("M1", "Building fans", "REMOVE"),
    ("M1", "Heat trace", "REMOVE"),
    ("M1", "Gas detector", "REMOVE"),
    ("ESD101", "", "REMOVE"),
    ("M1", "Unknown equipment", "REVIEW"),
    ("PT101B", "Backup pressure transmitter", "REVIEW"),
    ("PT101", "", "KEEP"),
])
def test_classification(name, description, expected):
    assert ModuleFilter().classify([module(name, description)])[0].classification == expected


def test_sis_class_is_excluded():
    assert ModuleFilter().classify([module("PT101", module_class="(SIS MODULE)")])[0].classification == "REMOVE"


def test_redundant_suffix_never_establishes_primary():
    rows = [module("PT101A", "Pressure"), module("PT101B", "Pressure")]
    assert [d.classification for d in ModuleFilter().classify(rows)] == ["REVIEW", "REVIEW"]
    rows[1] = replace(rows[1], description="Primary pressure transmitter")
    assert [d.classification for d in ModuleFilter().classify(rows)] == ["REMOVE", "KEEP"]


def test_numbered_tags_are_not_automatically_deduplicated():
    assert [d.classification for d in ModuleFilter().classify([module("PT101"), module("PT102")])] == ["KEEP", "KEEP"]


def test_explicit_decision_overrides_rules():
    assert ModuleFilter({"M1": "KEEP"}).classify([module("M1")])[0].classification == "KEEP"
    with pytest.raises(ValueError):
        ModuleFilter({"M1": "INVALID"})
