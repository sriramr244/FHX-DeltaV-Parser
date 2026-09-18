# FHX Parser

Production-structured DeltaV FHX parser with CSV export, an alarm report, and PI AF preparation metadata.

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
| `Module_class.csv` | Module class header fields |
| `Module_class_attrib.csv` | Module class attribute instances |
| `Module_class_inst.csv` | Module instance header fields |
| `Module_class_inst_attrib.csv` | Module instance attribute instances |
| `Classless_module.csv` | Classless module header fields |
| `Classless_module_attrib.csv` | Classless module attribute instances |
| `Module_inventory.csv` | One row per module with controller, area, class, type, displays, last user and timestamp |
| `History_tags.csv` | History points prepared for PI AF |
| `Module_alarm_report.xlsx` | One row per module alarm |

## Alarm report

The alarm report lists every module alarm in the FHX, one row per alarm attribute, with the block and parameter that raises it and, for analog alarms, the limit, hysteresis and delay values configured against it.

Four things it handles that a plain text search does not:

- Class wiring and instance overrides are merged field by field. An instance override that only carries a priority or an enable keeps the `MONATTR` / `ALMATTR` / `LIMATTR` wiring defined on the class.
- `$` and `/` parameter paths are the same parameter. DeltaV writes `AI1/HI_LIM` on the class and `AI1$HI_LIM` on the instance.
- Paths that point inside a composite, for example `SD_BLK/SDALM/HI_LIM`, are resolved through the composite definition and its wires, so the block type and the limit are both found.
- Alarms are identified by the alarm type in the value block, not by a name ending in `_ALM`. `MAINT_REQ`, `CALIBRATION` and `PVBAD_ALM` are alarms too.

Disabled alarms are reported with `Enabled` set to FALSE rather than dropped. A limit parameter with no value anywhere in the export is left empty, which means the block is sitting at its DeltaV default.

## History export

The history export includes history tag, module name, module description, module class, unit module, process cell, AF element path, history instance, and field.

History tag format is `MODULE/HISTORY_INSTANCE.FIELD`.

## Running

Desktop:

```
python -m fhx_tool
```

Tests:

```
pytest
```

Running `build_executable.py` creates a single-file windowed executable named `FHXParser` in the `dist` folder. The build script installs PyInstaller if it is not already available.

## Notes

The core parsing and service layers do not depend on Tkinter, so the UI can be replaced later without rewriting parsing logic.

`parsers/block_scanner.py` walks the file once and returns every top level block grouped by kind. Nothing calls it yet. It is there for the next step, which is generating module instances from a control strategy document rather than only reading them.

Reference run, a 13 MB single-area export: 511 modules, 343 history points, 3370 alarms across 492 modules, about three and a half seconds end to end.
