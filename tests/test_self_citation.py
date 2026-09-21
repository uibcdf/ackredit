"""Ackredit must be discoverable by Ackredit.

It reads `CITATION.cff` to learn how a package wants to be cited, and shipped
none of its own: a citation tracker that could not be cited, failing the
discovery path it asks every other project to support.

This is also the smallest honest end-to-end check available. If Ackredit
discovers Ackredit, the CFF reader, the metadata reader and the registry agree
with each other on a real file rather than on a fixture.
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

import ackredit
from ackredit.core.cff import find_and_parse_cff, parse_cff

ROOT = Path(__file__).resolve().parents[1]
CITATION = ROOT / "CITATION.cff"
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cff():
    return yaml.safe_load(CITATION.read_text(encoding="utf-8"))


def test_ackredit_discovers_ackredit():
    """The check this file exists for."""
    discovered = find_and_parse_cff(Path(ackredit.__file__).parent)

    assert discovered is not None, (
        "Ackredit cannot find its own CITATION.cff, which is the discovery it "
        "asks every other project to support"
    )
    assert discovered["title"] == "Ackredit"
    assert discovered["authors"], "discovered with no authors"


def test_what_is_discovered_is_enough_to_cite():
    discovered = find_and_parse_cff(Path(ackredit.__file__).parent)

    for field in ("title", "authors", "url"):
        assert discovered.get(field), f"discovery produced no {field}"


def test_the_file_is_valid_cff(cff):
    assert cff["cff-version"] == "1.2.0"
    assert cff["type"] == "software"
    for author in cff["authors"]:
        assert author["family-names"] and author["given-names"]
        assert author["orcid"].startswith("https://orcid.org/")


def test_the_package_metadata_agrees_with_the_citation_file(cff):
    """Two places naming the authors is two places that can disagree, so the
    disagreement is what is tested rather than trusted."""
    declared = {entry["name"] for entry in PYPROJECT["project"]["authors"]}
    cited = {
        f"{author['given-names']} {author['family-names']}" for author in cff["authors"]
    }

    assert declared == cited, (
        f"pyproject.toml names {sorted(declared)} while CITATION.cff names "
        f"{sorted(cited)}; a citing tool reads the second"
    )


def test_the_cited_version_matches_the_latest_tag(cff):
    """`version:` in CITATION.cff is the one place a release number is still
    written by hand. Guarded rather than removed, because a citation without a
    version is less useful than one that has to be kept current."""
    described = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if described.returncode != 0:
        pytest.skip("no tag to compare against")

    latest = described.stdout.strip()
    cited = str(cff["version"])

    # The file may name the release being prepared, which is the next one.
    assert re.match(r"^\d+\.\d+\.\d+$", cited), cited
    assert cited >= latest, (
        f"CITATION.cff cites {cited} while the latest tag is {latest}; the "
        "citation metadata is behind the releases"
    )


def test_a_citing_workflow_produces_a_usable_entry(clean_registry):
    """End to end: discover, register, track, render."""

    discovered = find_and_parse_cff(Path(ackredit.__file__).parent)
    ackredit.register_item(
        id="ackredit:self",
        type="software",
        title=discovered["title"],
        authors=discovered["authors"],
        url=discovered.get("url"),
    )
    ackredit.track_item("ackredit:self", used_by="a.workflow")

    rendered = ackredit.report(format="bibtex")

    assert "@misc{ackredit-self," in rendered
    assert "Ackredit" in rendered
    assert "Prada-Gracia, Diego" in rendered


def test_the_two_copies_are_identical():
    """GitHub reads CITATION.cff at the repository root; discovery reads the one
    inside the package, because a wheel does not carry the root. Two copies are
    two things that can disagree, so the disagreement is tested."""
    root = CITATION.read_text(encoding="utf-8")
    packaged = (ROOT / "ackredit" / "CITATION.cff").read_text(encoding="utf-8")

    assert root == packaged, (
        "CITATION.cff and ackredit/CITATION.cff have diverged. The root copy is "
        "the authority; copy it over the packaged one."
    )


def test_a_built_wheel_carries_the_citation_file(tmp_path):
    """An editable install hides this: the repository root is the package's
    parent there, so discovery works from a checkout while a real installation
    finds nothing."""
    import zipfile

    built = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--outdir",
            str(tmp_path),
            str(ROOT),
        ],
        capture_output=True,
        text=True,
    )
    if built.returncode != 0:
        pytest.skip(f"wheel build unavailable: {built.stderr[-300:]}")

    wheels = list(tmp_path.glob("*.whl"))
    assert wheels, "no wheel produced"

    names = zipfile.ZipFile(wheels[0]).namelist()

    assert "ackredit/CITATION.cff" in names, (
        "the wheel ships no CITATION.cff inside the package, so an installed "
        "Ackredit cannot discover itself"
    )


def test_the_shipped_file_is_what_is_parsed(cff):
    """Guard the guard: comparing the parser against the same YAML loader it
    is meant to replace would prove nothing if either read a different file."""
    parsed = parse_cff(CITATION.read_text(encoding="utf-8"))

    assert parsed["title"] == cff["title"]
    assert len(parsed["authors"]) == len(cff["authors"])


def test_the_citation_page_agrees_with_the_citation_file(cff):
    """The page told users to cite "Prada, D. et al." for a two-author work.

    It named one of the two authors, abbreviated the other away, and gave a
    title and a year that `CITATION.cff` does not say. A library that asks every
    project to keep an accurate citation record cannot get its own wrong.
    """
    page = (ROOT / "docs/content/about/citation.md").read_text(encoding="utf-8")

    for author in cff["authors"]:
        family = author["family-names"]
        assert family in page, (
            f"{family} is an author in CITATION.cff and is missing from the "
            f"citation page, so the page credits fewer people than the record"
        )

    year = str(cff["date-released"])[:4]
    assert year in page, f"the page does not carry the released year {year}"
