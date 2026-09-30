"""Step framework: shared settings, backend registry, and dispatch.

Every step (motion correction, source extraction, ...) defines a settings class derived from
:class:`StepSettings`, a :class:`BackendRegistry` that maps ``(scan_mode, backend)`` to an
implementation, and a console entry point that calls :func:`cli_main`. Code Ocean capsules and
pipeline tasks call those entry points; they never import step internals.
"""

import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from slap2_processing_library.enums import Backend, ScanMode, Step
from slap2_processing_library.matlab.bridge import MatlabRuntime, Runner, run_job, write_job
from slap2_processing_library.matlab.giant import GIANT_MATLAB, SLAP2_DATA_READER, verify_checkout

DEFAULT_INPUT_DIR = Path("/data")
DEFAULT_OUTPUT_DIR = Path("/results")
MATLAB_OUTPUT_SUBDIR = "matlab"
PYTHON_OUTPUT_SUBDIR = "python"


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
    backend: Backend = Field(
        default=Backend.MATLAB,
        description="Implementation to run: matlab, python, or both with a parity check.",
    )


@dataclass(frozen=True)
class StepResult:
    """Outcome of one backend run.

    Attributes
    ----------
    step : Step
        Step that ran.
    scan_mode : ScanMode
        Scan mode the step ran for.
    backend : Backend
        Backend that did the numerical work; never ``Backend.BOTH``.
    output_dir : Path
        Directory holding the outputs.
    outputs : tuple of Path
        Files the backend wrote, relative to ``output_dir``.
    """

    step: Step
    scan_mode: ScanMode
    backend: Backend
    output_dir: Path
    outputs: tuple[Path, ...] = ()


class UnsupportedCombinationError(ValueError):
    """Raised when a step has no implementation for a scan mode and backend."""


class NotPortedError(NotImplementedError):
    """Raised by a Python backend whose port from GIAnT-MATLAB has not landed yet.

    Parameters
    ----------
    step : Step
        Step whose Python backend was requested.
    scan_mode : ScanMode
        Scan mode that was requested.
    matlab_reference : str
        GIAnT-MATLAB function the port reproduces, for example ``MultiRoiRegistration``.
    """

    def __init__(self, step: Step, scan_mode: ScanMode, matlab_reference: str) -> None:
        """Build the message from the step, scan mode, and MATLAB reference."""
        super().__init__(
            f"The Python {step} backend for {scan_mode} is not ported yet. It will reproduce "
            f"GIAnT-MATLAB {matlab_reference}; run with backend=matlab until it passes parity. "
            "See docs/design/matlab-transition.md."
        )
        self.step = step
        self.scan_mode = scan_mode
        self.matlab_reference = matlab_reference


BackendImplementation = Callable[[StepSettings, Path], StepResult]
ParityCheck = Callable[[StepResult, StepResult], Path]


@dataclass
class BackendRegistry:
    """Map ``(scan_mode, backend)`` to the implementation that runs a step.

    Parameters
    ----------
    step : Step
        Step the registry belongs to.
    """

    step: Step
    _implementations: dict[tuple[ScanMode, Backend], BackendImplementation] = field(
        default_factory=dict, repr=False
    )
    _unsupported: dict[ScanMode, str] = field(default_factory=dict, repr=False)

    def register(
        self, scan_mode: ScanMode, backend: Backend
    ) -> Callable[[BackendImplementation], BackendImplementation]:
        """Return a decorator that registers an implementation.

        Parameters
        ----------
        scan_mode : ScanMode
            Scan mode the implementation handles.
        backend : Backend
            ``Backend.MATLAB`` or ``Backend.PYTHON``. ``Backend.BOTH`` is composed by
            :func:`run_step` and cannot be registered.

        Returns
        -------
        Callable
            Decorator that stores the implementation and returns it unchanged.

        Raises
        ------
        ValueError
            If ``backend`` is ``Backend.BOTH`` or the combination is already registered.
        """
        if backend is Backend.BOTH:
            raise ValueError("Backend.BOTH is composed from the matlab and python backends.")
        key = (scan_mode, backend)
        if key in self._implementations:
            raise ValueError(f"{self.step} already has an implementation for {key}.")

        def decorator(implementation: BackendImplementation) -> BackendImplementation:
            """Store an implementation under the combination.

            Parameters
            ----------
            implementation : BackendImplementation
                Callable that runs the step.

            Returns
            -------
            BackendImplementation
                The same callable, unchanged.
            """
            self._implementations[key] = implementation
            return implementation

        return decorator

    def mark_unsupported(self, scan_mode: ScanMode, reason: str) -> None:
        """Record why a scan mode has no implementation for this step.

        Parameters
        ----------
        scan_mode : ScanMode
            Scan mode that is not supported.
        reason : str
            Explanation shown to the user, for example the missing dependency.
        """
        self._unsupported[scan_mode] = reason

    def resolve(self, scan_mode: ScanMode, backend: Backend) -> BackendImplementation:
        """Return the implementation for a scan mode and a concrete backend.

        Parameters
        ----------
        scan_mode : ScanMode
            Scan mode of the session.
        backend : Backend
            ``Backend.MATLAB`` or ``Backend.PYTHON``.

        Returns
        -------
        BackendImplementation
            Callable that runs the step.

        Raises
        ------
        UnsupportedCombinationError
            If the scan mode is marked unsupported or nothing is registered for the combination.
        """
        if scan_mode in self._unsupported:
            raise UnsupportedCombinationError(
                f"{self.step} does not support {scan_mode}: {self._unsupported[scan_mode]}"
            )
        try:
            return self._implementations[(scan_mode, backend)]
        except KeyError:
            raise UnsupportedCombinationError(
                f"{self.step} has no {backend} implementation for {scan_mode}."
            ) from None

    def supported(self) -> list[tuple[ScanMode, Backend]]:
        """List the registered combinations in a stable order.

        Returns
        -------
        list of tuple
            ``(scan_mode, backend)`` pairs sorted by their string values.
        """
        return sorted(self._implementations, key=lambda key: (str(key[0]), str(key[1])))


