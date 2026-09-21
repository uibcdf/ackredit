"""Guards for what an installed distribution actually ships.

These run against the declared configuration rather than a built wheel, so they
stay fast, need no build backend at test time, and still fail on the exact
regression they exist for.
"""

import re
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


def _requirement_name(requirement: str) -> str:
    """The distribution name in a requirement string, without its specifiers."""
    return re.split(r"[<>=!~\[ ;]", requirement, maxsplit=1)[0].strip()


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


def test_the_package_states_its_version():
    """The first thing a user reports in a bug, and what a citation of Ackredit
    itself needs. It was absent, and the CI check for it could not fail."""
    import ackredit

    assert ackredit.__version__
    assert ackredit.__version__ != "0.0.0+unknown"
    assert "__version__" in ackredit.__all__


def test_every_optional_library_can_be_installed_through_an_extra():
    """`dependency_info()` reported duecredit as an optional feature, and no
    extra installed it. `full` listed only flask, so it was not full."""
    from ackredit._depdigest import LIBRARIES

    extras = _pyproject()["project"]["optional-dependencies"]
    # The extras that install one feature: not the ones that build or test, and
    # not `full`, which is their union and would satisfy this on its own.
    declared = {
        name
        for extra, requirements in extras.items()
        if extra not in {"test", "docs", "full"}
        for name in (_requirement_name(item) for item in requirements)
    }

    missing = set(LIBRARIES) - declared
    assert not missing, (
        f"{sorted(missing)} is declared to DepDigest as an optional feature "
        f"and has no extra of its own, so it can only be installed by taking "
        f"every other optional dependency with it"
    )


def test_the_full_extra_is_full():
    from ackredit._depdigest import LIBRARIES

    full = {
        _requirement_name(item)
        for item in _pyproject()["project"]["optional-dependencies"]["full"]
    }
    assert set(LIBRARIES) <= full, (
        f"the 'full' extra omits {sorted(set(LIBRARIES) - full)}"
    )
