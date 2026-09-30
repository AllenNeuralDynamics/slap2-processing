"""Backend registry for the motion correction step."""

from pathlib import Path

from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.motion_correction.settings import MotionCorrectionSettings
from slap2_processing_library.steps import (
    BackendRegistry,
    NotPortedError,
    StepResult,
    run_matlab_step,
)

REGISTRY = BackendRegistry(Step.MOTION_CORRECTION)
REGISTRY.mark_unsupported(
    ScanMode.INTEGRATION,
    "integration (voltage) extraction needs the MBF slap2 Trace backend, which is not available",
)


@REGISTRY.register(ScanMode.MULTI_ROI_RASTER, Backend.PYTHON)
def python_multi_roi_raster(settings: MotionCorrectionSettings, output_dir: Path) -> StepResult:
    """Run the Python port for multi roi raster data.

    Parameters
    ----------
    settings : MotionCorrectionSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.MOTION_CORRECTION, ScanMode.MULTI_ROI_RASTER, "MultiRoiRegistration")


@REGISTRY.register(ScanMode.BAND_SCAN, Backend.PYTHON)
def python_band_scan(settings: MotionCorrectionSettings, output_dir: Path) -> StepResult:
    """Run the Python port for band scan data.

    Parameters
    ----------
    settings : MotionCorrectionSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.MOTION_CORRECTION, ScanMode.BAND_SCAN, "BandRegistration")


@REGISTRY.register(ScanMode.MULTI_ROI_RASTER, Backend.MATLAB)
def matlab_multi_roi_raster(settings: MotionCorrectionSettings, output_dir: Path) -> StepResult:
    """Run GIAnT-MATLAB for multi roi raster data.

    Parameters
    ----------
    settings : MotionCorrectionSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Returns
    -------
    StepResult
        Outputs listed by the MATLAB entry point.
    """
    return run_matlab_step(
        settings, Step.MOTION_CORRECTION, output_dir, "slap2_run_motion_correction"
    )


@REGISTRY.register(ScanMode.BAND_SCAN, Backend.MATLAB)
def matlab_band_scan(settings: MotionCorrectionSettings, output_dir: Path) -> StepResult:
    """Run GIAnT-MATLAB for band scan data.

    Parameters
    ----------
    settings : MotionCorrectionSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Returns
    -------
    StepResult
        Outputs listed by the MATLAB entry point.
    """
    return run_matlab_step(
        settings, Step.MOTION_CORRECTION, output_dir, "slap2_run_motion_correction"
    )
