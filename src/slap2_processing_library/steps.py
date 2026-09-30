"""Shared pieces of every step: settings base, result, errors, and settings parsing.

Each step package has ``settings.py`` (its settings class), ``core.py`` (the processing code,
dispatched on scan mode), and ``job.py`` (the entry point that parses settings and calls
``core.run``). Code Ocean capsules and pipeline tasks call the entry points.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from slap2_processing_library.enums import ScanMode, Step

DEFAULT_INPUT_DIR = Path("/data")
DEFAULT_OUTPUT_DIR = Path("/results")


class StepSettings(BaseSettings):
    """Settings shared by every step.

    Subclasses are defined at module top level in ``<step>/settings.py`` so that
    ``auto-app-panel`` can generate Code Ocean app panels from them. Field names use
    underscores and are never a single character.
    """

    model_config = SettingsConfigDict(env_prefix="SLAP2_", extra="forbid")

    input_dir: Path = Field(
        default=DEFAULT_INPUT_DIR, description="Directory holding the step's input assets."
    )
    output_dir: Path = Field(
        default=DEFAULT_OUTPUT_DIR, description="Directory the step writes its outputs to."
    )
    scan_mode: ScanMode = Field(
        default=ScanMode.MULTI_ROI_RASTER, description="SLAP2 scan mode of the session."
    )


@dataclass(frozen=True)
class StepResult:
    """Outcome of one step run.

    Attributes
    ----------
    step : Step
        Step that ran.
    scan_mode : ScanMode
        Scan mode the step ran for.
    output_dir : Path
        Directory holding the outputs.
    outputs : tuple of Path
        Files the step wrote, relative to ``output_dir``.
    """

    step: Step
    scan_mode: ScanMode
    output_dir: Path
    outputs: tuple[Path, ...] = ()


class NotPortedError(NotImplementedError):
    """Raised by processing code whose port has not landed yet.

    Parameters
    ----------
    step : Step
        Step that was requested.
    scan_mode : ScanMode
        Scan mode that was requested.
    reference : str
        Existing code the port reproduces, for example GIAnT-MATLAB ``MultiRoiRegistration``.
    """

    def __init__(self, step: Step, scan_mode: ScanMode, reference: str) -> None:
        """Build the message from the step, scan mode, and reference."""
        super().__init__(
            f"{step} for {scan_mode} is not implemented yet. It will port {reference}. "
            "See docs/design/overview.md."
        )
        self.step = step
        self.scan_mode = scan_mode
        self.reference = reference


class UnsupportedScanModeError(ValueError):
    """Raised when a step does not support a scan mode.

    Parameters
    ----------
    step : Step
        Step that was requested.
    scan_mode : ScanMode
        Scan mode that is not supported.
    reason : str
        Why the scan mode is not supported.
    """

    def __init__(self, step: Step, scan_mode: ScanMode, reason: str) -> None:
        """Build the message from the step, scan mode, and reason."""
        super().__init__(f"{step} does not support {scan_mode}: {reason}")
        self.step = step
        self.scan_mode = scan_mode


def parse_settings[SettingsT: StepSettings](
    settings_class: type[SettingsT], argv: Sequence[str] | None = None
) -> SettingsT:
    """Build step settings from command-line arguments and ``SLAP2_`` environment variables.

    Parameters
    ----------
    settings_class : type
        Step settings class to build.
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    StepSettings
        Validated settings instance.
    """
    cli_args: bool | list[str] = True if argv is None else list(argv)
    return settings_class(_cli_parse_args=cli_args)
