"""A reader must be able to tell where one author ends and the next begins.

Authors are stored as `Family, Given` — the form `CITATION.cff` produces and the
integration guide asks a host to copy. The Markdown report and the notebook
summary joined them with a comma, so two people became `Ruiz, Ana, Gómez, Luis`,
which reads as four names and cannot be undone (`uibcdf/ackredit#67`). BibTeX was
unaffected: it joins with ` and `.
"""

import html
import re

import pytest

import ackredit
from ackredit.core.collector import track_item
from ackredit.core.registry import register_item
from ackredit.formats._names import AUTHOR_SEPARATOR, author_list

AUTHORS = ["Ruiz, Ana", "Gómez, Luis"]


@pytest.fixture(autouse=True)
def _two_inverted_names(clean_registry):
    register_item(id="paper:two", type="article", title="Two People", authors=AUTHORS)
    track_item("paper:two", used_by="pkg.run")


def _recovered(joined: str) -> list[str]:
    return joined.split(AUTHOR_SEPARATOR)


def test_markdown_keeps_the_people_apart():
    line = next(
        line
        for line in ackredit.report(format="markdown").splitlines()
        if "Authors:" in line
    )
    assert _recovered(line.split("Authors: ", 1)[1]) == AUTHORS


def test_the_notebook_summary_keeps_the_people_apart():
    shown = re.search(r"<i>(.*?)</i>", ackredit.summary()._repr_html_()).group(1)
    assert _recovered(html.unescape(shown)) == AUTHORS


def test_bibtex_still_joins_with_and():
    assert "Ruiz, Ana and Gómez, Luis" in ackredit.report(format="bibtex")


def test_a_csl_name_object_is_written_as_a_name():
    """The CSL-JSON path accepts one, so a person-facing list must too."""
    assert author_list([{"family": "Ruiz", "given": "Ana"}, {"literal": "SciPy"}]) == (
        "Ruiz, Ana; SciPy"
    )


def test_a_single_string_is_left_as_written():
    assert author_list("Ruiz, Ana and Gómez, Luis") == "Ruiz, Ana and Gómez, Luis"


def test_every_author_is_escaped_on_its_own():
    assert author_list(["<b>", "Gómez, Luis"], html.escape) == "&lt;b&gt;; Gómez, Luis"
