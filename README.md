# slap2-processing-library

![Version](https://img.shields.io/badge/version-0.0.0-black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Interrogate](https://img.shields.io/badge/interrogate-100.0%25-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![Python](https://img.shields.io/badge/python->=3.12,<=3.13-blue?logo=python)
![support](https://img.shields.io/badge/support-supported-brightgreen) 


One Python library for all SLAP2 processing: motion correction, source extraction, QC, and
NWB packaging, for multi-ROI raster and band-scan data.

> **Status: skeleton.** Every step's settings, entry point, and scan-mode dispatch exist. The
> processing code raises `NotPortedError`, naming the GIAnT code it will port, until each port
> lands. See [docs/design/overview.md](docs/design/overview.md).

## Why this repository

- SLAP2 processing is MATLAB today (GIAnT-MATLAB inside separate Code Ocean capsules, chained by
  hand). This library ports GIAnT-MATLAB to Python step by step and becomes the single home for
  SLAP2 processing code.
- GIAnT-Python is retired: its band-scan code migrates here and GIAnT-MATLAB is frozen once every
  step passes parity.
- One library means one version, one lockfile, and one review for all steps, instead of one
  library per step.

## Layout

```
src/slap2_processing_library/
  cli.py               slap2 <step> --param=value ...   (one entry point for every step)
  steps.py             StepSettings, StepResult, errors, settings parsing
  enums.py             ScanMode, Step
  identity.py          library version for provenance
  motion_correction/   MultiRoiRegistration (raster), BandRegistration (band scan)
  source_extraction/   SILo (raster), BandSILo (band scan)
  qc/                  quality_control.json per step
  nwb/                 slap2.nwb.zarr packaging
```

Each step has `settings.py` (a pydantic-settings class, also the source of the Code Ocean app
panel), `core.py` (the processing code, dispatched on scan mode), and `job.py` (the entry point
that parses settings and calls `core.run`).

## Usage

One capsule runs any step by passing the step name first:

```bash
slap2 motion_correction --scan_mode=multi_roi_raster
slap2 source_extraction --scan_mode=band_scan --output_dir=/results
```

Each step is also installed as its own command, for example `slap2-motion-correction`.

## Installation

If you choose to clone the repository, you can install the package by running the following command from the root directory of the repository:

```bash
uv sync
```

## Development
Please test your changes using linting and testing:
```bash
uv run interrogate --verbose # Checks docstring coverage
uv run ruff check # Runs lint checks
uv run ruff format --check # Runs format checks
uv run pytest # Check tests and test coverage
```

Tests marked `data` need the reference datasets and are deselected by default; run them with
`uv run pytest -m data`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
