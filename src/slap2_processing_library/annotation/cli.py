"""Command-line entry point for the annotation step."""

from collections.abc import Sequence

from slap2_processing_library.annotation.backends import REGISTRY
from slap2_processing_library.annotation.settings import AnnotationSettings
from slap2_processing_library.steps import StepResult, cli_main


def main(argv: Sequence[str] | None = None) -> list[StepResult]:
    """Run the annotation step from command-line arguments.

    Parameters
    ----------
    argv : sequence of str, optional
        Arguments such as ``["--scan_mode=band_scan"]``. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    list of StepResult
        Results of the run.
    """
    return cli_main(AnnotationSettings, REGISTRY, argv)
