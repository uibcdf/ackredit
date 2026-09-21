"""The version has one source of truth: the Git tag.

A static literal in `pyproject.toml` and a release tag are two sources kept in
step by hand, and they drift the first time someone forgets. Versioningit derives
one from the other, and `policy-v1.4.1` requires the derivation to refuse a tag
that is not a canonical MolSysSuite release identifier.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

import ackredit

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

CANONICAL = [
    "0.0.0",
    "1.2.3",
    "0.5.0",
    "10.20.30",
]

REJECTED = [
    "v1.2.3",  # a prefix
    "1.2.3rc1",  # a prerelease
    "1.2.3.dev0",  # a development suffix
    "1.2.3+local",  # a local suffix
    "01.2.3",  # a leading zero
    "1.2",  # not three parts
    "1.2.3.4",  # four
]


def test_the_version_is_derived_not_written():
    """A static `project.version` is the second source of truth this removes."""
    assert PYPROJECT["project"].get("version") is None
    assert "version" in PYPROJECT["project"]["dynamic"]
    assert any(
        requirement.startswith("versioningit")
        for requirement in PYPROJECT["build-system"]["requires"]
    )


def test_the_tag_parser_is_the_canonical_suite_pattern():
    """Taken from `policies.release-version.versioningit-pattern` in suite.toml.
    Copying it by hand is how two patterns start to differ, so it is asserted."""
    tag2version = PYPROJECT["tool"]["versioningit"]["tag2version"]

    assert tag2version["require-match"] is True, (
        "without require-match the pattern is documentation, not a gate: a "
        "nonconforming tag would quietly produce some other version"
    )
    assert tag2version["regex"] == (
        r"^(?P<version>(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*))$"
    )


@pytest.mark.parametrize("tag", CANONICAL)
def test_a_canonical_tag_is_accepted(tag):
    regex = PYPROJECT["tool"]["versioningit"]["tag2version"]["regex"]
    match = re.match(regex, tag)

    assert match is not None
    assert match.group("version") == tag


@pytest.mark.parametrize("tag", REJECTED)
def test_a_nonconforming_tag_is_refused(tag):
    """With require-match, no match means the build fails rather than inventing
    a version. MolSysSuite release identifiers are exactly X.Y.Z."""
    regex = PYPROJECT["tool"]["versioningit"]["tag2version"]["regex"]

    assert re.match(regex, tag) is None


def test_the_public_version_matches_what_versioningit_derives():
    """The one assertion that catches the two drifting apart."""
    result = subprocess.run(
        [sys.executable, "-m", "versioningit", str(ROOT)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"versioningit could not derive a version here: {result.stderr}")

    derived = result.stdout.strip()

    assert ackredit.__version__ == derived, (
        f"the package reports {ackredit.__version__} while the tag derives "
        f"{derived}; the built metadata and the public version have drifted"
    )


def test_the_version_is_not_the_unknown_fallback():
    """`0.0.0+unknown` means neither the build nor the metadata answered, which
    is a broken install rather than a version."""
    assert ackredit.__version__ != "0.0.0+unknown"
    assert re.match(r"^\d+\.\d+\.\d+", ackredit.__version__), ackredit.__version__
