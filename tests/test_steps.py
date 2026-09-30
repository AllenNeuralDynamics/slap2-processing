"""Tests that every step registers its backends and CLI."""

from importlib import import_module
from pathlib import Path

import pytest

from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.steps import NotPortedError, UnsupportedCombinationError

MATLAB_STEPS = (Step.MOTION_CORRECTION, Step.ANNOTATION, Step.SOURCE_EXTRACTION)
PORTED_MODES = (ScanMode.MULTI_ROI_RASTER, ScanMode.BAND_SCAN)


@pytest.mark.parametrize("step", list(Step))
@pytest.mark.parametrize("scan_mode", PORTED_MODES)
def test_python_backend_is_stubbed(step: Step, scan_mode: ScanMode, tmp_path: Path) -> None:
    """Every Python backend raises until its port lands, through the step CLI."""
    cli = import_module(f"slap2_processing_library.{step.value}.cli")
    with pytest.raises(NotPortedError):
        cli.main([f"--scan_mode={scan_mode}", "--backend=python", f"--output_dir={tmp_path}"])


@pytest.mark.parametrize("step", MATLAB_STEPS)
@pytest.mark.parametrize("scan_mode", PORTED_MODES)
def test_matlab_backend_runs_bridge(
    step: Step, scan_mode: ScanMode, tmp_path: Path, fake_runner: object, monkeypatch: object
) -> None:
    """MATLAB-backed steps call the bridge with their entry point."""
    backends = import_module(f"slap2_processing_library.{step.value}.backends")
    settings_module = import_module(f"slap2_processing_library.{step.value}.settings")
    settings_class = next(
        value
        for name, value in vars(settings_module).items()
        if name.endswith("Settings") and value.__module__ == settings_module.__name__
    )
    settings = settings_class(scan_mode=scan_mode, output_dir=tmp_path)
    captured: dict[str, object] = {}

    def fake(settings_arg: object, step_arg: Step, output_dir: Path, entry_point: str) -> str:
        """Capture the call.

        Parameters
        ----------
        settings_arg : object
            Settings.
        step_arg : Step
            Step.
        output_dir : Path
            Output directory.
        entry_point : str
            MATLAB entry point.

        Returns
        -------
        str
            Marker.
        """
        captured.update(step=step_arg, entry_point=entry_point)
        return "ran"

    monkeypatch.setattr(backends, "run_matlab_step", fake)
    implementation = backends.REGISTRY.resolve(scan_mode, Backend.MATLAB)
    assert implementation(settings, tmp_path) == "ran"
    assert captured["step"] is step
    entry = Path(backends.__file__).parents[1] / "matlab/entry_points"
    assert (entry / f"{captured['entry_point']}.m").is_file()


@pytest.mark.parametrize("step", [s for s in Step if s not in (Step.QC, Step.NWB)])
def test_integration_is_unsupported(step: Step) -> None:
    """Integration scans are refused with the blocking reason."""
    backends = import_module(f"slap2_processing_library.{step.value}.backends")
    with pytest.raises(UnsupportedCombinationError, match="Trace"):
        backends.REGISTRY.resolve(ScanMode.INTEGRATION, Backend.PYTHON)
