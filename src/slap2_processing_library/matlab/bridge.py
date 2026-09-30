"""Run MATLAB entry points as subprocesses with a JSON job contract.

Python owns every run: it writes a job file, starts MATLAB (``matlab -batch``) or a compiled
MATLAB Runtime executable, fails on a non-zero exit, and reads the result file the entry point
wrote. Running one subprocess per (DMD, trial) batch bounds MATLAB's memory growth on Linux and
lets the pipeline fan work out across tasks.
"""

import json
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

ENTRY_POINT_DIR = Path(__file__).parent / "entry_points"
STDERR_TAIL_LINES = 20

Runner = Callable[..., subprocess.CompletedProcess[str]]


class RuntimeKind(StrEnum):
    """How MATLAB code is executed."""

    MATLAB = "matlab"
    MATLAB_RUNTIME = "matlab_runtime"


class MatlabJobError(RuntimeError):
    """Raised when a MATLAB job exits non-zero or writes no result."""


@dataclass(frozen=True)
class MatlabRuntime:
    """MATLAB installation used to run jobs.

    Attributes
    ----------
    kind : RuntimeKind
        Licensed MATLAB or a compiled executable on the MATLAB Runtime.
    executable : str
        ``matlab`` or the path of the compiled executable.
    search_paths : tuple of Path
        Directories added with ``addpath(genpath(...))``, for example the GIAnT-MATLAB and
        Slap2DataReader checkouts. Ignored for compiled executables.
    """

    kind: RuntimeKind = RuntimeKind.MATLAB
    executable: str = "matlab"
    search_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class MatlabJob:
    """A job file for one MATLAB entry point call.

    Attributes
    ----------
    entry_point : str
        MATLAB function in :data:`ENTRY_POINT_DIR`, for example
        ``slap2_run_motion_correction``.
    job_file : Path
        JSON file the entry point reads.
    result_file : Path
        JSON file the entry point writes on success.
    """

    entry_point: str
    job_file: Path
    result_file: Path


def matlab_string(value: str) -> str:
    """Quote a value as a MATLAB character vector literal.

    Parameters
    ----------
    value : str
        Text to quote.

    Returns
    -------
    str
        The text in single quotes with embedded single quotes doubled.
    """
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def write_job(job_dir: Path, entry_point: str, payload: Mapping[str, object]) -> MatlabJob:
    """Write the job file for one entry point call.

    Parameters
    ----------
    job_dir : Path
        Directory for the job and result files; created if missing.
    entry_point : str
        MATLAB entry point name.
    payload : Mapping
        JSON-serializable arguments, for example the trial table path, DMD, and trials.

    Returns
    -------
    MatlabJob
        Paths of the job and result files.
    """
    job_dir.mkdir(parents=True, exist_ok=True)
    job = MatlabJob(
        entry_point=entry_point,
        job_file=job_dir / f"{entry_point}.job.json",
        result_file=job_dir / f"{entry_point}.result.json",
    )
    document = {
        "entry_point": entry_point,
        "result_file": str(job.result_file),
        "payload": dict(payload),
    }
    job.job_file.write_text(json.dumps(document, indent=2, default=str))
    return job


def build_command(runtime: MatlabRuntime, job: MatlabJob) -> list[str]:
    """Build the command that runs a job.

    Parameters
    ----------
    runtime : MatlabRuntime
        MATLAB installation.
    job : MatlabJob
        Job to run.

    Returns
    -------
    list of str
        Argument vector for :func:`subprocess.run`.
    """
    if runtime.kind is RuntimeKind.MATLAB_RUNTIME:
        return [runtime.executable, str(job.job_file)]
    search_paths = (ENTRY_POINT_DIR, *runtime.search_paths)
    statements = [f"addpath(genpath({matlab_string(str(path))}))" for path in search_paths]
    statements.append(f"{job.entry_point}({matlab_string(str(job.job_file))})")
    return [runtime.executable, "-batch", "; ".join(statements)]


def run_job(
    runtime: MatlabRuntime,
    job: MatlabJob,
    runner: Runner = subprocess.run,
    timeout_s: float | None = None,
) -> dict[str, object]:
    """Run a job and return the result the entry point wrote.

    Parameters
    ----------
    runtime : MatlabRuntime
        MATLAB installation.
    job : MatlabJob
        Job to run.
    runner : Callable, optional
        ``subprocess.run`` or a test double.
    timeout_s : float, optional
        Seconds before the subprocess is killed.

    Returns
    -------
    dict
        Parsed result file.

    Raises
    ------
    MatlabJobError
        If MATLAB exits non-zero or the result file is missing.
    """
    completed = runner(
        build_command(runtime, job),
        capture_output=True,
        text=True,
        timeout=timeout_s,
        check=False,
    )
    if completed.returncode != 0:
        tail = "\n".join(completed.stderr.splitlines()[-STDERR_TAIL_LINES:])
        raise MatlabJobError(
            f"{job.entry_point} exited with code {completed.returncode}. stderr tail:\n{tail}"
        )
    if not job.result_file.is_file():
        raise MatlabJobError(f"{job.entry_point} exited 0 but wrote no {job.result_file}.")
    return json.loads(job.result_file.read_text())
