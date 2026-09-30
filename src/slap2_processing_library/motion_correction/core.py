"""Rigid motion correction of SLAP2 dynamic data."""

from slap2_processing_library.enums import ScanMode, Step
from slap2_processing_library.motion_correction.settings import MotionCorrectionSettings
from slap2_processing_library.steps import NotPortedError, StepResult, UnsupportedScanModeError

INTEGRATION_REASON = (
    "integration (voltage) extraction needs the MBF slap2 Trace backend, which is not available"
)


def register_multi_roi_raster(settings: MotionCorrectionSettings) -> StepResult:
    """Run the motion correction step on multi roi raster data.

    Parameters
    ----------
    settings : MotionCorrectionSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.MOTION_CORRECTION, ScanMode.MULTI_ROI_RASTER, "GIAnT-MATLAB MultiRoiRegistration"
    )


def register_band_scan(settings: MotionCorrectionSettings) -> StepResult:
    """Run the motion correction step on band scan data.

    Parameters
    ----------
    settings : MotionCorrectionSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.MOTION_CORRECTION, ScanMode.BAND_SCAN, "GIAnT-MATLAB BandRegistration"
    )


def run(settings: MotionCorrectionSettings) -> StepResult:
    """Run the step for the session's scan mode.

    Parameters
    ----------
    settings : MotionCorrectionSettings
        Validated step settings.

    Returns
    -------
    StepResult
        Outputs of the step.

    Raises
    ------
    UnsupportedScanModeError
        For integration scans.
    """
    if settings.scan_mode is ScanMode.MULTI_ROI_RASTER:
        return register_multi_roi_raster(settings)
    if settings.scan_mode is ScanMode.BAND_SCAN:
        return register_band_scan(settings)
    raise UnsupportedScanModeError(Step.MOTION_CORRECTION, settings.scan_mode, INTEGRATION_REASON)
