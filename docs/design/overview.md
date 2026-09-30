# Design overview

Status: proposal for the SLAP2 working group, 2026-09-30. Decisions marked **open** need the
group.

## Goal

Bring SLAP2 processing up to Scientific Computing standards in one library. GIAnT-MATLAB is
ported to Python inside this library, GIAnT-Python is retired, and the separate MATLAB capsule
repositories are replaced by one capsule that calls this library.

## Structure

- **Steps are the primary axis:** `conversion`, `motion_correction`, `annotation`,
  `source_extraction`, `qc`, `nwb`.
- **Scan mode is dispatched inside each step**, because the algorithms differ:

  | Step | Multi-ROI raster | Band scan | Integration (voltage) |
  |---|---|---|---|
  | motion_correction | `MultiRoiRegistration` | `BandRegistration` | unsupported |
  | annotation | `annotateROIs` / `drawROIs` | band ROI annotation (GIAnT-Python) | unsupported |
  | source_extraction | `SILo` | BandSILo (GIAnT-Python `implement-bandsilo`) | unsupported: needs MBF's `Trace` backend |
  | conversion | `getImages` + `interpFrames` | `getImages` | unsupported |
  | qc, nwb | Python only | Python only | not planned yet |

- **Backends.** Every step registers implementations per `(scan_mode, backend)` in a
  `BackendRegistry`:
  - `backend=matlab` runs GIAnT-MATLAB.
  - `backend=python` runs the port.
  - `backend=both` runs both into `matlab/` and `python/` subdirectories, then runs a parity
    check.

  A step's settings, CLI and output contract stay the same whichever backend runs.
- **One capsule, one entry point.** `slap2 <step> --param=value ...` runs any step.
  - A single Code Ocean capsule repository installs this library at one pinned commit.
  - A hand-written Nextflow DSL2 pipeline calls that capsule once per step, with different CLI
    parameters (see `examples/capsule/code/run`).
  - Settings classes are top-level pydantic-settings models, so `auto-app-panel` can generate
    the app panel.
  - Failures raise, so the capsule exits non-zero.
- **Metadata.** aind-metadata-manager assembles `processing.json` and `quality_control.json`
  downstream. Each step records its code identity from:
  - the installed library version;
  - the backend's language;
  - the GIAnT-MATLAB commit, as `Code.core_dependency`, while MATLAB runs.

## MATLAB transition

| State | What runs | Default backend |
|---|---|---|
| Before | GIAnT-MATLAB via the bridge; Python owns settings, IO, QC, metadata, NWB | `matlab` |
| Transition | Per step: `both` on the reference datasets until parity passes, then `python` | per step |
| After | Python only; `matlab/`, the `.m` entry points and the MATLAB image are deleted | `python` |

**Bridge** (`matlab/bridge.py`). Python writes a JSON job file and runs `matlab -batch` or a
compiled MATLAB Runtime executable. It fails on a non-zero exit, then reads the result JSON.
- There is no `matlab.engine`, so the Python version does not depend on the MATLAB release.
- Kort Driessen's Linux fix runs trial batches in separate MATLAB processes, because memory grows
  about 550 MB per trial. Running one subprocess per (DMD, trial) batch is the general form of
  that fix, and it lets work fan out across pipeline tasks.

**Pins** (`matlab/giant.py`):
- GIAnT-MATLAB `558c1693888cc009a19b2ea1cbb86e24698b8840` on `dev`, the commit that the source
  extraction and band-scan motion correction capsules run.
- Slap2DataReader `6f458c0045a982e62eda48f7a63d9c340efcf799`.

Today's capsules use three GIAnT commits and three reader commits; this collapses them to one of
each. **Open:** which GIAnT commit is the parity reference. Output units and six SILo defaults
differ between `main` and `dev`.

**Port order.** Each step lands behind `backend=python`, gated by parity:

1. Capture MATLAB golden outputs now, at leaf-function and step level, on 2-3 small datasets.
2. `.dat` and `.meta` reading, the trial table, and frame reconstruction (`getImages`). This also
   delivers the `.dat` to `.tif` conversion tool.
3. `MultiRoiRegistration`, with its QC metrics (`registrationFailed`, `recNegErr`, motion range).
4. Applying motion correction to `.dat`. The conversion tool and SILo stage C share this step.
5. SILo localization and selection, then the SILo NMF.
6. `BandRegistration`; band SILo migrates from GIAnT-Python.
7. GUIs, on a separate track. StripRegistration (NoRMCorre, GPL) is out of scope.

**Parity tiers:**
- L0: tiny synthetic fixtures with committed MATLAB expectations, run in GitHub CI without
  MATLAB.
- L1: step parity on the reference datasets in Code Ocean (`-m data`, `-m matlab`).
- L2: end-to-end NWB comparison.

Indices and trial tables must match exactly, and interpolation must match within tight
tolerances. NMF traces are compared statistically, because Python optimizers do not reproduce
`fmincon` bit for bit. **Open:** the tolerances, which the scientists sign off.

## GIAnT-Python retirement

- Migrate the band-scan code from `implement-bandsilo` into `source_extraction` and `annotation`,
  with its tests. It is MIT-licensed, so keep its copyright notice.
- Point the production band-annotation capsule, which pins `implement-bandsilo`, at this library.
- Archive GIAnT-Python with a README pointer to this repository.
- Freeze GIAnT-MATLAB after the last step reaches parity. It stays readable as the published
  reference.
- **Needs agreement from Kaspar Podgorski and Michael Xie.** Kaspar's comment on the brief asks
  for a top-level repository that imports GIAnT, and Michael pushed to `implement-bandsilo` on
  2026-09-30.
- **Open:** visibility. This repository is internal while GIAnT-Python is public, so external
  collaborators (Kort Driessen, Peter Hogg, Adrian Negrean) lose their contribution path unless
  this repository goes public.

## Output layout (proposal)

- One derived asset per session: `motion_correction/`, `annotations/`, `source_extraction/`,
  `qc/`, and the NWB file.
- Motion correction stores transforms and compressed movies instead of float32 TIFF, which today
  is 5 to 28 times the raw size.
- For legacy sessions, source extraction writes a new `*_source-extracted_*` asset that
  references the existing motion-correction asset. It never writes into a registered prefix.

## Open decisions for the group

1. Retiring GIAnT-Python, and who owns the port (Kaspar, Michael).
2. Repository visibility for external collaborators.
3. Which GIAnT-MATLAB commit is the parity reference, and the parity tolerances.
4. The 2-3 reference datasets (GFP, SLAP2, simulation), and where parity tests run.
5. Licensing of the `.dat`/`.meta` reader: Slap2DataReader has no license and derives from MBF
   code.
6. The annotation contract for on-rig annotation before motion correction (coordinate frame and
   schema).
7. Motion-correction storage format: chunked HDF5 or OME-Zarr. The brief's "apply MC to .dat"
   deliverable also needs defining.
8. Documentation tooling: the template ships Sphinx, but the standards require MkDocs.
