"""Tests for identity, shared step pieces, and the dispatcher CLI."""

import pytest

from slap2_processing_library import cli, identity
from slap2_processing_library.enums import ScanMode, Step
from slap2_processing_library.qc.job import main as qc_main
from slap2_processing_library.steps import (
    NotPortedError,
    StepSettings,
    UnsupportedScanModeError,
    parse_settings,
)


def test_library_version_is_installed() -> None:
    """The installed distribution reports a version."""
    assert identity.library_version()


def test_parse_settings_accepts_code_ocean_arguments() -> None:
    """Code Ocean style ``--name=value`` arguments parse."""
    settings = parse_settings(StepSettings, ["--scan_mode=band_scan", "--output_dir=/tmp/out"])
    assert settings.scan_mode is ScanMode.BAND_SCAN
    assert str(settings.output_dir) == "/tmp/out"


def test_errors_carry_context() -> None:
    """Errors name the step, scan mode, and reference or reason."""
    not_ported = NotPortedError(Step.MOTION_CORRECTION, ScanMode.BAND_SCAN, "BandRegistration")
    assert "BandRegistration" in str(not_ported)
    assert not_ported.reference == "BandRegistration"
    unsupported = UnsupportedScanModeError(Step.NWB, ScanMode.INTEGRATION, "not defined")
    assert unsupported.scan_mode is ScanMode.INTEGRATION
    assert "not defined" in str(unsupported)


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


def test_step_main_imports_job_module() -> None:
    """The loader returns the step's job entry point."""
    assert cli.step_main(Step.QC) is qc_main
