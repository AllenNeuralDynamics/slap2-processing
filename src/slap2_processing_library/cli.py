"""Single entry point that runs any step: ``slap2 <step> --param=value ...``.

One capsule can call every step of the pipeline by passing the step name first.
"""

import sys
from collections.abc import Callable, Sequence
from importlib import import_module

from slap2_processing_library.enums import Step
from slap2_processing_library.steps import StepResult

USAGE = "usage: slap2 {" + ",".join(step.value for step in Step) + "} [--param=value ...]"


def step_main(step: Step) -> Callable[[Sequence[str] | None], list[StepResult]]:
    """Return the ``main`` function of a step's CLI module.

    Parameters
    ----------
    step : Step
        Step to load. Only that step's module is imported.

    Returns
    -------
    Callable
        The step's ``main(argv)``.
    """
    return import_module(f"slap2_processing_library.{step.value}.cli").main


def main(argv: Sequence[str] | None = None) -> list[StepResult]:
    """Dispatch to a step's entry point.

    Parameters
    ----------
    argv : sequence of str, optional
        Step name followed by its arguments. Defaults to ``sys.argv[1:]``.

    Returns
    -------
    list of StepResult
        Results of the step.

    Raises
    ------
    SystemExit
        If no step or an unknown step is given.
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] not in set(Step):
        raise SystemExit(USAGE)
    return step_main(Step(args[0]))(args[1:])
