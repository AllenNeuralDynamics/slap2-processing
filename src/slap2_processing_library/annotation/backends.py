"""Backend registry for the annotation step."""

from pathlib import Path

from slap2_processing_library.annotation.settings import AnnotationSettings
from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.steps import (
    BackendRegistry,
    NotPortedError,
    StepResult,
    run_matlab_step,
)

REGISTRY = BackendRegistry(Step.ANNOTATION)
REGISTRY.mark_unsupported(
    ScanMode.INTEGRATION,
    "integration (voltage) extraction needs the MBF slap2 Trace backend, which is not available",
)


@REGISTRY.register(ScanMode.MULTI_ROI_RASTER, Backend.PYTHON)
def python_multi_roi_raster(settings: AnnotationSettings, output_dir: Path) -> StepResult:
    """Run the Python port for multi roi raster data.

    Parameters
    ----------
    settings : AnnotationSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(Step.ANNOTATION, ScanMode.MULTI_ROI_RASTER, "annotateROIs / drawROIs")


@REGISTRY.register(ScanMode.BAND_SCAN, Backend.PYTHON)
def python_band_scan(settings: AnnotationSettings, output_dir: Path) -> StepResult:
    """Run the Python port for band scan data.

    Parameters
    ----------
    settings : AnnotationSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Raises
    ------
    NotPortedError
        Until the port lands.
    """
    raise NotPortedError(
        Step.ANNOTATION,
        ScanMode.BAND_SCAN,
        "band ROI annotation (from GIAnT-Python implement-bandsilo)",
    )


@REGISTRY.register(ScanMode.MULTI_ROI_RASTER, Backend.MATLAB)
def matlab_multi_roi_raster(settings: AnnotationSettings, output_dir: Path) -> StepResult:
    """Run GIAnT-MATLAB for multi roi raster data.

    Parameters
    ----------
    settings : AnnotationSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Returns
    -------
    StepResult
        Outputs listed by the MATLAB entry point.
    """
    return run_matlab_step(settings, Step.ANNOTATION, output_dir, "slap2_run_annotation")


@REGISTRY.register(ScanMode.BAND_SCAN, Backend.MATLAB)
def matlab_band_scan(settings: AnnotationSettings, output_dir: Path) -> StepResult:
    """Run GIAnT-MATLAB for band scan data.

    Parameters
    ----------
    settings : AnnotationSettings
        Validated step settings.
    output_dir : Path
        Directory for the outputs.

    Returns
    -------
    StepResult
        Outputs listed by the MATLAB entry point.
    """
    return run_matlab_step(settings, Step.ANNOTATION, output_dir, "slap2_run_annotation")
