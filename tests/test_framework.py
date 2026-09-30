"""Tests for enums, identity, the step framework, and the dispatcher CLI."""

from pathlib import Path

import pytest

from slap2_processing_library import cli, identity
from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.steps import (
    BackendRegistry,
    MatlabStepSettings,
    NotPortedError,
    StepResult,
    StepSettings,
    UnsupportedCombinationError,
    cli_main,
    parse_settings,
    run_matlab_step,
    run_step,
)


def make_registry() -> BackendRegistry:
    """Build a registry with fake MATLAB and Python implementations.

    Returns
    -------
    BackendRegistry
        Registry for the motion-correction step.
    """
    registry = BackendRegistry(Step.MOTION_CORRECTION)
    for backend in (Backend.MATLAB, Backend.PYTHON):

        @registry.register(ScanMode.MULTI_ROI_RASTER, backend)
        def implementation(
            settings: StepSettings, output_dir: Path, backend: Backend = backend
        ) -> StepResult:
            """Return a result without doing work.

            Parameters
            ----------
            settings : StepSettings
                Settings.
            output_dir : Path
                Output directory.
            backend : Backend
                Backend being faked.

            Returns
            -------
            StepResult
                Empty result.
            """
            return StepResult(Step.MOTION_CORRECTION, settings.scan_mode, backend, output_dir)

    registry.mark_unsupported(ScanMode.INTEGRATION, "no Trace backend")
    return registry


def test_library_version_is_installed() -> None:
    """The installed distribution reports a version."""
    assert identity.library_version()


def test_registry_rejects_both_and_duplicates() -> None:
    """``both`` is composed, and a combination registers once."""
    registry = make_registry()
    with pytest.raises(ValueError, match="composed"):
        registry.register(ScanMode.BAND_SCAN, Backend.BOTH)
    with pytest.raises(ValueError, match="already"):
        registry.register(ScanMode.MULTI_ROI_RASTER, Backend.MATLAB)
    assert registry.supported() == [
        (ScanMode.MULTI_ROI_RASTER, Backend.MATLAB),
        (ScanMode.MULTI_ROI_RASTER, Backend.PYTHON),
    ]


def test_resolve_reports_unsupported_and_missing() -> None:
    """Unsupported and unregistered combinations raise with a reason."""
    registry = make_registry()
    with pytest.raises(UnsupportedCombinationError, match="no Trace backend"):
        registry.resolve(ScanMode.INTEGRATION, Backend.MATLAB)
    with pytest.raises(UnsupportedCombinationError, match="no python implementation"):
        registry.resolve(ScanMode.BAND_SCAN, Backend.PYTHON)


def test_run_step_single_and_both(tmp_path: Path) -> None:
    """A single backend writes to output_dir; both write to subdirectories and compare."""
    registry = make_registry()
    single = run_step(StepSettings(output_dir=tmp_path), registry)
    assert [result.output_dir for result in single] == [tmp_path]

    compared: list[tuple[StepResult, StepResult]] = []

    def parity(matlab: StepResult, python: StepResult) -> Path:
        """Record the comparison.

        Parameters
        ----------
        matlab : StepResult
            MATLAB result.
        python : StepResult
            Python result.

        Returns
        -------
        Path
            Fake report path.
        """
        compared.append((matlab, python))
        return tmp_path / "parity.json"

    both = StepSettings(output_dir=tmp_path, backend=Backend.BOTH)
    results = run_step(both, registry, parity)
    assert [result.output_dir.name for result in results] == ["matlab", "python"]
    assert len(compared) == 1
    with pytest.raises(UnsupportedCombinationError, match="parity"):
        run_step(both, registry)


def test_parse_settings_and_cli_main(tmp_path: Path) -> None:
    """Code Ocean style ``--name=value`` arguments parse and run."""
    settings = parse_settings(StepSettings, ["--scan_mode=band_scan", "--backend=python"])
    assert (settings.scan_mode, settings.backend) == (ScanMode.BAND_SCAN, Backend.PYTHON)
    results = cli_main(StepSettings, make_registry(), [f"--output_dir={tmp_path}"])
    assert results[0].backend is Backend.MATLAB


def test_not_ported_error_names_matlab_reference() -> None:
    """The error points at the GIAnT-MATLAB function being ported."""
    error = NotPortedError(Step.MOTION_CORRECTION, ScanMode.BAND_SCAN, "BandRegistration")
    assert "BandRegistration" in str(error)
    assert error.matlab_reference == "BandRegistration"


def test_run_matlab_step(tmp_path: Path, fake_runner: object) -> None:
    """The MATLAB helper verifies pins, runs the job, and lists outputs."""
    settings = MatlabStepSettings(output_dir=tmp_path)
    result = run_matlab_step(
        settings, Step.MOTION_CORRECTION, tmp_path, "slap2_run_motion_correction", fake_runner
    )
    assert result.outputs == (Path("out.h5"),)
    assert result.backend is Backend.MATLAB


def test_dispatcher(monkeypatch: pytest.MonkeyPatch) -> None:
    """``slap2 <step>`` loads only that step and forwards the remaining arguments."""
    with pytest.raises(SystemExit, match="usage"):
        cli.main([])
    with pytest.raises(SystemExit, match="usage"):
        cli.main(["segmentation"])
    seen: list[list[str]] = []
    monkeypatch.setattr(cli, "step_main", lambda step: seen.append)
    monkeypatch.setattr("sys.argv", ["slap2", "nwb", "--scan_mode=band_scan"])
    cli.main()
    assert seen == [["--scan_mode=band_scan"]]


def test_step_main_imports_step_module() -> None:
    """The real loader returns the step's main function."""
    from slap2_processing_library.qc.cli import main

    assert cli.step_main(Step.QC) is main
