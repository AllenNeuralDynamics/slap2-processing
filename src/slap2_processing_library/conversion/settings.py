"""Settings for the conversion step."""

from pydantic import Field

from slap2_processing_library.enums import Backend
from slap2_processing_library.steps import StepSettings


class ConversionSettings(StepSettings):
    """Settings for the conversion step."""

    backend: Backend = Field(
        default=Backend.PYTHON, description="Implementation to run; this step is Python only."
    )
    target_format: str = Field(default="tif", description="Output format: tif or h5.")
    apply_motion_correction: bool = Field(
        default=False, description="Apply motion-correction transforms before writing."
    )
