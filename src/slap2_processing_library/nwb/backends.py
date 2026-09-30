"""Backend registry for the nwb step."""

from pathlib import Path

from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.nwb.settings import NwbSettings
from slap2_processing_library.steps import BackendRegistry, NotPortedError, StepResult

REGISTRY = BackendRegistry(Step.NWB)


@REGISTRY.register(ScanMode.MULTI_ROI_RASTER, Backend.PYTHON)
def python_multi_roi_raster(settings: NwbSettings, output_dir: Path) -> StepResult:
    """Run the Python port for multi roi raster data.

    Parameters
    ----------
    settings : NwbSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.NWB, ScanMode.MULTI_ROI_RASTER, "slap2_packaging_nwb")


@REGISTRY.register(ScanMode.BAND_SCAN, Backend.PYTHON)
def python_band_scan(settings: NwbSettings, output_dir: Path) -> StepResult:
    """Run the Python port for band scan data.

    Parameters
    ----------
    settings : NwbSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.NWB, ScanMode.BAND_SCAN, "slap2_packaging_nwb")
