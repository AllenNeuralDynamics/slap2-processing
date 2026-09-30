"""Pinned MATLAB code that the MATLAB backend runs.

The pins are single-sourced here. MATLAB capsule images clone them at build time with
:meth:`GitPin.clone_commands`, and the bridge verifies the checkout before every run.
"""

import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

Runner = Callable[..., subprocess.CompletedProcess[str]]


class PinMismatchError(RuntimeError):
    """Raised when a MATLAB checkout is not at its pinned commit."""


@dataclass(frozen=True)
class GitPin:
    """A git repository pinned to one commit.

    Attributes
    ----------
    name : str
        Repository name, recorded as ``Code.core_dependency`` in processing metadata.
    url : str
        Clone URL.
    commit : str
        Full commit SHA.
    """

    name: str
    url: str
    commit: str

    def clone_commands(self, destination: Path) -> list[list[str]]:
        """Return the commands that check out this pin.

        Parameters
        ----------
        destination : Path
            Directory to clone into, for example ``/opt/GIAnT-MATLAB``.

        Returns
        -------
        list of list of str
            ``git clone`` then ``git checkout --detach`` argument vectors.
        """
        return [
            ["git", "clone", "--filter=blob:none", self.url, str(destination)],
            ["git", "-C", str(destination), "checkout", "--detach", self.commit],
        ]


GIANT_MATLAB = GitPin(
    name="GIAnT-MATLAB",
    url="https://github.com/AllenNeuralDynamics/GIAnT-MATLAB.git",
    commit="558c1693888cc009a19b2ea1cbb86e24698b8840",
)
SLAP2_DATA_READER = GitPin(
    name="Slap2DataReader",
    url="https://github.com/m-xie/Slap2DataReader.git",
    commit="6f458c0045a982e62eda48f7a63d9c340efcf799",
)
MATLAB_PINS = (GIANT_MATLAB, SLAP2_DATA_READER)


def checked_out_commit(checkout: Path, runner: Runner = subprocess.run) -> str:
    """Return the commit a checkout is at.

    Parameters
    ----------
    checkout : Path
        Repository working tree.
    runner : Callable, optional
        ``subprocess.run`` or a test double.

    Returns
    -------
    str
        Full commit SHA of ``HEAD``.
    """
    completed = runner(
        ["git", "-C", str(checkout), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def verify_checkout(checkout: Path, pin: GitPin, runner: Runner = subprocess.run) -> None:
    """Fail unless a checkout is at its pinned commit.

    Parameters
    ----------
    checkout : Path
        Repository working tree.
    pin : GitPin
        Expected pin.
    runner : Callable, optional
        ``subprocess.run`` or a test double.

    Raises
    ------
    PinMismatchError
        If ``HEAD`` differs from ``pin.commit``.
    """
    actual = checked_out_commit(checkout, runner)
    if actual != pin.commit:
        raise PinMismatchError(f"{pin.name} at {checkout} is {actual}, expected {pin.commit}.")
