"""Quality-control metrics and figures, written as quality_control.json."""

from slap2_processing_library.enums import ScanMode, Step
from slap2_processing_library.qc.settings import QcSettings
from slap2_processing_library.steps import NotPortedError, StepResult, UnsupportedScanModeError

INTEGRATION_REASON = "integration-scan outputs are not defined yet"


def evaluate_multi_roi_raster(settings: QcSettings) -> StepResult:
    """Run the qc step on multi roi raster data.

    Parameters
    ----------
    settings : QcSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.QC,
        ScanMode.MULTI_ROI_RASTER,
        "the GIAnT-MATLAB ALIGNMENTDATA.h5 gates and SILo summary metrics",
    )


def evaluate_band_scan(settings: QcSettings) -> StepResult:
    """Run the qc step on band scan data.

    Parameters
    ----------
    settings : QcSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.QC,
        ScanMode.BAND_SCAN,
        "the GIAnT-MATLAB BandRegistration gates and BandSILo summary metrics",
    )


def run(settings: QcSettings) -> StepResult:
    """Run the step for the session's scan mode.

    Parameters
    ----------
    settings : QcSettings
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
        return evaluate_multi_roi_raster(settings)
    if settings.scan_mode is ScanMode.BAND_SCAN:
        return evaluate_band_scan(settings)
    raise UnsupportedScanModeError(Step.QC, settings.scan_mode, INTEGRATION_REASON)
