"""Settings for the qc step."""

from pydantic import Field

from slap2_processing_library.enums import Backend
from slap2_processing_library.steps import StepSettings


class QcSettings(StepSettings):
    """Settings for the qc step."""

    backend: Backend = Field(
        default=Backend.PYTHON, description="Implementation to run; this step is Python only."
    )
