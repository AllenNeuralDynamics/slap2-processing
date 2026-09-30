"""Command-line entry point for the qc step."""

from collections.abc import Sequence

from slap2_processing_library.qc.backends import REGISTRY
from slap2_processing_library.qc.settings import QcSettings
from slap2_processing_library.steps import StepResult, cli_main


def main(argv: Sequence[str] | None = None) -> list[StepResult]:
    """Run the qc step from command-line arguments.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    list of StepResult
        Results of the run.
    """
    return cli_main(QcSettings, REGISTRY, argv)
