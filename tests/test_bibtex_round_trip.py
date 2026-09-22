r"""A `.bib` file loaded and written back must still be the same file.

Two causes, one outcome. `_parse_entry` mapped `@book` to Ackredit's `other`,
and the renderer mapped `other` to `@misc`: Ackredit's vocabulary has six types
and BibTeX has fourteen, so anything outside the overlap was flattened. And the
renderer emitted a list of fields chosen in advance — `journal`, `volume`,
`number` and `pages` only when the type was `article` — so the publisher of a
book, the editor of a conference paper and the school of a thesis were dropped,
although the parser had stored all three.

That is the shape of `uibcdf/ackredit#27`, where the `json` format emitted six
fixed keys and discarded the DOI. It is not only about round trips: a host
registering an item with `publisher=` lost it the same way.
"""

import re

import pytest

import ackredit
from ackredit.core.registry import Registry

SOURCE = """\
@book{b1,
  author = {Knuth, Donald E.},
  title = {The {TeX}book},
  publisher = {Addison-Wesley},
  year = {1984},
  isbn = {0-201-13447-0},
  series = {Computers and Typesetting}
}

@inproceedings{c1,
  author = {Hunter, John D.},
  title = {Matplotlib in {Python}},
  booktitle = {Proceedings of SciPy},
  pages = {90--95},
  year = {2007},
  editor = {Varoquaux, G.}
}

@phdthesis{t1,
  author = {Doe, J.},
  title = {A Thesis},
  school = {Some University},
  year = {2020}
}
"""


@pytest.fixture
def rendered(tmp_path, clean_registry):
    path = tmp_path / "in.bib"
    path.write_text(SOURCE, encoding="utf-8")
    ackredit.load_bibtex(str(path))
    for item_id in Registry.items:
        ackredit.track_item(item_id)
    return ackredit.report(format="bibtex")


@pytest.mark.parametrize("entry", ["@book{b1,", "@inproceedings{c1,", "@phdthesis{t1,"])
def test_the_entry_type_comes_back(rendered, entry):
    """`@book` used to be written back as `@misc`."""
    assert entry in rendered


@pytest.mark.parametrize(
    "field",
    [
        "publisher = {Addison-Wesley}",
        "isbn = {0-201-13447-0}",
        "series = {Computers and Typesetting}",
        "booktitle = {Proceedings of SciPy}",
        "pages = {90--95}",
        "editor = {Varoquaux, G.}",
        "school = {Some University}",
    ],
)
def test_every_field_comes_back(rendered, field):
    assert field in rendered


def test_nothing_in_the_file_is_lost(rendered, tmp_path):
    """Read both sides as key-value pairs and compare, so the check is the
    claim rather than a list of fields someone remembered to assert."""
    pattern = re.compile(r"^\s*(\w+)\s*=\s*\{(.*)\}[,]?$", re.MULTILINE)
    original = {
        (key.lower(), value.rstrip("},")) for key, value in pattern.findall(SOURCE)
    }
    produced = {
        (key.lower(), value.rstrip("},")) for key, value in pattern.findall(rendered)
    }

    assert not original - produced, f"lost: {sorted(original - produced)}"


def test_a_howpublished_is_not_invented_for_an_entry_that_says_what_it_is(rendered):
    """`howpublished` names the kind BibTeX cannot express in its entry type.
    A `@book` expresses it, so adding one would be noise."""
    assert "howpublished" not in rendered


# --- items that did not come from a .bib file -----------------------------


def test_a_registered_field_is_not_dropped(clean_registry):
    """The same defect without a file: a host registers a publisher and the
    renderer discards it."""
    ackredit.register_item(
        id="x:1",
        type="other",
        title="A Book",
        authors=["Ruiz, Ana"],
        publisher="A Press",
        edition="2nd",
    )
    ackredit.track_item("x:1")
    rendered = ackredit.report(format="bibtex")

    assert "publisher = {A Press}" in rendered
    assert "edition = {2nd}" in rendered


def test_ackredits_own_keys_are_not_emitted_as_fields(clean_registry):
    ackredit.register_item(id="x:1", type="software", title="T", authors=["A, B"])
    ackredit.track_item("x:1")
    rendered = ackredit.report(format="bibtex")

    for key in ("id = ", "type = ", "authors = ", "_source", "_bibtex_type"):
        assert key not in rendered


def test_a_type_ackredit_knows_still_maps_when_there_is_no_original(clean_registry):
    """Nothing changes for an item a host registered rather than loaded."""
    ackredit.register_item(id="x:1", type="dataset", title="A Dataset")
    ackredit.track_item("x:1")
    rendered = ackredit.report(format="bibtex")

    assert "@misc{x-1," in rendered
    assert "howpublished = {Dataset}" in rendered


def test_a_field_from_a_file_is_still_passed_through_unescaped(
    tmp_path, clean_registry
):
    """The provenance rule survives: a .bib file's fields are LaTeX already."""
    path = tmp_path / "in.bib"
    path.write_text(r"@book{b, title = {50\% off}, publisher = {A \& B}}")
    ackredit.load_bibtex(str(path))
    ackredit.track_item("b")
    rendered = ackredit.report(format="bibtex")

    assert r"publisher = {A \& B}" in rendered
    assert r"\textbackslash" not in rendered
