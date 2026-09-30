"""Settings for the source extraction step."""

from pathlib import Path

from pydantic import Field

from slap2_processing_library.steps import MatlabStepSettings


class SourceExtractionSettings(MatlabStepSettings):
    """Settings for the source extraction step."""

    analyze_hz: float = Field(default=200.0, description="Rate traces are extracted at, in Hz.")
    motion_correction_dir: Path | None = Field(
        default=None, description="Existing motion-correction output, for legacy sessions."
    )
