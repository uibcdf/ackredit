r"""A `.bib` file must survive being read and written again.

Fields were read with `(\w+)\s*=\s*(\{.*?\}|".*?"|[^,]+)`. The braced branch is
non-greedy, so it stopped at the first closing brace, and brace protection is
the ordinary BibTeX idiom for acronyms and proper nouns — it is what stops a
style lowercasing them, and every reference manager emits it:

    title = {The {DNA} helix}   ->   'The {DNA'

The report was then not merely wrong but invalid BibTeX, because the braces no
longer balanced, so a file loaded from Zotero and re-emitted would not compile.
`_source = "bibtex"` passes these fields through unescaped, which is correct and
is also why nothing downstream repaired it.
"""

import pytest

import ackredit
from ackredit.core.registry import Registry, _split_bibtex_authors


@pytest.fixture(autouse=True)
def _own_registry(clean_registry):
    """Each case reads its own file into an empty registry."""


def load(tmp_path, text: str) -> dict:
    path = tmp_path / "in.bib"
    path.write_text(text, encoding="utf-8")
    ackredit.load_bibtex(str(path))
    return Registry.items


def balanced(text: str) -> bool:
    depth = 0
    for char in text:
        depth += (char == "{") - (char == "}")
        if depth < 0:
            return False
    return depth == 0


# --- the defect -----------------------------------------------------------


@pytest.mark.parametrize(
    "field,expected",
    [
        ("{The {DNA} helix}", "The {DNA} helix"),
        ("{Analysis with {MolSysMT}}", "Analysis with {MolSysMT}"),
        ("{{DNA} and {RNA} in {Python}}", "{DNA} and {RNA} in {Python}"),
        ("{{A Fully Protected Title}}", "{A Fully Protected Title}"),
        ("{Nested {deeply {inside}} here}", "Nested {deeply {inside}} here"),
    ],
)
def test_a_protected_word_does_not_truncate_the_value(tmp_path, field, expected):
    items = load(tmp_path, f"@article{{a, title = {field}, year = {{2024}}}}")
    assert items["a"]["title"] == expected


def test_the_fields_after_a_protected_word_are_still_read(tmp_path):
    items = load(
        tmp_path,
        "@article{a, title = {The {DNA} helix}, year = {2024}, journal = {Nature}}",
    )
    assert items["a"]["year"] == 2024
    assert items["a"]["journal"] == "Nature"


def test_the_inner_braces_are_kept(tmp_path):
    """They are the citation: dropping them lets a style lowercase the acronym."""
    items = load(tmp_path, "@article{a, title = {The {DNA} helix}}")
    assert "{DNA}" in items["a"]["title"]


# --- the round trip -------------------------------------------------------


def test_what_is_written_back_has_balanced_braces(tmp_path):
    """The failure that reaches a user: the re-emitted file does not compile."""
    load(
        tmp_path,
        "@article{rt, title = {Analysis with {MolSysMT}}, "
        "author = {Prada-Gracia, Diego}, year = {2024}, journal = {J}}",
    )
    ackredit.track_item("rt")
    rendered = ackredit.report(format="bibtex")

    assert balanced(rendered), rendered
    assert "title = {Analysis with {MolSysMT}}" in rendered


def test_a_corporate_author_survives_the_round_trip(tmp_path):
    load(tmp_path, "@misc{e, author = {{The SciPy Community}}, title = {SciPy}}")
    ackredit.track_item("e")
    rendered = ackredit.report(format="bibtex")

    assert balanced(rendered)
    assert "{The SciPy Community}" in rendered


# --- authors --------------------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        ("Harris, C. R. and Millman, K. J.", ["Harris, C. R.", "Millman, K. J."]),
        ("{Smith and Sons} and Jones, A.", ["{Smith and Sons}", "Jones, A."]),
        ("{The SciPy Community}", ["{The SciPy Community}"]),
        ("Solo, H.", ["Solo, H."]),
        ("A and B AND C", ["A", "B", "C"]),
        ("Anderson, A. and Andrews, B.", ["Anderson, A.", "Andrews, B."]),
    ],
    ids=["plain", "braced-and", "corporate", "one", "case", "and-inside-a-name"],
)
def test_and_separates_names_only_outside_braces(value, expected):
    """`{Smith and Sons}` is one author, and the braces are what say so."""
    assert _split_bibtex_authors(value) == expected


# --- shapes a .bib file legitimately has ----------------------------------


def test_a_quoted_value_is_read(tmp_path):
    items = load(tmp_path, '@article{g, title = "A {quoted} title", year = 2024}')
    assert items["g"]["title"] == "A {quoted} title"
    assert items["g"]["year"] == 2024


def test_a_value_spanning_lines_becomes_one_line(tmp_path):
    """A TeX engine collapses this whitespace; so does the stored value."""
    items = load(tmp_path, "@article{h,\n  title = {A very\n    long title}\n}")
    assert items["h"]["title"] == "A very long title"


def test_a_trailing_comma_is_not_a_field(tmp_path):
    items = load(tmp_path, "@article{c, title = {T}, year = {2024},}")
    assert items["c"]["title"] == "T"


def test_two_entries_are_both_read(tmp_path):
    items = load(tmp_path, "@article{d, title={One}}\n@book{e, title={Two}}")
    assert items["d"]["title"] == "One"
    assert items["e"]["title"] == "Two"


def test_an_at_sign_inside_a_value_is_not_a_new_entry(tmp_path):
    items = load(tmp_path, "@article{f, title = {Email: a@b.c}, year={2024}}")
    assert items["f"]["title"] == "Email: a@b.c"


def test_an_unclosed_entry_is_reported_rather_than_dropped(tmp_path):
    """An entry with no closing brace cannot be read, and used to vanish in
    silence: the user got fewer citations and nothing said so."""
    from ackredit._private.smonitor.warnings import BibtexEntryWarning

    with pytest.warns(BibtexEntryWarning, match="article"):
        items = load(
            tmp_path, "@article{ok, title={T}}\n@article{u, title = {Never closed"
        )

    assert items["ok"]["title"] == "T", "the entries before it are still loaded"
    assert "u" not in items
