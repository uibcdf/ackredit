"""The citation data Ackredit ships must be true.

Ackredit injects citation metadata for packages it knows, and half of those
entries listed `"et al."` as an author. BibTeX reads a name-shaped string as a
person, so `author = {Harris, C. R. and et al.}` prints "C. R. Harris and
E. al." in a bibliography, and that is carried into a manuscript. One entry went
further and named a MolSysMT paper, with a title, a year and an author, that
does not exist.

A citation library that invents a detail is worse than one that has none. These
tests hold the shipped data to its sources, and hold the documentation to the
same rule, because the guide host libraries copy taught the defect too.
"""

import re
from pathlib import Path

import pytest

import ackredit
from ackredit.core.registry import Registry
from ackredit.core.session import current_session
from ackredit.core.standard_injections import STANDARD_INJECTIONS

ROOT = Path(__file__).resolve().parents[1]

ITEMS = [(pkg, item) for pkg, items in STANDARD_INJECTIONS.items() for item in items]
IDS = [f"{pkg}:{item['id']}" for pkg, item in ITEMS]

# Strings that describe how to print an author list rather than naming someone.
TRUNCATIONS = ("et al", "et. al", "and others", "others", "...", "…", "etal")

# BibTeX entry types the renderer knows. An unmapped type falls back silently.
KNOWN_TYPES = {"article", "software", "repo", "web", "dataset", "other", "book"}


def is_truncation(name: str) -> bool:
    stripped = name.strip().strip(".").lower()
    return any(stripped == marker.strip(".") for marker in TRUNCATIONS)


@pytest.fixture(autouse=True)
def _clean():
    current_session().clear()
    Registry.items.clear()
    yield
    current_session().clear()
    Registry.items.clear()


@pytest.mark.parametrize("pkg,item", ITEMS, ids=IDS)
def test_no_shipped_author_is_a_truncation(pkg, item):
    """The defect. `"et al."` is not a person and must not sit in `authors`."""
    for name in item.get("authors", []):
        assert not is_truncation(name), (
            f"{item['id']} lists {name!r} as an author of a work. BibTeX will "
            f"render it as a person; abbreviating a list is the bibliography "
            f"style's decision, not the data's"
        )


@pytest.mark.parametrize("pkg,item", ITEMS, ids=IDS)
def test_every_shipped_item_can_be_cited(pkg, item):
    assert item.get("id"), f"{pkg} ships an item with no id"
    assert item.get("title"), f"{item['id']} has no title"
    assert item.get("authors"), f"{item['id']} names nobody"
    assert item.get("type") in KNOWN_TYPES, (
        f"{item['id']} has type {item.get('type')!r}, which no renderer maps"
    )
    assert item.get("doi") or item.get("url"), (
        f"{item['id']} gives neither a DOI nor a URL, so a reader cannot reach it"
    )


@pytest.mark.parametrize("pkg,item", ITEMS, ids=IDS)
def test_an_article_says_where_it_was_published(pkg, item):
    if item["type"] == "article":
        assert item.get("journal"), f"{item['id']} is an article with no journal"
        assert item.get("year"), f"{item['id']} is an article with no year"


def test_nothing_shipped_renders_as_an_invented_person():
    """End to end: the output a user would paste into a manuscript."""
    for _, item in ITEMS:
        ackredit.register_item(**item)
        ackredit.track_item(item["id"], used_by="run")

    bibtex = ackredit.report(format="bibtex")
    for marker in ("and et al", "and others", "{et al.}"):
        assert marker not in bibtex, f"the bibliography contains {marker!r}"


def test_the_molsysmt_entry_is_the_software_molsysmt_asks_for():
    """It used to name a 2024 article by "Diego" that does not exist.

    MolSysMT's own CITATION.cff asks to be cited as software, by both authors,
    through its Zenodo DOI.
    """
    (item,) = STANDARD_INJECTIONS["molsysmt"]
    assert item["type"] == "software"
    assert item["doi"] == "10.5281/zenodo.1298752"
    assert item["authors"] == ["Prada-Gracia, Diego", "Moreno-Vargas, Liliana M."]
    assert "paper" not in item["id"]


# Authors written into a list literal, in code or in documentation. The examples
# are what a host library copies, and the guide's example taught `"et al."`.
_AUTHOR_LIST = re.compile(r"""authors["'\s]*[=:]\s*\[(.*?)\]""", re.DOTALL)

SCANNED = sorted(
    path
    for pattern in ("**/*.py", "**/*.md", "**/*.rst")
    for path in ROOT.glob(pattern)
    # The archive records history, which the reporting protocol forbids rewriting.
    if ".git" not in path.parts and "archive" not in path.parts
)


@pytest.mark.parametrize("path", SCANNED, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_example_teaches_a_truncation_as_an_author(path):
    text = path.read_text(encoding="utf-8")
    for match in _AUTHOR_LIST.finditer(text):
        for name in re.findall(r"""["']([^"']+)["']""", match.group(1)):
            assert not is_truncation(name), (
                f"{path.relative_to(ROOT)} writes {name!r} into an author list. "
                f"Whatever copies this example inherits the defect"
            )
