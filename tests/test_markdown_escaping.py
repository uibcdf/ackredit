"""The default report must not be markup the author never wrote.

`report()` returns Markdown by default and `standards/ACKREDIT_GUIDE.md` tells
every host library to expose `cite(format="markdown")`, so this is the output
almost every user meets first — and nothing in it was escaped. A `[` in a title
closed the link early, an asterisk became emphasis, and `<script>` reached a
renderer that passes raw HTML through.

This is the third renderer in the family. LaTeX was #7 and #9, HTML was #25, and
both were found by looking. This one was never looked at because its output
reads plausibly.
"""

import pytest

import ackredit
from ackredit.formats._markdown import destination, escape, safe_link

HOSTILE = "<script>alert('x')</script>"


def render(**fields) -> str:
    item = {"id": "x:1", "type": "article", "title": "A Title"}
    item.update(fields)
    ackredit.register_item(**item)
    ackredit.track_item("x:1", used_by=fields.pop("_used_by", "run"))
    return ackredit.report(format="markdown")


def body(markdown: str) -> list[str]:
    return [line for line in markdown.splitlines() if line.startswith(("- ", "  - "))]


# --- what a field may not become -----------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", f"Pockets [see note] {HOSTILE}"),
        ("authors", [f"Ann *Bold* O'Neill {HOSTILE}"]),
        ("year", f"2024 {HOSTILE}"),
        ("note", f"A note {HOSTILE}"),
    ],
)
def test_no_field_reaches_the_report_as_markup(field, value):
    report = render(**{field: value})
    assert HOSTILE not in report
    assert "<script>" not in report


def test_the_caller_name_is_escaped_too():
    ackredit.register_item(id="x:1", title="A Title")
    ackredit.track_item("x:1", used_by="run *now* [here]")
    assert "run \\*now\\* \\[here\\]" in ackredit.report(format="markdown")


def test_brackets_in_a_title_do_not_close_the_link():
    """The defect: `[**Pockets [see note]**](url)` ends the link text early."""
    (line,) = [
        line
        for line in body(render(title="Pockets [see note]", doi="10.1/x"))
        if line.startswith("- ")
    ]
    assert line == "- [**Pockets \\[see note\\]**](https://doi.org/10.1/x)"


def test_asterisks_stay_asterisks():
    assert "Rate \\*k\\* and 2\\*3" in render(title="Rate *k* and 2*3", doi="10.1/z")


def test_a_backslash_is_escaped_before_anything_it_would_escape():
    """`\\` first, or the escaping escapes its own output."""
    assert escape("C:\\path") == "C:\\\\path"


def test_a_newline_in_a_note_does_not_end_the_list():
    """A CITATION.cff folded scalar carries newlines into an item's note."""
    report = render(note="line one\nline two", doi="10.1/v")
    assert "  - Note: line one line two" in report
    assert len(body(report)) == 3


# --- links ----------------------------------------------------------------


def test_a_url_that_cannot_be_followed_is_not_linked():
    report = render(url="javascript:alert(1)")
    assert "](" not in report
    assert "**A Title**" in report, "the citation is still reported"


def test_a_real_url_is_linked():
    assert "](https://example.org/a)" in render(url="https://example.org/a")


def test_a_doi_builds_its_link():
    assert "](https://doi.org/10.1/x)" in render(doi="10.1/x")


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://e.org/a", "https://e.org/a"),
        ("https://e.org/a(b)c", "<https://e.org/a(b)c>"),
        ("https://e.org/a b", "<https://e.org/a b>"),
        ("https://e.org/a<b>c", "https://e.org/a%3Cb%3Ec"),
        ("https://e.org/a<b>(c)", "<https://e.org/a%3Cb%3E(c)>"),
    ],
)
def test_a_destination_is_written_so_a_parser_reads_all_of_it(url, expected):
    assert destination(url) == expected


def test_a_doi_containing_a_parenthesis_does_not_break_the_link():
    """The DOI is interpolated into the link we build, and is not ours."""
    assert "](<https://doi.org/10.1/a(b)>)" in render(doi="10.1/a(b)")


# --- the escaper itself ---------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("a [b] c", "a \\[b\\] c"),
        ("*emphasis*", "\\*emphasis\\*"),
        ("snake_case", "snake\\_case"),
        ("`code`", "\\`code\\`"),
        ("<b>", "\\<b\\>"),
        ("  spaced  out  ", "spaced out"),
        (2024, "2024"),
    ],
)
def test_escape_covers_what_changes_rendering(raw, expected):
    assert escape(raw) == expected


@pytest.mark.parametrize("raw", ["Computing in Science & Engineering", "~10 nm"])
def test_what_is_deliberately_left_alone(raw):
    """`&` would put a visible backslash in front of every real journal name in
    renderers that are not CommonMark, and a single `~` is ordinary in
    scientific prose while strikethrough needs a pair. Both are refusals, not
    oversights, and this records them."""
    assert escape(raw) == raw


def test_the_link_validator_is_the_one_the_html_renderer_uses():
    """Escaping a `javascript:` URL yields a well-formed Markdown destination
    holding a live script, exactly as it yields a well-formed HTML attribute."""
    from ackredit.formats import _html

    assert safe_link is _html.safe_link
    assert safe_link("javascript:alert(1)") is None
