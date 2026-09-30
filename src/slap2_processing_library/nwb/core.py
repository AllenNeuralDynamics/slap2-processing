"""Package extracted sources and traces into slap2.nwb.zarr."""

from slap2_processing_library.enums import ScanMode, Step
from slap2_processing_library.nwb.settings import NwbSettings
from slap2_processing_library.steps import NotPortedError, StepResult, UnsupportedScanModeError

INTEGRATION_REASON = "integration-scan outputs are not defined yet"


def package_multi_roi_raster(settings: NwbSettings) -> StepResult:
    """Run the nwb step on multi roi raster data.

    Parameters
    ----------
    settings : NwbSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.NWB, ScanMode.MULTI_ROI_RASTER, "slap2_packaging_nwb")


def package_band_scan(settings: NwbSettings) -> StepResult:
    """Run the nwb step on band scan data.

    Parameters
    ----------
    settings : NwbSettings
        Validated step settings.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.NWB, ScanMode.BAND_SCAN, "slap2_packaging_nwb")


def run(settings: NwbSettings) -> StepResult:
    """Run the step for the session's scan mode.

    Parameters
    ----------
    settings : NwbSettings
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
        return package_multi_roi_raster(settings)
    if settings.scan_mode is ScanMode.BAND_SCAN:
        return package_band_scan(settings)
    raise UnsupportedScanModeError(Step.NWB, settings.scan_mode, INTEGRATION_REASON)
