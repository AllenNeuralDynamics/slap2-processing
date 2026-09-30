"""Backend registry for the qc step."""

from pathlib import Path

from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.qc.settings import QcSettings
from slap2_processing_library.steps import BackendRegistry, NotPortedError, StepResult

REGISTRY = BackendRegistry(Step.QC)


@REGISTRY.register(ScanMode.MULTI_ROI_RASTER, Backend.PYTHON)
def python_multi_roi_raster(settings: QcSettings, output_dir: Path) -> StepResult:
    """Run the Python port for multi roi raster data.

    Parameters
    ----------
    settings : QcSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.QC, ScanMode.MULTI_ROI_RASTER, "ALIGNMENTDATA.h5 gates and SILo summary metrics"
    )


@REGISTRY.register(ScanMode.BAND_SCAN, Backend.PYTHON)
def python_band_scan(settings: QcSettings, output_dir: Path) -> StepResult:
    """Run the Python port for band scan data.

    Parameters
    ----------
    settings : QcSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.QC, ScanMode.BAND_SCAN, "ALIGNMENTDATA.h5 gates and BandSILo summary metrics"
    )
