"""Text bound for a TeX engine must survive it.

Citation metadata is prose: journal names contain ampersands, titles contain
percentages and underscores. Emitted unescaped, they do not fail loudly. They
produce a bibliography that is subtly wrong, and that error is carried into a
manuscript.
"""

import pytest

from ackredit import register_item, report, track_item
from ackredit.formats._latex import escape

SPECIALS = [
    ("Surfaces & Pockets", r"Surfaces \& Pockets"),
    ("Computing in Science & Engineering", r"Computing in Science \& Engineering"),
    ("100% Theory", r"100\% Theory"),
    ("snake_case_name", r"snake\_case\_name"),
    ("C# and F#", r"C\# and F\#"),
]

PRESERVED = [
    # Already escaped by the author, or by a .bib file we loaded.
    r"already \& escaped",
    r"already \% escaped",
    # Intentional mathematics in a scientific title.
    r"$\alpha$-helix",
    r"\textbf{bold}",
]


@pytest.mark.parametrize("raw,expected", SPECIALS)
def test_specials_are_escaped(raw, expected):
    assert escape(raw) == expected


@pytest.mark.parametrize("raw", PRESERVED)
def test_intentional_latex_is_left_alone(raw):
    assert escape(raw) == raw


@pytest.mark.parametrize("raw,_expected", SPECIALS)
def test_escaping_is_idempotent(raw, _expected):
    """load_bibtex reads escaped text; rendering it again must not double-escape."""
    once = escape(raw)
    assert escape(once) == once


def test_bibtex_output_escapes_every_field():
    register_item(
        id="esc:bib",
        type="article",
        title="Surfaces & Pockets",
        journal="Computing in Science & Engineering",
        authors=["Smith & Sons"],
        note="100% reproducible",
        year=2024,
    )
    track_item("esc:bib")

    rendered = report(format="bibtex")
    entry = [block for block in rendered.split("\n\n") if "esc-bib" in block][0]

    assert r"Surfaces \& Pockets" in entry
    assert r"Computing in Science \& Engineering" in entry
    assert r"Smith \& Sons" in entry
    assert r"100\% reproducible" in entry
    # No bare special survives inside the entry's field values.
    for line in entry.splitlines():
        if "=" not in line:
            continue
        value = line.split("=", 1)[1]
        for index, character in enumerate(value):
            if character in "&%#_":
                assert value[index - 1] == "\\", f"unescaped {character!r} in {line!r}"


def test_latex_output_escapes_titles_and_callers():
    register_item(id="esc:tex", type="article", title="Surfaces & 100% Pockets")
    track_item("esc:tex", used_by="my_module.run_analysis")

    rendered = report(format="latex")

    assert r"Surfaces \& 100\% Pockets" in rendered
    assert r"my\_module.run\_analysis" in rendered


def test_citation_keys_are_safe_as_printed_labels():
    """With no author, natbib prints the key as the label. A bare underscore
    there is read in math mode and aborts the compilation, and auto-discovered
    items frequently have no author."""
    register_item(
        id="key_check:with_underscore", type="article", title="No author here"
    )
    track_item("key_check:with_underscore")

    rendered = report(format="bibtex")

    assert "key-check-with-underscore" in rendered
    assert "key_check" not in rendered


def test_an_unparseable_author_name_is_brace_protected():
    """BibTeX reads at most two commas in a name; more is an error that aborts
    the run. Package metadata hands us whole comma-separated author lists."""
    register_item(
        id="many:commas",
        type="article",
        title="Metadata derived",
        authors=["A Person, B Person, C Person, D Person"],
    )
    track_item("many:commas")

    entry = [b for b in report(format="bibtex").split("\n\n") if "many-commas" in b][0]

    assert "{{A Person, B Person, C Person, D Person}}" in entry


def test_ordinary_author_names_are_not_brace_protected():
    register_item(
        id="normal:author", type="article", title="T", authors=["Smith, John"]
    )
    track_item("normal:author")

    entry = [b for b in report(format="bibtex").split("\n\n") if "normal-author" in b][
        0
    ]

    assert "author = {Smith, John}" in entry


def test_metadata_author_strings_are_split_into_names():
    from ackredit.core.hooks import _split_authors

    assert _split_authors("Ana Ruiz, Luis Gómez, Others") == [
        "Ana Ruiz",
        "Luis Gómez",
        "Others",
    ]
    assert _split_authors(None) == []
    assert _split_authors("") == []
