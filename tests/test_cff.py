"""CITATION.cff is the file a project writes to say how it wants to be cited.

Reading it with regular expressions over lines could not tell whether an
`authors:` block belonged to the root document or to `preferred-citation`, and
produced a confident wrong answer on three constructs the specification
documents. These tests pin the behaviour that replaced it.
"""

import pytest

from ackredit.core.cff import find_and_parse_cff, parse_cff


def test_an_entity_author_is_credited():
    """An organisation is a valid CFF author and used to disappear, which
    under-credits exactly the institutions least able to notice."""
    data = parse_cff(
        "cff-version: 1.2.0\n"
        "title: MyTool\n"
        "authors:\n"
        '  - name: "The Research Consortium"\n'
        "  - family-names: Ruiz\n"
        "    given-names: Ana\n"
    )

    assert data["authors"] == ["The Research Consortium", "Ruiz, Ana"]


def test_preferred_citation_replaces_rather_than_merges():
    """The block exists so a project can say "cite this paper, not this
    software". Merging credited authors belonging to neither."""
    data = parse_cff(
        "cff-version: 1.2.0\n"
        "title: MyTool Software\n"
        "authors:\n"
        "  - family-names: Ruiz\n"
        "    given-names: Ana\n"
        "preferred-citation:\n"
        "  type: article\n"
        "  title: The Paper Describing MyTool\n"
        "  doi: 10.1234/paper\n"
        "  authors:\n"
        "    - family-names: Gomez\n"
        "      given-names: Luis\n"
    )

    assert data["title"] == "The Paper Describing MyTool"
    assert data["authors"] == ["Gomez, Luis"]
    assert data["doi"] == "10.1234/paper"


def test_preferred_citation_falls_back_for_what_it_does_not_state():
    data = parse_cff(
        "cff-version: 1.2.0\n"
        "title: MyTool Software\n"
        "url: https://example.org/mytool\n"
        "authors:\n"
        "  - family-names: Ruiz\n"
        "    given-names: Ana\n"
        "preferred-citation:\n"
        "  title: The Paper\n"
    )

    assert data["title"] == "The Paper"
    assert data["url"] == "https://example.org/mytool"
    # No authors of its own, so the document's stand.
    assert data["authors"] == ["Ruiz, Ana"]


@pytest.mark.parametrize(
    "block,expected",
    [
        ("doi: 10.1234/short\n", "10.1234/short"),
        (
            "identifiers:\n  - type: doi\n    value: 10.5281/zenodo.123456\n",
            "10.5281/zenodo.123456",
        ),
        (
            "identifiers:\n  - type: url\n    value: https://example.org\n"
            "  - type: doi\n    value: 10.5281/zenodo.999\n",
            "10.5281/zenodo.999",
        ),
    ],
)
def test_the_doi_is_found_wherever_the_specification_allows_it(block, expected):
    """`identifiers` is the canonical form, and what a Zenodo deposition writes."""
    data = parse_cff(f"cff-version: 1.2.0\ntitle: MyTool\n{block}")

    assert data["doi"] == expected


def test_a_colon_in_a_title_survives():
    data = parse_cff('cff-version: 1.2.0\ntitle: "MolSysMT: a toolkit"\n')

    assert data["title"] == "MolSysMT: a toolkit"


def test_a_person_with_only_one_name_is_kept():
    data = parse_cff("cff-version: 1.2.0\ntitle: T\nauthors:\n  - family-names: Ruiz\n")

    assert data["authors"] == ["Ruiz"]


def test_an_empty_or_unstructured_document_yields_nothing():
    assert parse_cff("") == {}
    assert parse_cff("just a string\n") == {}


def test_a_malformed_file_is_reported_not_swallowed(tmp_path):
    (tmp_path / "CITATION.cff").write_text("title: [unclosed\n")
    package = tmp_path / "pkg"
    package.mkdir()

    import warnings

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = find_and_parse_cff(package)

    assert result is None
    assert [getattr(w.message, "code", None) for w in caught] == ["ACKREDIT-W004"]
