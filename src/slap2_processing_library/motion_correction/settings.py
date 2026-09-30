"""Settings for the motion correction step."""

from pydantic import Field

from slap2_processing_library.steps import MatlabStepSettings


class MotionCorrectionSettings(MatlabStepSettings):
    """Settings for the motion correction step."""

    align_hz: float = Field(default=80.0, description="Rate of the motion estimate, in Hz.")
    max_shift_px: int = Field(default=40, description="Largest shift searched, in pixels.")
