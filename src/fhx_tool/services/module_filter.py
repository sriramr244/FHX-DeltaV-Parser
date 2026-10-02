"""Conservative, auditable module selection for the instrumentation report."""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping, Sequence

from fhx_tool.domain.models import ModuleInventoryRecord


@dataclass(frozen=True)
class ModuleDecision:
    module: ModuleInventoryRecord
    classification: str
    category: str
    reason: str


class ModuleFilter:
    # Evaluate module metadata only: an ordinary pressure module's trip alarm
    # does not make the entire module a trip-only function.
    exclusions = (
        (r"\bSIGNAL\s+SELECT(?:OR)?\b|\bSELECTOR\b", "Signal selector"),
        (r"\b(?:ESD|SIS|SIF|SAFETY|FIRE|DETECTOR|DETECTORS)\b|\bF\s*&\s*G\b|\bBUILDING\s+FAN\w*\b", "Safety / building system"),
        (r"\b(?:TRIP|INTERLOCK|SHUTDOWN)\b", "Trip / interlock function"),
        (r"\bHEAT\s*TRAC(?:E|ING)\b|\bHTR\b", "Heat trace"),
    )
    categories = (
        ("Power", r"\b(?:POWER|ELECTRICAL|VOLTAGE|CURRENT|KW|KWH|AMPERAGE)\b", r"(?:EI|ET|EIT|II|IT|IIT|JI|JT|JIT)"),
        ("Temperature", r"\b(?:TEMP|TEMPERATURE)\b", r"T(?:T|IT|I|IC|C|E)"),
        ("Flow", r"\bFLOW\b", r"F(?:T|IT|I|IC|C|QI|QIT)"),
        ("Pressure", r"\bPRESSURE\b", r"P(?:T|IT|I|IC|C|DT|DIT)"),
        ("Level", r"\bLEVEL\b", r"L(?:T|IT|I|IC|C)"),
        ("Valve", r"\bVALVE\w*\b", r"(?:XV|FV|LV|PV|TV|HV|MOV|AOV|SDV)"),
        ("Well", r"\b(?:WELL|WELLS|WELLHEAD)\b", r"(?!)"),
    )

    def __init__(self, overrides: Mapping[str, str] | None = None) -> None:
        self.overrides = dict(overrides or {})
        if any(value not in {"KEEP", "REMOVE", "REVIEW"} for value in self.overrides.values()):
            raise ValueError("Module overrides must be KEEP, REMOVE, or REVIEW")

    def classify(self, modules: Sequence[ModuleInventoryRecord]) -> list[ModuleDecision]:
        decisions = {m.module_name: self._classify(m) for m in modules}
        groups: dict[tuple[str, str], list[ModuleInventoryRecord]] = defaultdict(list)
        for module in modules:
            # A/B/C suffixes indicate a *possible* redundant group, never a primary.
            match = re.fullmatch(r"(.*(?:PT|PIT|TT|TIT|FT|FIT|LT|LIT)[-_]?\d+)[-_]?([ABC])", module.module_name.upper())
            if match:
                groups[(module.plant_area, match.group(1))].append(module)
        for members in groups.values():
            if len(members) < 2:
                continue
            primaries = [m for m in members if re.search(r"\bPRIMARY\b", m.description.upper())]
            for module in members:
                old = decisions[module.module_name]
                if old.classification == "REMOVE":
                    continue
                if len(primaries) == 1 and decisions[primaries[0].module_name].classification == "KEEP":
                    if module != primaries[0]:
                        decisions[module.module_name] = ModuleDecision(module, "REMOVE", old.category, f"Redundant transmitter; explicit primary: {primaries[0].module_name}")
                else:
                    decisions[module.module_name] = ModuleDecision(module, "REVIEW", old.category, "Possible redundant group; primary not established")
        for name, classification in self.overrides.items():
            if name in decisions:
                old = decisions[name]
                decisions[name] = ModuleDecision(old.module, classification, old.category, "Explicit module override")
        return [decisions[m.module_name] for m in modules]

    def _classify(self, module: ModuleInventoryRecord) -> ModuleDecision:
        text = re.sub(r"[_-]+", " ", " ".join((module.module_name, module.description, module.module_class, module.module_type, module.module_subtype))).upper()
        text = re.sub(r"(?<=[A-Z])(?=\d)", " ", text)
        for pattern, reason in self.exclusions:
            if re.search(pattern, text):
                return ModuleDecision(module, "REMOVE", "", reason)
        categories = [name for name, words, tag in self.categories if re.search(words, text) or re.search(rf"(?:^|[^A-Z]){tag}(?=\d|[^A-Z]|$)", module.module_name.upper())]
        category = ", ".join(categories)
        if re.search(r"\b(?:REDUNDANT|SECONDARY|BACKUP|STANDBY|VOTING)\b", text):
            return ModuleDecision(module, "REVIEW", category, "Redundancy indicated; confirm primary before removal")
        if categories:
            return ModuleDecision(module, "KEEP", category, "Requested instrumentation category")
        return ModuleDecision(module, "REVIEW", "", "Insufficient evidence for an automatic decision")
