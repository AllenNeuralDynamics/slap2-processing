"""Shared test doubles."""

import json
import subprocess
from pathlib import Path

import pytest

from slap2_processing_library.matlab.giant import GIANT_MATLAB, SLAP2_DATA_READER


class FakeRunner:
    """Stand-in for ``subprocess.run`` covering git and MATLAB calls."""

    def __init__(self, returncode: int = 0, write_result: bool = True) -> None:
        """Configure the MATLAB outcome.

        Parameters
        ----------
        returncode : int
            Exit code of the MATLAB call.
        write_result : bool
            Whether the MATLAB call writes its result file.
        """
        self.returncode = returncode
        self.write_result = write_result
        self.calls: list[list[str]] = []

    def __call__(self, command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        """Record a command and fake its result.

        Parameters
        ----------
        command : list of str
            Argument vector.
        **_ : object
            Ignored keyword arguments.

        Returns
        -------
        subprocess.CompletedProcess
            Fake completed process.
        """
        self.calls.append(command)
        if command[0] == "git":
            pin = GIANT_MATLAB if "GIAnT" in command[2] else SLAP2_DATA_READER
            return subprocess.CompletedProcess(command, 0, stdout=f"{pin.commit}\n", stderr="")
        job_file = (
            Path(command[-1].rsplit("'", 2)[-2]) if "-batch" in command else Path(command[-1])
        )
        if self.write_result:
            job = json.loads(job_file.read_text())
            Path(job["result_file"]).write_text(json.dumps({"outputs": ["out.h5"]}))
        return subprocess.CompletedProcess(command, self.returncode, stdout="", stderr="boom\n")


@pytest.fixture
def fake_runner() -> FakeRunner:
    """Return a runner whose MATLAB calls succeed.

    Returns
    -------
    FakeRunner
        Runner that writes a result file.
    """
    return FakeRunner()
