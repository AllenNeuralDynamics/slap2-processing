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


class Backend(StrEnum):
    """Implementation that performs a step's numerical work.

    ``matlab`` runs the pinned GIAnT-MATLAB code, ``python`` runs this library's port, and
    ``both`` runs the two and compares their outputs with the parity checks.
    """

    MATLAB = "matlab"
    PYTHON = "python"
    BOTH = "both"


class Step(StrEnum):
    """Processing steps provided by the library."""

    CONVERSION = "conversion"
    MOTION_CORRECTION = "motion_correction"
    ANNOTATION = "annotation"
    SOURCE_EXTRACTION = "source_extraction"
    QC = "qc"
    NWB = "nwb"
