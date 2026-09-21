"""When two sources disagree about how to cite a package, the package wins.

A `CITATION.cff` is the project's own statement, versioned and updated by the
project. Ackredit's shipped table is a snapshot that can only go stale. The hook
ran the snapshot first and marked the package as handled, so the file was never
read: `import molsysmt` credited a MolSysMT paper that does not exist while the
file saying what to cite sat unread in the same directory.

Fixing the snapshot (#26) did not change which one wins, so the next divergence
would have reproduced it. These tests hold the order.
"""

import importlib
import sys

import pytest

from ackredit.core.collector import get_used_items
from ackredit.core.hooks import InjectionsFinder
from ackredit.core.registry import Registry

CFF = """\
cff-version: 1.2.0
message: "Cite the file, not the snapshot."
type: software
title: "The Real Title"
version: 9.9.9
doi: 10.5281/zenodo.9999999
url: "https://example.org/real"
authors:
- family-names: "Moreno-Vargas"
  given-names: "Liliana M."
"""

SHIPPED_SOFTWARE = {
    "id": "fixture:software",
    "type": "software",
    "title": "A Stale Title",
    "authors": ["Someone Else"],
    "url": "https://example.org/stale",
}
SHIPPED_PAPER = {
    "id": "fixture:paper:2020",
    "type": "article",
    "title": "A Paper About It",
    "authors": ["Ruiz, Ana"],
    "year": 2020,
    "doi": "10.1/paper",
    "journal": "A Journal",
}


@pytest.fixture(autouse=True)
def _clean(clean_registry):
    yield


@pytest.fixture
def package(tmp_path, monkeypatch):
    """An importable package, with or without a CITATION.cff."""

    def build(name: str, citation: str | None):
        directory = tmp_path / name
        directory.mkdir()
        (directory / "__init__.py").write_text("")
        if citation is not None:
            (directory / "CITATION.cff").write_text(citation, encoding="utf-8")
        monkeypatch.syspath_prepend(str(tmp_path))
        importlib.invalidate_caches()
        sys.modules.pop(name, None)
        return name

    return build


def credit(name, shipped, monkeypatch):
    from ackredit.core import standard_injections

    monkeypatch.setitem(standard_injections.STANDARD_INJECTIONS, name, shipped)
    InjectionsFinder()._record(name)
    return get_used_items()


def test_the_packages_own_file_beats_the_shipped_entry(package, monkeypatch):
    """The defect: the shipped entry ran first and the file was never read."""
    name = package("fixture_both", CFF)
    used = credit(name, [SHIPPED_SOFTWARE], monkeypatch)

    assert "fixture:software" in used
    item = Registry.items["fixture:software"]
    assert item["title"] == "The Real Title"
    assert item["authors"] == ["Moreno-Vargas, Liliana M."]
    assert item["doi"] == "10.5281/zenodo.9999999"
    assert item["url"] == "https://example.org/real"
    # Only the file carries a version. Its presence says which source was read.
    assert item["version"] == "9.9.9"


def test_the_shipped_id_is_kept_so_a_binding_still_matches(package, monkeypatch):
    """The file is authoritative about the data, not about the identity."""
    name = package("fixture_id", CFF)
    used = credit(name, [SHIPPED_SOFTWARE], monkeypatch)

    assert "fixture:software" in used
    assert f"discovered:{name}" not in used


def test_a_shipped_paper_is_a_different_work_and_still_stands(package, monkeypatch):
    name = package("fixture_paper", CFF)
    used = credit(name, [SHIPPED_SOFTWARE, SHIPPED_PAPER], monkeypatch)

    assert "fixture:software" in used, "the software is credited from the file"
    assert "fixture:paper:2020" in used, "the paper is not what the file describes"
    assert Registry.items["fixture:paper:2020"]["journal"] == "A Journal"


def test_the_shipped_entry_is_used_when_there_is_no_file(package, monkeypatch):
    """A fallback, which is what it is for."""
    name = package("fixture_nofile", None)
    used = credit(name, [SHIPPED_SOFTWARE], monkeypatch)

    assert "fixture:software" in used
    assert Registry.items["fixture:software"]["title"] == "A Stale Title"


def test_a_file_with_no_shipped_entry_is_credited_on_its_own(package):
    name = package("fixture_onlyfile", CFF)
    InjectionsFinder()._record(name)

    assert f"discovered:{name}" in get_used_items()
    assert Registry.items[f"discovered:{name}"]["title"] == "The Real Title"


def test_what_the_host_asked_for_wins_over_everything(package, monkeypatch):
    """An injection is a human saying what to credit. Nothing overrides that."""
    name = package("fixture_manual", CFF)
    Registry.items["host:choice"] = {"id": "host:choice", "title": "Host's choice"}
    Registry.injections[name] = ["host:choice"]

    from ackredit.core import standard_injections

    monkeypatch.setitem(
        standard_injections.STANDARD_INJECTIONS, name, [SHIPPED_SOFTWARE]
    )
    InjectionsFinder().find_spec(name, None)

    used = get_used_items()
    assert "host:choice" in used
    assert "fixture:software" not in used
    assert f"discovered:{name}" not in used


def test_a_package_is_credited_once(package, monkeypatch):
    name = package("fixture_once", CFF)
    finder = InjectionsFinder()

    from ackredit.core import standard_injections

    monkeypatch.setitem(
        standard_injections.STANDARD_INJECTIONS, name, [SHIPPED_SOFTWARE]
    )
    finder.find_spec(name, None)
    finder.find_spec(name, None)

    assert get_used_items()["fixture:software"] == [name]
