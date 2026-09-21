"""CSL-JSON exists to be read by a machine, so its names must be readable.

Every author was emitted as `{"literal": "Harris, Charles R."}`, and a literal
tells a reference manager the name cannot be decomposed. Zotero, Mendeley and
EndNote could then not sort by surname, not abbreviate to "Harris, C. R.", and
not apply a journal's name style.

The other half matters as much: a string that does not decompose must stay
literal. "SciPy 1.0 Contributors" split at the last space would become the given
name "SciPy 1.0" of a family called "Contributors", and inventing a person is
the defect this library exists to prevent.
"""

import json

import pytest

import ackredit
from ackredit.formats._names import csl_name

STRUCTURED = [
    ("Harris, Charles R.", "Harris", "Charles R."),
    ("van der Walt, Stéfan J.", "van der Walt", "Stéfan J."),
    ("Polat, İlhan", "Polat", "İlhan"),
    ("Moreno-Vargas, Liliana M.", "Moreno-Vargas", "Liliana M."),
    ("  Hunter,  John D.  ", "Hunter", "John D."),
]

LITERAL = [
    "SciPy 1.0 Contributors",
    "UIBCDF Lab",
    "Travis E. Oliphant",
    "Plato",
    "Smith, Jr., John",
    "Harris,",
    ", Charles",
]


@pytest.mark.parametrize("raw,family,given", STRUCTURED, ids=[n[0] for n in STRUCTURED])
def test_a_family_given_name_decomposes(raw, family, given):
    assert csl_name(raw) == {"family": family, "given": given}


@pytest.mark.parametrize("raw", LITERAL)
def test_anything_else_stays_literal(raw):
    """A literal name is less useful. An invented one is wrong."""
    assert set(csl_name(raw)) == {"literal"}


@pytest.mark.parametrize("raw,family,given", STRUCTURED, ids=[n[0] for n in STRUCTURED])
def test_nothing_is_added_or_dropped_when_it_decomposes(raw, family, given):
    """The two parts put back together are the name that was registered."""
    name = csl_name(raw)
    assert f"{name['family']}, {name['given']}" == " ".join(raw.split())


@pytest.mark.parametrize("raw", LITERAL)
def test_a_literal_is_the_string_that_was_registered(raw):
    assert csl_name(raw)["literal"] == raw.strip()


def test_a_name_object_passes_through():
    """A host that knows CSL may pass one; wrapping it would produce a name
    that is not a string."""
    given = {"family": "Harris", "given": "Charles R.", "suffix": "Jr."}
    assert csl_name(given) == given


# --- through the renderer -------------------------------------------------


def report_authors(authors) -> list[dict]:
    ackredit.register_item(id="x:1", type="article", title="T", authors=authors)
    ackredit.track_item("x:1")
    return json.loads(ackredit.report(format="csl-json"))[0]["author"]


def test_the_renderer_emits_structured_names():
    assert report_authors(["Harris, Charles R."]) == [
        {"family": "Harris", "given": "Charles R."}
    ]


def test_order_and_count_survive_a_mixed_list():
    authors = ["Virtanen, Pauli", "SciPy 1.0 Contributors", "Gommers, Ralf"]
    emitted = report_authors(authors)

    assert len(emitted) == len(authors)
    assert emitted[1] == {"literal": "SciPy 1.0 Contributors"}
    assert [name.get("family", name.get("literal")) for name in emitted] == [
        "Virtanen",
        "SciPy 1.0 Contributors",
        "Gommers",
    ]


def test_every_shipped_author_becomes_a_usable_name(clean_registry):
    """The data Ackredit injects is the data most users will see cited."""
    from ackredit.core.standard_injections import STANDARD_INJECTIONS

    for items in STANDARD_INJECTIONS.values():
        for item in items:
            ackredit.register_item(**item)
            ackredit.track_item(item["id"])

    for record in json.loads(ackredit.report(format="csl-json")):
        for name in record["author"]:
            assert set(name) in ({"family", "given"}, {"literal"}), name
            assert all(value.strip() for value in name.values())


def test_the_collective_author_scipy_ships_is_not_split(clean_registry):
    from ackredit.core.standard_injections import STANDARD_INJECTIONS

    (scipy,) = STANDARD_INJECTIONS["scipy"]
    ackredit.register_item(**scipy)
    ackredit.track_item(scipy["id"])

    (record,) = json.loads(ackredit.report(format="csl-json"))
    assert record["author"][-1] == {"literal": "SciPy 1.0 Contributors"}
    assert record["author"][0] == {"family": "Virtanen", "given": "Pauli"}
