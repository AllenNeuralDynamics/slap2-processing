"""Tests for the MATLAB bridge and pins."""

import json
import subprocess
from pathlib import Path

import pytest

from slap2_processing_library.matlab import bridge, giant
from tests.conftest import FakeRunner


def test_matlab_string_escapes_quotes() -> None:
    """Single quotes are doubled."""
    assert bridge.matlab_string("it's") == "'it''s'"


def test_write_job_and_build_commands(tmp_path: Path) -> None:
    """Job files carry the payload; both runtime kinds build commands."""
    job = bridge.write_job(tmp_path / "jobs", "slap2_run_qc", {"dmd": 1})
    assert json.loads(job.job_file.read_text())["payload"] == {"dmd": 1}
    batch = bridge.build_command(bridge.MatlabRuntime(search_paths=(Path("/opt/g"),)), job)
    assert batch[:2] == ["matlab", "-batch"]
    assert "addpath(genpath('/opt/g'))" in batch[2]
    assert batch[2].endswith(f"slap2_run_qc('{job.job_file}')")
    compiled = bridge.MatlabRuntime(kind=bridge.RuntimeKind.MATLAB_RUNTIME, executable="/opt/mc")
    assert bridge.build_command(compiled, job) == ["/opt/mc", str(job.job_file)]


def test_run_job_success_and_failures(tmp_path: Path) -> None:
    """Non-zero exits and missing results raise; success returns the result."""
    runtime = bridge.MatlabRuntime()
    job = bridge.write_job(tmp_path, "slap2_run_qc", {})
    assert bridge.run_job(runtime, job, FakeRunner()) == {"outputs": ["out.h5"]}
    with pytest.raises(bridge.MatlabJobError, match="exited with code 1"):
        bridge.run_job(runtime, job, FakeRunner(returncode=1))
    job.result_file.unlink()
    with pytest.raises(bridge.MatlabJobError, match="wrote no"):
        bridge.run_job(runtime, job, FakeRunner(write_result=False))


def test_pins_clone_and_verify(tmp_path: Path) -> None:
    """Clone commands check out the pin; a mismatched checkout raises."""
    commands = giant.GIANT_MATLAB.clone_commands(tmp_path)
    assert commands[-1][-1] == giant.GIANT_MATLAB.commit
    giant.verify_checkout(Path("/opt/GIAnT-MATLAB"), giant.GIANT_MATLAB, FakeRunner())

    def wrong(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        """Report another commit.

        Parameters
        ----------
        command : list of str
            Argument vector.
        **_ : object
            Ignored.

        Returns
        -------
        subprocess.CompletedProcess
            Fake result.
        """
        return subprocess.CompletedProcess(command, 0, stdout="deadbeef\n", stderr="")

    with pytest.raises(giant.PinMismatchError, match="expected"):
        giant.verify_checkout(tmp_path, giant.GIANT_MATLAB, wrong)
