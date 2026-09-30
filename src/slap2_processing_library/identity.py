"""Identity of this library, used for provenance in emitted metadata."""

from importlib.metadata import version

LIBRARY_DISTRIBUTION = "slap2-processing-library"
LIBRARY_URL = "https://github.com/AllenNeuralDynamics/slap2-processing-library"


def library_version() -> str:
    """Return the installed version of this library.

    Returns
    -------
    str
        Version string read from the installed distribution metadata. An uninstalled library
        raises ``PackageNotFoundError`` rather than recording an unknown version.
    """
    return version(LIBRARY_DISTRIBUTION)
