"""Guards for what an installed distribution actually ships.

These run against the declared configuration rather than a built wheel, so they
stay fast, need no build backend at test time, and still fail on the exact
regression they exist for.
"""

import tomllib
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def _packages_on_disk() -> set[str]:
    return {
        ".".join(path.relative_to(ROOT).parts[:-1])
        for path in (ROOT / "ackredit").rglob("__init__.py")
    }


def test_package_discovery_is_declarative():
    """A hardcoded package list silently drops subpackages when one is added."""
    setuptools_config = _pyproject()["tool"]["setuptools"]

    assert (
        "packages" not in setuptools_config or "find" in setuptools_config["packages"]
    ), "declare tool.setuptools.packages.find, not a literal package list"
    assert setuptools_config["packages"]["find"]["include"]


def test_every_subpackage_is_shipped():
    """Regression guard: packages = ["ackredit"] shipped only __init__ and cli.

    An installed wheel then raised ModuleNotFoundError for ackredit.core on
    import, while the test suite passed from the repository root.
    """
    include = _pyproject()["tool"]["setuptools"]["packages"]["find"]["include"]
    on_disk = _packages_on_disk()

    covered = {
        package
        for package in on_disk
        if any(fnmatch(package, pattern) for pattern in include)
    }

    assert covered == on_disk, f"not shipped: {sorted(on_disk - covered)}"


def test_the_subpackages_we_expect_are_present():
    """Keeps the guard honest if the package layout is ever flattened."""
    on_disk = _packages_on_disk()

    assert {
        "ackredit",
        "ackredit.core",
        "ackredit.formats",
        "ackredit.contrib",
    } <= on_disk
