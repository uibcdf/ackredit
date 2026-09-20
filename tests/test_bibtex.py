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
    register_item(
        id="ackredit:repo",
        type="software",
        title="Ackredit Tool",
        url="https://github.com/uibcdf/ackredit",
        note="A tracking tool",
    )
    track_item("ackredit:repo")
    bib = report(format="bibtex")

    assert "@software{ackredit-repo" in bib
    assert "url = {https://github.com/uibcdf/ackredit}" in bib
    assert "note = {A tracking tool}" in bib
