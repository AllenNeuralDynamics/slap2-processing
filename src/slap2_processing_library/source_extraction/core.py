"""Source localization and trace extraction."""

from slap2_processing_library.enums import ScanMode, Step
from slap2_processing_library.source_extraction.settings import SourceExtractionSettings
from slap2_processing_library.steps import NotPortedError, StepResult, UnsupportedScanModeError

INTEGRATION_REASON = (
    "integration (voltage) extraction needs the MBF slap2 Trace backend, which is not available"
)


def extract_multi_roi_raster(settings: SourceExtractionSettings) -> StepResult:
    """Run the source extraction step on multi roi raster data.

    Parameters
    ----------
    settings : SourceExtractionSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.SOURCE_EXTRACTION, ScanMode.MULTI_ROI_RASTER, "GIAnT-MATLAB SILo")


def extract_band_scan(settings: SourceExtractionSettings) -> StepResult:
    """Run the source extraction step on band scan data.

    Parameters
    ----------
    settings : SourceExtractionSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.SOURCE_EXTRACTION, ScanMode.BAND_SCAN, "GIAnT-Python BandSILo (implement-bandsilo)"
    )


def run(settings: SourceExtractionSettings) -> StepResult:
    """Run the step for the session's scan mode.

    Parameters
    ----------
    settings : SourceExtractionSettings
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
        return extract_multi_roi_raster(settings)
    if settings.scan_mode is ScanMode.BAND_SCAN:
        return extract_band_scan(settings)
    raise UnsupportedScanModeError(Step.SOURCE_EXTRACTION, settings.scan_mode, INTEGRATION_REASON)
