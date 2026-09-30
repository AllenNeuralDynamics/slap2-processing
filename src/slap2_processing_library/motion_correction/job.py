"""Entry point for the motion correction step."""

from collections.abc import Sequence

from slap2_processing_library.motion_correction.core import run
from slap2_processing_library.motion_correction.settings import MotionCorrectionSettings
from slap2_processing_library.steps import StepResult, parse_settings


def main(argv: Sequence[str] | None = None) -> StepResult:
    """Run the motion correction step from command-line arguments.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    StepResult
        Outputs of the step.
    """
    return run(parse_settings(MotionCorrectionSettings, argv))
