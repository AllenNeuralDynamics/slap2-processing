"""Command-line entry point for the nwb step."""

from collections.abc import Sequence

from slap2_processing_library.nwb.backends import REGISTRY
from slap2_processing_library.nwb.settings import NwbSettings
from slap2_processing_library.steps import StepResult, cli_main


def main(argv: Sequence[str] | None = None) -> list[StepResult]:
    """Run the nwb step from command-line arguments.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    list of StepResult
        Results of the run.
    """
    return cli_main(NwbSettings, REGISTRY, argv)
