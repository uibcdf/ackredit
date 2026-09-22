"""CSL-JSON is what a reference manager reads, so it must carry a reference.

Two defects, measured. It raised `ValueError` on a year Ackredit itself
produces: `ACKREDIT-W009` documents that a biblatex date range and "in press"
reach a renderer legitimately, and its hint promises at worst that the value is
rendered unchanged. And it mapped a short fixed list, so a book arrived with no
publisher, no ISBN and no series, and a conference paper with no booktitle and
no editor — a reference a manager cannot format.

Unlike BibTeX nothing can simply be passed through here, because CSL-JSON is a
schema and a processor has no use for a key it does not define. So the mapping
is bounded, and these tests are what say it is wide enough.
"""

import json
import tempfile
from pathlib import Path

import pytest

import ackredit
from ackredit.core.registry import Registry

SOURCE = """\
@book{b1, author = {Knuth, Donald E.}, title = {The TeXbook},
      publisher = {Addison-Wesley}, year = {1984}, isbn = {0-201-13447-0},
      series = {Computers and Typesetting}, edition = {2nd}}

@inproceedings{c1, author = {Hunter, John D.}, title = {Matplotlib},
      booktitle = {Proc. SciPy}, pages = {90--95}, year = {2007},
      editor = {Varoquaux, G.}}

@phdthesis{t1, author = {Doe, J.}, title = {A Thesis},
      school = {Some University}, year = {2020}}
"""


@pytest.fixture
def records(tmp_path, clean_registry):
    path = tmp_path / "in.bib"
    path.write_text(SOURCE, encoding="utf-8")
    ackredit.load_bibtex(str(path))
    for item_id in Registry.items:
        ackredit.track_item(item_id)
    return {
        record["id"]: record
        for record in json.loads(ackredit.report(format="csl-json"))
    }


# --- a year that is not a number ------------------------------------------


@pytest.mark.parametrize("fmt", sorted(ackredit.available_formats()))
def test_no_format_raises_on_a_year_ackredit_kept_as_text(fmt, clean_registry):
    """`csl-json` was the one of seven that raised."""
    ackredit.register_item(id="x:1", type="article", title="T", year="in press")
    ackredit.track_item("x:1")
    ackredit.report(format=fmt)


def test_a_year_that_is_not_a_number_becomes_a_literal_date(clean_registry):
    """CSL has a literal date for exactly this."""
    ackredit.register_item(id="x:1", type="article", title="T", year="in press")
    ackredit.track_item("x:1")
    (record,) = json.loads(ackredit.report(format="csl-json"))

    assert record["issued"] == {"literal": "in press"}


def test_a_numeric_year_still_becomes_date_parts(clean_registry):
    ackredit.register_item(id="x:1", type="article", title="T", year=2024)
    ackredit.track_item("x:1")
    (record,) = json.loads(ackredit.report(format="csl-json"))

    assert record["issued"] == {"date-parts": [[2024]]}


def test_a_biblatex_date_range_survives(clean_registry):
    """The other case ACKREDIT-W009 names."""
    ackredit.register_item(id="x:1", type="article", title="T", year="2020/2021")
    ackredit.track_item("x:1")
    (record,) = json.loads(ackredit.report(format="csl-json"))

    assert record["issued"] == {"literal": "2020/2021"}


# --- the fields a manager formats with ------------------------------------


@pytest.mark.parametrize(
    "item_id,field,expected",
    [
        ("b1", "publisher", "Addison-Wesley"),
        ("b1", "ISBN", "0-201-13447-0"),
        ("b1", "collection-title", "Computers and Typesetting"),
        ("b1", "edition", "2nd"),
        ("c1", "container-title", "Proc. SciPy"),
        ("c1", "page", "90--95"),
        ("t1", "publisher", "Some University"),
    ],
)
def test_every_field_csl_defines_arrives(records, item_id, field, expected):
    assert records[item_id][field] == expected


def test_an_editor_is_a_name_not_a_string(records):
    """Editors are people, like authors, and a manager sorts and abbreviates
    them the same way."""
    assert records["c1"]["editor"] == [{"family": "Varoquaux", "given": "G."}]


def test_a_journal_wins_over_a_booktitle_for_the_container(clean_registry):
    """One CSL field, and an entry that somehow carries both."""
    ackredit.register_item(
        id="x:1", type="article", title="T", journal="A Journal", booktitle="A Book"
    )
    ackredit.track_item("x:1")
    (record,) = json.loads(ackredit.report(format="csl-json"))

    assert record["container-title"] == "A Journal"


# --- what the entry said it was -------------------------------------------


@pytest.mark.parametrize(
    "entry,expected",
    [
        ("@book{x, title={T}}", "book"),
        ("@inproceedings{x, title={T}}", "paper-conference"),
        ("@phdthesis{x, title={T}}", "thesis"),
        ("@techreport{x, title={T}}", "report"),
        ("@incollection{x, title={T}}", "chapter"),
        ("@article{x, title={T}}", "article-journal"),
    ],
)
def test_the_entry_type_reaches_csls_vocabulary(entry, expected, clean_registry):
    """All of these were "document", and a manager cannot format a book it has
    been told is a document."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "in.bib"
        path.write_text(entry, encoding="utf-8")
        ackredit.load_bibtex(str(path))

    ackredit.track_item("x")
    (record,) = json.loads(ackredit.report(format="csl-json"))
    assert record["type"] == expected


def test_an_item_that_came_from_no_file_keeps_ackredits_mapping(clean_registry):
    ackredit.register_item(id="x:1", type="software", title="T")
    ackredit.track_item("x:1")
    (record,) = json.loads(ackredit.report(format="csl-json"))

    assert record["type"] == "software"


def test_no_ackredit_bookkeeping_reaches_the_schema(records):
    """A CSL processor has no use for a key it does not define."""
    for record in records.values():
        assert not [key for key in record if key.startswith("_")]
        assert "authors" not in record
