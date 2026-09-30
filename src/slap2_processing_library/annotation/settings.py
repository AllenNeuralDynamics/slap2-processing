"""Settings for the annotation step."""

from pathlib import Path

from pydantic import Field

from slap2_processing_library.steps import MatlabStepSettings


class AnnotationSettings(MatlabStepSettings):
    """Settings for the annotation step."""

    annotation_file: Path | None = Field(
        default=None, description="Existing annotations.h5 to validate instead of drawing."
    )
