"""Explicit CSL author identity must survive portable BibTeX rendering (#78)."""

import json
import shutil
import subprocess

import pytest

import ackredit
from ackredit.core.registry import Registry


@pytest.fixture(autouse=True)
def _own_registry(clean_registry):
    """Each case declares its own bibliography."""


def captured(authors):
    with ackredit.capture("result") as result:
        ackredit.register_item(
            id="names", type="article", title="Resource description", authors=authors
        )
        ackredit.track_item("names")
    return result.attribution


def test_detached_literal_author_is_bibtex_syntax_not_a_dictionary(monkeypatch):
    authors = [{"literal": "The UniProt Consortium"}]
    original = captured(authors)
    saved = original.to_json()
    # Replace only this fixture-owned view, restoring it automatically on exit.
    monkeypatch.setattr(Registry, "items", {})
    ackredit.current_session().clear()
    restored = ackredit.Attribution.from_json(saved)

    assert "author = {{The UniProt Consortium}}" in restored.report(format="bibtex")
    assert json.loads(restored.report(format="csl-json"))[0]["author"] == authors
    assert original.to_json() == saved
    assert ackredit.get_used_items() == {}
    assert Registry.items == {}


def test_mixed_author_order_and_explicit_personal_parts_survive():
    authors = [
        "Doe, Jane",
        {"literal": "The UniProt Consortium"},
        {"family": "Smith", "given": "John", "suffix": "Jr."},
        {"family": "Gogh", "given": "Vincent", "non-dropping-particle": "van"},
        {"family": "Humboldt", "given": "Alexander", "dropping-particle": "von"},
    ]
    result = captured(authors)
    expected = (
        "author = {Doe, Jane and {The UniProt Consortium} and Smith, Jr., John "
        "and van Gogh, Vincent and Humboldt, Alexander von}"
    )
    assert expected in result.report(format="bibtex")
    assert expected in ackredit.report(format="bibtex")
    assert json.loads(result.report(format="csl-json"))[0]["author"][1:] == authors[1:]


@pytest.mark.parametrize(
    "author,expected",
    [
        ({"family": "Smith"}, "Smith"),
        ({"given": "Plato"}, "Plato"),
        ({"family": "Smith", "suffix": "III"}, "Smith, III, "),
        (
            {
                "family": "Cruz",
                "given": "Juan",
                "non-dropping-particle": "la",
                "dropping-particle": "de",
            },
            "la Cruz, Juan de",
        ),
        ({"literal": "Collective", "family": "Ignore", "given": "Me"}, "{Collective}"),
    ],
)
def test_explicit_name_parts_are_not_dropped(author, expected):
    assert f"author = {{{expected}}}" in captured([author]).report(format="bibtex")


@pytest.mark.parametrize(
    "text,escaped",
    [
        ("R&D and 50%", r"R\&D and 50\%"),
        ("Cost_$#", r"Cost\_\$\#"),
        ("A{B}~^", r"A\{B\}\textasciitilde{}\textasciicircum{}"),
        (r"A\B", r"A\textbackslash{}B"),
        ("One, Two, Three, Four", "One, Two, Three, Four"),
    ],
)
def test_literal_text_is_escaped_before_adding_syntax_braces(text, escaped):
    assert f"author = {{{{{escaped}}}}}" in captured([{"literal": text}]).report(
        format="bibtex"
    )


def test_structured_name_parts_are_escaped():
    result = captured([{"family": "A&B", "given": "J_#", "suffix": "50%"}])
    assert r"author = {A\&B, 50\%, J\_\#}" in result.report(format="bibtex")


def test_delimiters_within_explicit_personal_parts_are_content():
    result = captured([{"family": "Research and Development", "given": "Jane, Anne"}])
    assert "author = {{Research and Development}, {Jane, Anne}}" in result.report(
        format="bibtex"
    )


def test_bibtex_itself_retains_literal_identity_and_personal_parts(tmp_path):
    executable = shutil.which("bibtex")
    if executable is None:
        pytest.skip("BibTeX is unavailable")
    result = captured(
        [
            {"literal": "Research and Development, Consortium"},
            {"family": "Smith", "given": "John", "suffix": "Jr."},
            {"family": "Gogh", "given": "Vincent", "non-dropping-particle": "van"},
            {"family": "Humboldt", "given": "Alexander", "dropping-particle": "von"},
        ]
    )
    (tmp_path / "names.bib").write_text(
        result.report(format="bibtex"), encoding="utf-8"
    )
    (tmp_path / "names.aux").write_text(
        "\\citation{*}\n\\bibdata{names}\n\\bibstyle{names}\n", encoding="utf-8"
    )
    (tmp_path / "names.bst").write_text(
        "ENTRY { author } {} {}\n"
        "FUNCTION {inspect} {\n"
        "author num.names$ int.to.str$ write$ newline$\n"
        'author #1 "{ll}" format.name$ write$ newline$\n'
        'author #2 "{ll}|{jj}|{ff}" format.name$ write$ newline$\n'
        'author #3 "{vv}|{ll}|{ff}" format.name$ write$ newline$\n'
        'author #4 "{ll}|{ff}" format.name$ write$ newline$\n'
        "}\nREAD\nITERATE {inspect}\n",
        encoding="utf-8",
    )
    process = subprocess.run(
        [executable, "names"], cwd=tmp_path, capture_output=True, text=True, timeout=30
    )
    assert process.returncode == 0, process.stdout + process.stderr
    assert (tmp_path / "names.bbl").read_text().splitlines() == [
        "4",
        "{Research and Development, Consortium}",
        "Smith|Jr.|John",
        "van|Gogh|Vincent",
        "Humboldt|Alexander~von",
    ]


def test_plain_strings_retain_the_existing_personal_name_contract():
    result = captured(["The UniProt Consortium", "Doe, Jane", "Travis E. Oliphant"])
    assert (
        "author = {The UniProt Consortium and Doe, Jane and Travis E. Oliphant}"
        in result.report(format="bibtex")
    )


def test_literal_and_personal_authors_survive_a_bib_file_round_trip(
    tmp_path, monkeypatch
):
    result = captured(
        [
            {"literal": "Research and Development, Consortium"},
            {"family": "Smith", "given": "John", "suffix": "Jr."},
        ]
    )
    first = result.report(format="bibtex")
    path = tmp_path / "names.bib"
    path.write_text(first, encoding="utf-8")
    monkeypatch.setattr(Registry, "items", {})
    ackredit.current_session().clear()
    ackredit.load_bibtex(str(path))

    assert Registry.items["names"]["authors"] == [
        "{Research and Development, Consortium}",
        "Smith, Jr., John",
    ]
    ackredit.track_item("names")
    assert ackredit.report(format="bibtex") == first
