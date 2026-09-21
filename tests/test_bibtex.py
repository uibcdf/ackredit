import pytest

from ackredit import register_item, report, track_item


def test_bibtex_article():
    register_item(
        id="molsysmt:2024",
        type="article",
        title="MolSysMT Paper",
        authors=["Diego", "Other Author"],
        year=2024,
        doi="10.1234/msm.2024",
        journal="Nature Molecular Systems",
    )
    track_item("molsysmt:2024")
    bib = report(format="bibtex")

    assert "@article{molsysmt-2024" in bib
    assert "title = {MolSysMT Paper}" in bib
    assert "author = {Diego and Other Author}" in bib
    assert "doi = {10.1234/msm.2024}" in bib
    assert "journal = {Nature Molecular Systems}" in bib


def test_bibtex_software():
    """`@software` is biblatex's, not BibTeX's.

    A BibTeX style does not define it, so a run warns and falls back to a
    default layout that loses the distinction entirely. `@misc` plus
    `howpublished` keeps it, shows it to the reader, and compiles clean under
    any style.
    """
    register_item(
        id="ackredit:repo",
        type="software",
        title="Ackredit Tool",
        url="https://github.com/uibcdf/ackredit",
        note="A tracking tool",
    )
    track_item("ackredit:repo")
    bib = report(format="bibtex")

    assert "@misc{ackredit-repo" in bib
    assert "howpublished = {Software}" in bib
    assert "url = {https://github.com/uibcdf/ackredit}" in bib
    assert "note = {A tracking tool}" in bib


@pytest.mark.parametrize(
    "item_type,entry,kind",
    [
        ("article", "article", None),
        ("software", "misc", "Software"),
        ("dataset", "misc", "Dataset"),
        ("repo", "misc", "Software repository"),
        ("web", "misc", "Web resource"),
        ("other", "misc", None),
    ],
)
def test_every_type_uses_an_entry_bibtex_defines(item_type, entry, kind):
    """Verified against a real BibTeX run: zero "entry type ... isn't
    style-file defined" warnings, where @software and @dataset produced one
    each."""
    register_item(id=f"kind:{item_type}", type=item_type, title=f"A {item_type}")
    track_item(f"kind:{item_type}")
    bib = report(format="bibtex")

    assert f"@{entry}{{kind-{item_type}," in bib
    block = [b for b in bib.split("\n\n") if f"kind-{item_type}," in b][0]
    if kind:
        assert f"howpublished = {{{kind}}}" in block
    else:
        assert "howpublished" not in block
