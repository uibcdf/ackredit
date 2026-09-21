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

# Text a .bib file already carries in LaTeX form. Nothing here may be touched,
# and none of it is distinguishable from prose by looking at the characters:
# only the item's provenance separates "$\alpha$-helix" from "Cost in $ per unit".
LATEX_SOURCE = [
    r"$\alpha$-helix",
    r"\textbf{bold}",
    r"already \& escaped",
    r"50\% yield",
]

# Values this module produced. Escaping must be idempotent so a field that passes
# through two renderers is not escaped twice.
ALREADY_ESCAPED = [
    r"already \& escaped",
    r"already \% escaped",
    r"a\textasciitilde{}b",
]


@pytest.mark.parametrize("raw,expected", SPECIALS)
def test_specials_are_escaped(raw, expected):
    assert escape(raw) == expected


@pytest.mark.parametrize("raw", LATEX_SOURCE)
def test_latex_source_is_never_touched(raw):
    """Provenance decides, not the characters."""
    assert escape(raw, latex_source=True) == raw


@pytest.mark.parametrize("raw", ALREADY_ESCAPED)
def test_escaping_what_this_module_produced_changes_nothing(raw):
    assert escape(raw) == raw


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Cost in $ per sample", r"Cost in \$ per sample"),
        ("a~b", r"a\textasciitilde{}b"),
        ("x^2", r"x\textasciicircum{}2"),
        ("A {curly} title", r"A \{curly\} title"),
    ],
)
def test_plain_text_specials_are_escaped_too(raw, expected):
    """These were left alone while escaping guessed per character. An unpaired
    dollar is never intentional mathematics; it opens math mode and aborts."""
    assert escape(raw) == expected


def test_a_backslash_does_not_re_escape_its_own_replacement():
    """Sequential replacement turned this into 'C:\\textbackslash\\{\\}path'."""
    assert escape(r"C:\path") == r"C:\textbackslash{}path"


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


@pytest.mark.parametrize(
    "name,protected",
    [
        ("Smith, John", False),
        # "von Last, Jr, First" is BibTeX's own three-part form: two commas, valid.
        ("van der Berg, Jr, Johannes", False),
        ("A Person, B Person, C Person, D Person", True),
    ],
)
def test_only_a_name_bibtex_cannot_read_is_brace_protected(name, protected):
    """Protection costs the name its sorting key and initials, so it is used
    only when BibTeX genuinely cannot parse it."""
    from ackredit.formats.bibtex import _bibtex_name

    assert _bibtex_name(name).startswith("{") is protected


def test_an_unparseable_author_name_is_brace_protected():
    """BibTeX reads at most two commas in a name; a third is an error that
    aborts the run. Package metadata hands us whole comma-separated lists."""
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


@pytest.mark.parametrize(
    "raw,expected",
    [
        # Every part carries a space, so these are people, not one name.
        ("Ana Ruiz, Luis Gómez", ["Ana Ruiz", "Luis Gómez"]),
        # "Last, First": splitting would invent an author who does not exist.
        ("Prada, Diego", ["Prada, Diego"]),
        ("Prada Gracia, Diego", ["Prada Gracia, Diego"]),
        ("Smith, J., Doe, A.", ["Smith, J., Doe, A."]),
        # No comma at all.
        ("Travis E. Oliphant et al.", ["Travis E. Oliphant et al."]),
        (None, []),
        ("", []),
    ],
)
def test_a_free_text_author_field_is_split_only_when_it_is_safe(raw, expected):
    from ackredit.core.hooks import _split_authors

    assert _split_authors(raw) == expected


def test_author_email_is_preferred_because_it_is_unambiguous():
    """`Name <email>` pairs can be parsed exactly; free text cannot."""
    from ackredit.core.hooks import _authors_from_metadata

    meta = {
        "Author-email": "Adam Turner <aa@example.org>, Georg Brandl <georg@example.org>",
        "Author": "Turner, Adam",
    }
    assert _authors_from_metadata(meta) == ["Adam Turner", "Georg Brandl"]


def test_free_text_author_is_used_when_there_is_no_structured_field():
    from ackredit.core.hooks import _authors_from_metadata

    assert _authors_from_metadata({"Author": "Prada, Diego"}) == ["Prada, Diego"]
    assert _authors_from_metadata({}) == []


def test_a_bib_file_survives_a_round_trip_untouched(tmp_path):
    """Provenance exists for this: a .bib file's fields are already LaTeX, and
    escaping them again would turn its '\\&' into a literal backslash."""
    from ackredit import load_bibtex

    source = tmp_path / "in.bib"
    source.write_text(
        "@article{roundtrip,\n"
        "  title = {Surfaces \\& Pockets at 50\\% with $\\alpha$-helix},\n"
        "  author = {Prada, Diego},\n"
        "  year = {2024}\n"
        "}\n"
    )

    load_bibtex(str(source))
    track_item("roundtrip")
    rendered = report(format="bibtex")

    assert r"Surfaces \& Pockets at 50\% with $\alpha$-helix" in rendered
    assert r"\\&" not in rendered
    # The provenance marker is internal and must not reach any output.
    assert "_source" not in rendered


def test_the_provenance_marker_never_reaches_a_report(tmp_path, clean_registry):

    source = tmp_path / "in.bib"
    source.write_text("@article{marker, title = {A Title}, year = {2024}}\n")
    from ackredit import load_bibtex

    load_bibtex(str(source))
    track_item("marker")

    for fmt in ("markdown", "text", "bibtex", "json", "csl-json", "latex"):
        assert "_source" not in report(format=fmt), fmt
