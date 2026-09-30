"""Entry point for the qc step."""

from collections.abc import Sequence

from slap2_processing_library.qc.core import run
from slap2_processing_library.qc.settings import QcSettings
from slap2_processing_library.steps import StepResult, parse_settings


def main(argv: Sequence[str] | None = None) -> StepResult:
    """Run the qc step from command-line arguments.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    StepResult
        Outputs of the step.
    """
    return run(parse_settings(QcSettings, argv))
