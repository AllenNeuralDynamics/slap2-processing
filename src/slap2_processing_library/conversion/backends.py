"""Backend registry for the conversion step."""

from pathlib import Path

from slap2_processing_library.conversion.settings import ConversionSettings
from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.steps import BackendRegistry, NotPortedError, StepResult

REGISTRY = BackendRegistry(Step.CONVERSION)
REGISTRY.mark_unsupported(
    ScanMode.INTEGRATION,
    "integration (voltage) extraction needs the MBF slap2 Trace backend, which is not available",
)


@REGISTRY.register(ScanMode.MULTI_ROI_RASTER, Backend.PYTHON)
def python_multi_roi_raster(settings: ConversionSettings, output_dir: Path) -> StepResult:
    """Run the Python port for multi roi raster data.

    Parameters
    ----------
    settings : ConversionSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.CONVERSION, ScanMode.MULTI_ROI_RASTER, "getImages (Slap2DataReader) + interpFrames"
    )


@REGISTRY.register(ScanMode.BAND_SCAN, Backend.PYTHON)
def python_band_scan(settings: ConversionSettings, output_dir: Path) -> StepResult:
    """Run the Python port for band scan data.

    Parameters
    ----------
    settings : ConversionSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.CONVERSION, ScanMode.BAND_SCAN, "getImages (Slap2DataReader)")
