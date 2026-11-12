"""The version has one source of truth: the Git tag.

A static literal in `pyproject.toml` and a release tag are two sources kept in
step by hand, and they drift the first time someone forgets. Versioningit derives
one from the other, and `policy-v1.4.1` requires the derivation to refuse a tag
that is not a canonical MolSysSuite release identifier.
"""

import json
import re
import subprocess
import sys
import tomllib
from importlib.metadata import version
from pathlib import Path

import pytest
from packaging.version import Version

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


def test_the_public_version_comes_from_the_tag():
    """The assertion that catches the release identifier drifting from the tag.

    Only the part before `+` is compared. The suffix is distance and revision,
    which changes with every commit in a checkout, so asserting the whole string
    would fail on the next commit and teach everyone to ignore this file.
    """
    origin = Path(ackredit.__file__).resolve()
    if (
        re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", ackredit.__version__)
        and origin.is_relative_to(Path(sys.prefix).resolve())
        and not origin.is_relative_to(ROOT / "ackredit")
    ):
        # Installed qualification precedes the public tag and uses a separate
        # source checkout. Its Git fallback is not the artifact's identity.
        # Keep a real rejection of stale/mismatched packages rather than skipping
        # the guard or manufacturing tags/version overrides (#141).
        assert ackredit.__version__ == version("ackredit"), "distribution mismatch"
        candidate = tomllib.loads(
            (ROOT / "devtools/conda-build/release_plan.toml").read_text()
        )["version"]
        assert ackredit.__version__ == candidate, "installed candidate mismatch"
        return
    result = subprocess.run(
        [sys.executable, "-m", "versioningit", str(ROOT)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(f"versioningit could not derive a version here: {result.stderr}")

    derived = result.stdout.strip()

    assert ackredit.__version__.split("+")[0] == derived.split("+")[0], (
        f"the package reports {ackredit.__version__} while the tag derives "
        f"{derived}; the release identifier has drifted from the tag"
    )


@pytest.mark.parametrize(
    "runtime,distribution,accepted",
    [
        ("0.12.2", "0.12.2", True),
        ("0.12.1", "0.12.1", False),
        ("0.12.2", "0.12.1", False),
    ],
)
def test_installed_candidate_identity_does_not_depend_on_checkout_tags(
    tmp_path, monkeypatch, runtime, distribution, accepted
):
    from types import SimpleNamespace

    root = tmp_path / "checkout"
    plan = root / "devtools/conda-build/release_plan.toml"
    plan.parent.mkdir(parents=True)
    plan.write_text('version = "0.12.2"\n')
    monkeypatch.setattr(sys.modules[__name__], "ROOT", root)
    monkeypatch.setattr(ackredit, "__version__", runtime)
    monkeypatch.setattr(
        ackredit,
        "__file__",
        str(Path(sys.prefix) / "lib/site-packages/ackredit/__init__.py"),
    )
    monkeypatch.setattr(sys.modules[__name__], "version", lambda _: distribution)
    # A shallow pre-release checkout has no release tag; it is not the authority
    # for the separately inspected installed archive's canonical identity.
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="0.0.0", stderr=""),
    )
    if accepted:
        test_the_public_version_comes_from_the_tag()
    else:
        with pytest.raises(AssertionError, match="candidate|distribution"):
            test_the_public_version_comes_from_the_tag()


def test_a_development_version_is_marked_as_one():
    """A build away from a tag must not look like the release itself."""
    result = subprocess.run(
        [sys.executable, "-m", "versioningit", str(ROOT)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip("versioningit could not derive a version here")

    derived = result.stdout.strip()
    distance = subprocess.run(
        ["git", "describe", "--tags", "--long"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if distance.returncode != 0:
        pytest.skip("no tag to measure distance from")

    commits_since_tag = int(distance.stdout.strip().rsplit("-", 2)[1])
    dirty = bool(
        subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        ).stdout.strip()
    )

    if commits_since_tag == 0 and not dirty:
        assert "+" not in derived, (
            f"{derived} is exactly the tag in a clean tree and should be the "
            "bare release identifier"
        )
    else:
        reason = "dirty" if dirty else f"{commits_since_tag} commits past its tag"
        assert "+" in derived, (
            f"{derived} is {reason} and does not say so; a development build "
            "must not be mistaken for the release"
        )
        if dirty:
            assert derived.endswith(".dirty"), derived


def test_the_version_is_not_the_unknown_fallback():
    """`0.0.0+unknown` means neither the build nor the metadata answered, which
    is a broken install rather than a version."""
    assert ackredit.__version__ != "0.0.0+unknown"
    assert re.match(r"^\d+\.\d+\.\d+", ackredit.__version__), ackredit.__version__


def test_installed_version_is_not_older_than_verified_public_delivery():
    """A missing release tag made the editable package fail consumer minima."""
    receipts = ROOT / "devtools" / "conda-build" / "receipts"
    published = [
        Version(json.loads(path.read_text(encoding="utf-8"))["published_version"])
        for path in receipts.glob("ackredit_*_public_*.json")
    ]
    assert published, "retain the verified public delivery receipt"
    minimum = max(published)
    for actual in (version("ackredit"), ackredit.__version__):
        assert Version(actual) >= minimum, (
            f"installed Ackredit {actual} predates verified public {minimum}; "
            "register the release tag at its recorded producer and reinstall"
        )