def run_step(
    settings: StepSettings,
    registry: BackendRegistry,
    parity_check: ParityCheck | None = None,
) -> list[StepResult]:
    """Run a step with the backend the settings select.

    Parameters
    ----------
    settings : StepSettings
        Validated step settings.
    registry : BackendRegistry
        Registry of the step's implementations.
    parity_check : ParityCheck, optional
        Comparison run when ``settings.backend`` is ``Backend.BOTH``. It receives the MATLAB and
        Python results and returns the path of the parity report it wrote.

    Returns
    -------
    list of StepResult
        One result, or the MATLAB and Python results when both backends ran.

    Raises
    ------
    UnsupportedCombinationError
        If ``Backend.BOTH`` is requested without a parity check, or the combination is not
        implemented.
    """
    if settings.backend is not Backend.BOTH:
        implementation = registry.resolve(settings.scan_mode, settings.backend)
        return [implementation(settings, settings.output_dir)]
    if parity_check is None:
        raise UnsupportedCombinationError(f"{registry.step} has no parity check for backend=both.")
    matlab = registry.resolve(settings.scan_mode, Backend.MATLAB)
    python = registry.resolve(settings.scan_mode, Backend.PYTHON)
    matlab_result = matlab(settings, settings.output_dir / MATLAB_OUTPUT_SUBDIR)
    python_result = python(settings, settings.output_dir / PYTHON_OUTPUT_SUBDIR)
    parity_check(matlab_result, python_result)
    return [matlab_result, python_result]


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


def cli_main(
    settings_class: type[StepSettings],
    registry: BackendRegistry,
    argv: Sequence[str] | None = None,
    parity_check: ParityCheck | None = None,
) -> list[StepResult]:
    """Parse settings and run a step; exceptions propagate so the process exits non-zero.

    Parameters
    ----------
    settings_class : type
        Step settings class.
    registry : BackendRegistry
        Registry of the step's implementations.
    argv : sequence of str, optional
        Command-line arguments. Defaults to ``sys.argv[1:]``.
    parity_check : ParityCheck, optional
        Comparison used when both backends run.

    Returns
    -------
    list of StepResult
        Results from :func:`run_step`.
    """
    settings = parse_settings(settings_class, argv)
    return run_step(settings, registry, parity_check)


class MatlabStepSettings(StepSettings):
    """Settings for steps that can run on the GIAnT-MATLAB backend."""

    giant_matlab_dir: Path = Field(
        default=Path("/opt/GIAnT-MATLAB"), description="Pinned GIAnT-MATLAB checkout."
    )
    data_reader_dir: Path = Field(
        default=Path("/opt/Slap2DataReader"), description="Pinned Slap2DataReader checkout."
    )
    matlab_executable: str = Field(
        default="matlab", description="MATLAB launcher or compiled MATLAB Runtime executable."
    )


def run_matlab_step(
    settings: MatlabStepSettings,
    step: Step,
    output_dir: Path,
    entry_point: str,
    runner: Runner = subprocess.run,
) -> StepResult:
    """Run a step's GIAnT-MATLAB entry point through the subprocess bridge.

    Parameters
    ----------
    settings : MatlabStepSettings
        Validated step settings.
    step : Step
        Step being run.
    output_dir : Path
        Directory for the outputs and the job files.
    entry_point : str
        MATLAB entry point in the library's ``matlab/entry_points`` directory.
    runner : Callable, optional
        ``subprocess.run`` or a test double.

    Returns
    -------
    StepResult
        Outputs listed in the result file the entry point wrote.
    """
    for checkout, pin in (
        (settings.giant_matlab_dir, GIANT_MATLAB),
        (settings.data_reader_dir, SLAP2_DATA_READER),
    ):
        verify_checkout(checkout, pin, runner)
    runtime = MatlabRuntime(
        executable=settings.matlab_executable,
        search_paths=(settings.giant_matlab_dir, settings.data_reader_dir),
    )
    payload = settings.model_dump(mode="json") | {"output_dir": str(output_dir)}
    job = write_job(output_dir / "matlab_jobs", entry_point, payload)
    result = run_job(runtime, job, runner)
    outputs = tuple(Path(str(path)) for path in result.get("outputs", []))
    return StepResult(step, settings.scan_mode, Backend.MATLAB, output_dir, outputs)
