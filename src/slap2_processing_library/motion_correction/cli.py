"""Command-line entry point for the motion correction step."""

from collections.abc import Sequence

from slap2_processing_library.motion_correction.backends import REGISTRY
from slap2_processing_library.motion_correction.settings import MotionCorrectionSettings
from slap2_processing_library.steps import StepResult, cli_main


def main(argv: Sequence[str] | None = None) -> list[StepResult]:
    """Run the motion correction step from command-line arguments.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    list of StepResult
        Results of the run.
    """
    return cli_main(MotionCorrectionSettings, REGISTRY, argv)
