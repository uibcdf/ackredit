"""Citation metadata rendered as HTML must reach the page as text.

Ackredit renders into a notebook and into a local dashboard, and the values it
renders are not its own: they arrive from Crossref, from DataCite, from the
`CITATION.cff` of any installed package and from whatever a host library
registered. Emitted raw they do two things, and the ordinary one comes first —
a journal called "Computing in Science & Engineering" renders wrong, and
Ackredit ships that name itself. The second is that a `<script>` in a title, or
a `javascript:` URL in a `url` field, becomes live markup in the user's session.

This is the HTML twin of `test_latex_escaping.py`. Every field the renderers
interpolate is covered here, because the defect was that none of them were.
"""

import pytest

import ackredit
from ackredit.contrib.jupyter import summary
from ackredit.formats._html import escape, safe_link

HOSTILE = "<script>alert('x')</script>"


@pytest.fixture(autouse=True)
def _clean(clean_registry):
    yield


def render(**fields) -> str:
    item = {"id": "x:1", "type": "article", "title": "A Title"}
    item.update(fields)
    ackredit.register_item(**item)
    ackredit.track_item("x:1", used_by=fields.pop("_used_by", "run"))
    return summary()._repr_html_()


# Every value the notebook renderer interpolates. Each was raw before this.
@pytest.mark.parametrize(
    "field,value",
    [
        ("title", f"Surfaces & Pockets {HOSTILE}"),
        ("authors", [f"Ann O'Neill {HOSTILE}"]),
        ("year", f"2024 {HOSTILE}"),
        ("journal", f"Science & Nature {HOSTILE}"),
    ],
)
def test_item_fields_are_not_markup(field, value):
    html = render(**{field: value})
    assert HOSTILE not in html
    assert "<script>" not in html


def test_the_caller_name_is_not_markup():
    ackredit.register_item(id="x:1", title="A Title")
    ackredit.track_item("x:1", used_by=f"run {HOSTILE}")
    html = summary()._repr_html_()
    assert HOSTILE not in html
    assert "&lt;script&gt;" in html


def test_an_ampersand_in_a_real_journal_name_renders_as_one():
    """The ordinary half of this defect, with a name Ackredit itself ships."""
    html = render(title="Computing in Science & Engineering")
    assert "Computing in Science &amp; Engineering" in html
    assert "Science & Engineering" not in html


def test_a_quote_in_a_doi_cannot_escape_the_href():
    """The href is delimited by single quotes, and a DOI is not ours to trust."""
    html = render(doi="10.1/x' onmouseover='alert(1)")
    # The text may appear inside the attribute; what must not happen is the
    # attribute ending early, which is what an unescaped quote would do.
    assert "' onmouseover='" not in html
    assert "&#x27; onmouseover=&#x27;" in html


@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "JavaScript:alert(1)",
        "  javascript:alert(1)",
        "java\tscript:alert(1)",
        "java\nscript:alert(1)",
        "data:text/html,<script>alert(1)</script>",
        "vbscript:msgbox(1)",
    ],
)
def test_a_url_that_is_not_a_link_is_not_linked(url):
    html = render(url=url)
    assert "<a href" not in html
    # The citation is still reported; only the link is withheld.
    assert "A Title" in html


@pytest.mark.parametrize("url", ["http://example.org/a", "https://example.org/a"])
def test_a_real_url_is_still_linked(url):
    assert f"href='{url}'" in render(url=url)


def test_a_doi_still_builds_its_link():
    assert "href='https://doi.org/10.1038/s41586-020-2649-2'" in render(
        doi="10.1038/s41586-020-2649-2"
    )


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("a & b", "a &amp; b"),
        ("<b>", "&lt;b&gt;"),
        ('say "hi"', "say &quot;hi&quot;"),
        ("O'Neill", "O&#x27;Neill"),
        (2024, "2024"),
    ],
)
def test_escape_covers_content_and_attribute_contexts(raw, expected):
    assert escape(raw) == expected


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://doi.org/10.1/x", "https://doi.org/10.1/x"),
        ("http://example.org", "http://example.org"),
        ("javascript:alert(1)", None),
        ("", None),
        (None, None),
        ("ftp://example.org/a", None),
    ],
)
def test_safe_link_admits_only_what_can_be_followed(url, expected):
    assert safe_link(url) == expected


def test_a_summary_is_readable_outside_a_notebook():
    """`print(ackredit.summary())` used to give the object's address."""
    ackredit.register_item(id="x:1", title="A Work", authors=["Ruiz, Ana"], year=2024)
    ackredit.track_item("x:1", used_by="run")
    summary = ackredit.summary()

    for rendering in (str(summary), repr(summary)):
        assert "A Work" in rendering
        assert "object at 0x" not in rendering


def test_an_empty_session_says_so_in_text_too():
    assert "No items" in str(ackredit.summary())


def test_the_notebook_rendering_is_still_html():
    ackredit.register_item(id="x:1", title="A Work")
    ackredit.track_item("x:1", used_by="run")
    assert ackredit.summary()._repr_html_().startswith("<div")
