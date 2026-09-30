"""Tests that every step dispatches on scan mode through its job entry point."""

from importlib import import_module
from pathlib import Path

import pytest

from slap2_processing_library.enums import ScanMode, Step
from slap2_processing_library.steps import NotPortedError, UnsupportedScanModeError

PLANNED_MODES = (ScanMode.MULTI_ROI_RASTER, ScanMode.BAND_SCAN)


@pytest.mark.parametrize("step", list(Step))
@pytest.mark.parametrize("scan_mode", PLANNED_MODES)
def test_planned_modes_are_stubbed(step: Step, scan_mode: ScanMode, tmp_path: Path) -> None:
    """Every planned scan mode raises until its port lands."""
    job = import_module(f"slap2_processing_library.{step.value}.job")
    with pytest.raises(NotPortedError) as raised:
        job.main([f"--scan_mode={scan_mode}", f"--output_dir={tmp_path}"])
    assert (raised.value.step, raised.value.scan_mode) == (step, scan_mode)


@pytest.mark.parametrize("step", list(Step))
def test_integration_is_unsupported(step: Step) -> None:
    """Integration scans are refused with a reason."""
    job = import_module(f"slap2_processing_library.{step.value}.job")
    with pytest.raises(UnsupportedScanModeError, match="integration"):
        job.main(["--scan_mode=integration"])
