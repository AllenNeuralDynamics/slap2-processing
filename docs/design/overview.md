# Design overview

Status: proposal for the SLAP2 working group, 2026-09-30. Decisions marked **open** need the
group.

## Goal

Bring SLAP2 processing up to Scientific Computing standards in one library. GIAnT-MATLAB is
ported to Python inside this library, GIAnT-Python is retired, and the separate MATLAB capsule
repositories are replaced by one capsule that calls this library.

## Structure

- **Steps are the primary axis:** `motion_correction`, `source_extraction`, `qc`, `nwb`.
  Annotation (manual ROI drawing) is an input to source extraction, not a step, and the
  `.dat` to `.tif` conversion tool is deferred.
- **Scan mode is dispatched inside each step**, because the algorithms differ:

  | Step | Multi-ROI raster | Band scan | Integration (voltage) |
  |---|---|---|---|
  | motion_correction | `MultiRoiRegistration` | `BandRegistration` | unsupported |
  | source_extraction | `SILo` | BandSILo (GIAnT-Python `implement-bandsilo`) | unsupported: needs MBF's `Trace` backend |
  | qc, nwb | Python only | Python only | not planned yet |

- **Per-step files.** `settings.py` holds the step's settings class, `core.py` holds the
  processing code and its `run` function (which dispatches on scan mode), and `job.py` is the
  entry point that parses settings and calls `core.run`.
- **One capsule, one entry point.** `slap2 <step> --param=value ...` runs any step.
  - A single Code Ocean capsule repository installs this library at one pinned commit.
  - A hand-written Nextflow DSL2 pipeline calls that capsule once per step, with different CLI
    parameters, for example `slap2 motion_correction --scan_mode=band_scan`.
  - Settings classes are top-level pydantic-settings models, so `auto-app-panel` can generate
    the app panel.
  - Failures raise, so the capsule exits non-zero.
- **Metadata.** aind-metadata-manager assembles `processing.json` and `quality_control.json`
  downstream. Each step records its code identity from:
  - the installed library version;
  - the library's repository URL.

## Porting GIAnT-MATLAB

This library never runs MATLAB. Production keeps running the existing GIAnT-MATLAB capsules until
each step's Python port lands here and passes parity, then the pipeline switches that step to
this library.

| State | Production runs | This library |
|---|---|---|
| Before | GIAnT-MATLAB capsules, as today | stubs raise `NotPortedError` |
| Transition | per step: this library once its port passes parity, MATLAB capsules otherwise | ported steps implemented |
| After | this library only; GIAnT-MATLAB frozen, MATLAB capsules retired | all steps implemented |

**Port order:**

1. Capture MATLAB golden outputs now, while the license exists, at leaf-function and step level,
   on 2-3 small datasets. They are generated with GIAnT-MATLAB outside this library and stored as
   versioned data assets.
2. `.dat` and `.meta` reading, the trial table, and frame reconstruction (`getImages`).
3. `MultiRoiRegistration`, with its QC metrics (`registrationFailed`, `recNegErr`, motion range).
4. Applying motion correction to `.dat`, which SILo stage C needs.
5. SILo localization and selection, then the SILo NMF.
6. `BandRegistration`; band SILo migrates from GIAnT-Python.
7. GUIs, on a separate track. StripRegistration (NoRMCorre, GPL) is out of scope.

**Parity tiers** (Python output against the stored MATLAB golden outputs):
- L0: tiny synthetic fixtures with committed MATLAB expectations, run in GitHub CI.
- L1: step parity on the reference datasets in Code Ocean (`-m data`).
- L2: end-to-end NWB comparison.

Indices and trial tables must match exactly, and interpolation must match within tight
tolerances. NMF traces are compared statistically, because Python optimizers do not reproduce
`fmincon` bit for bit. **Open:** the tolerances, which the scientists sign off. Per-(DMD, trial)
entry points let the pipeline fan work out across tasks, which also removes the memory growth
that Kort Driessen's Linux fix works around.

## GIAnT-Python retirement

- Migrate the band-scan code from `implement-bandsilo` into `source_extraction`,
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
