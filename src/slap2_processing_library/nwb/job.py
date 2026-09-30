"""Entry point for the nwb step."""

from collections.abc import Sequence

from slap2_processing_library.nwb.core import run
from slap2_processing_library.nwb.settings import NwbSettings
from slap2_processing_library.steps import StepResult, parse_settings


def main(argv: Sequence[str] | None = None) -> StepResult:
    """Run the nwb step from command-line arguments.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    StepResult
        Outputs of the step.
    """
    return run(parse_settings(NwbSettings, argv))
