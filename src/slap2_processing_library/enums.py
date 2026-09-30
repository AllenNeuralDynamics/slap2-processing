"""Enumerations shared by every processing step."""

from enum import StrEnum


class ScanMode(StrEnum):
    """SLAP2 acquisition scan modes.

    Steps dispatch on the scan mode because the algorithms differ: multi-ROI raster data is
    registered frame by frame, band-scan data is registered against a reference-stack lookup
    table, and integration (voltage) data needs extraction code that is not available yet.
    """

    MULTI_ROI_RASTER = "multi_roi_raster"
    BAND_SCAN = "band_scan"
    INTEGRATION = "integration"


class Step(StrEnum):
    """Processing steps provided by the library."""

    MOTION_CORRECTION = "motion_correction"
    SOURCE_EXTRACTION = "source_extraction"
    QC = "qc"
    NWB = "nwb"
