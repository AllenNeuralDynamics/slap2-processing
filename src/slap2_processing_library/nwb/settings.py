"""Settings for the nwb step."""

from pydantic import Field

from slap2_processing_library.enums import Backend
from slap2_processing_library.steps import StepSettings


class NwbSettings(StepSettings):
    """Settings for the nwb step."""

    backend: Backend = Field(
        default=Backend.PYTHON, description="Implementation to run; this step is Python only."
    )
