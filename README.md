# FHX Parser

Production-structured DeltaV FHX parser with CSV export and PI AF preparation metadata.

## Structure

- `src/fhx_tool/app.py` application composition and desktop workflow
- `src/fhx_tool/config/fhx_schema.py` FHX field, header, and output definitions
- `src/fhx_tool/domain/` typed domain records
- `src/fhx_tool/parsers/` parsing logic
- `src/fhx_tool/services/` application service layer
- `src/fhx_tool/exporters/` CSV output
- `src/fhx_tool/io/` FHX file access
- `src/fhx_tool/ui/` current Tkinter adapter and future UI boundary
- `tests/` automated tests
- `build_executable.py` Windows executable build entry point

The desktop application writes an `output` folder beside the selected FHX file.

The history export includes history tag, module name, module description, module class, unit module, process cell, AF element path, history instance, and field.

History tag format is `MODULE/HISTORY_INSTANCE.FIELD`.

The core parsing and service layers do not depend on Tkinter, so the UI can be replaced later without rewriting parsing logic.

Running `build_executable.py` creates a single-file windowed executable named `FHXParser` in the `dist` folder. The build script installs PyInstaller if it is not already available.
