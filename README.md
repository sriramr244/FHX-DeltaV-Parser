# FHX Parser

Production-structured DeltaV FHX parser with CSV export, an alarm report, History report generation.

Point it at an FHX export and it writes an `output` folder beside the selected file. No DeltaV installation or database connection is needed. The export is the only input.

## Structure

- `src/fhx_tool/app.py` application composition and desktop workflow
- `src/fhx_tool/config/fhx_schema.py` FHX field, block, and output definitions
- `src/fhx_tool/domain/` typed domain records
- `src/fhx_tool/parsers/` parsing logic
- `src/fhx_tool/services/` application service layer
- `src/fhx_tool/exporters/` CSV and Excel output
- `src/fhx_tool/io/` FHX file access
- `src/fhx_tool/ui/` current Tkinter adapter and future UI boundary
- `tests/` automated tests
- `build_executable.py` Windows executable build entry point

## Output

| File | Contents |
| --- | --- |
| `_module_class.csv` | Module class header fields |
| `_module_class_attrib.csv` | Module class attribute instances |
| `_module_class_inst.csv` | Module instance header fields |
| `_module_class_inst_attrib.csv` | Module instance attribute instances |
| `_classless_module.csv` | Classless module header fields |
| `_classless_module_attrib.csv` | Classless module attribute instances |
| `_module_inventory.csv` | One row per module with controller, area, class, type, displays, last user and timestamp |
| `_history_tags.csv` | History points prepared for PI AF |
| `_module_alarm_report.xlsx` | One row per module alarm (unfiltered audit export) |
| `_filtered_module_report.xlsx` | Selected modules with linked history, matching alarms, review sheets, and filter audit |

## Alarm report

The alarm report lists every module alarm in the FHX, one row per alarm attribute, with the block and parameter that raises it and, for analog alarms, the limit, hysteresis and delay values configured against it.

Four things it handles that a plain text search does not:

- Class wiring and instance overrides are merged field by field. An instance override that only carries a priority or an enable keeps the `MONATTR` / `ALMATTR` / `LIMATTR` wiring defined on the class.
- `$` and `/` parameter paths are the same parameter. DeltaV writes `AI1/HI_LIM` on the class and `AI1$HI_LIM` on the instance.
- Paths that point inside a composite, for example `SD_BLK/SDALM/HI_LIM`, are resolved through the composite definition and its wires, so the block type and the limit are both found.
- Alarms are identified by the alarm type in the value block, not by a name ending in `_ALM`. `MAINT_REQ`, `CALIBRATION` and `PVBAD_ALM` are alarms too.

Disabled alarms are reported with `Enabled` set to FALSE rather than dropped. A limit parameter with no value anywhere in the export is left empty, which means the block is sitting at its DeltaV default.

## History export

The CSV history export includes history tag, module name, description, class, plant area, unit module, and process cell. The filtered workbook additionally includes all parsed history settings, including enable state and sample period when supplied in the FHX.

History tag format is `MODULE/HISTORY_INSTANCE.FIELD`. Class-defined history is inherited by each module instance. Instance settings override individual class properties for the same path and field; `$` and `/` paths are normalized before merging. Disabled history points remain visible with their configured enable value.

## Filtered module and history report

Every normal desktop/service run also writes `_filtered_module_report.xlsx`:

- **Modules**: retained modules, classification reason, history-point count, and a clickable link to their history rows.
- **Module History**: one row per history point belonging to a retained module, with all parsed settings.
- **Module Alarms**: alarms belonging to the same retained modules.
- **Review Modules**, **Review History**, and **Review Alarms**: ambiguous modules and their associated records for manual review.
- **Filter Audit**: every module and its KEEP / REMOVE / REVIEW decision, category, reason, and history count.

The default filter keeps power, temperature, flow, pressure, level, valve, and well-related instrumentation based on tag patterns and module description/class/type metadata. It excludes explicit signal selectors, safety/ESD/SIS systems, detectors, building fans, trip/interlock/shutdown modules, and heat tracing. Alarm descriptions are not used to exclude an otherwise relevant module.

Possible A/B/C transmitter groups are reviewed unless exactly one member is explicitly described as primary. The primary is retained and its redundant peers are excluded. A suffix alone never proves which transmitter is primary; numbered tags are not automatically treated as duplicates. Descriptions that indicate redundancy without an established primary are reviewed. Unrecognized equipment is also reviewed.

Modules without parsed history remain in the report with a zero count and **No history found in FHX**. That label does not assert that history is disabled in the live system: the supplied export may be incomplete. These reports contain historian configuration, not recorded process values or timestamps.

The original CSV and alarm outputs remain unfiltered audit exports. Use the new workbook for the shortened list. Its module, history, and alarm sheets use the same selection.

Site-specific decisions can be supplied through the service API:

```python
from fhx_tool.services.fhx_service import FhxProcessingService
from fhx_tool.services.module_filter import ModuleFilter

service = FhxProcessingService(module_filter=ModuleFilter(overrides={
    "10-PT-101A": "KEEP",   # confirmed primary
    "10-PT-101B": "REMOVE", # confirmed redundant instrument
}))
# service.process(source_file, output_directory)
```

Overrides use exact module tags and accept `KEEP`, `REMOVE`, or `REVIEW`; each is identified in the audit sheet. Review classifications against your site's naming conventions before using the shortened list.

## Running

Desktop:

```console
pip install -e .
python -m fhx_tool
```

Tests:

```console
pytest
```

Running `build_executable.py` creates a single-file windowed executable named `FHXParser` in the `dist` folder. The build script installs PyInstaller if it is not already available.

## Notes

The core parsing and service layers do not depend on Tkinter, so the UI can be replaced later without rewriting parsing logic.

`parsers/block_scanner.py` walks the file once and returns every top level block grouped by kind. Nothing calls it yet. It is there for the next step, which is generating module instances from a control strategy document rather than only reading them.
