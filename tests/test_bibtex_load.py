from ackredit import Registry, load_bibtex


def test_load_bibtex_file(tmp_path):
    bib_content = """
@article{paper1,
  author = {Smith, John and Doe, Jane},
  title = {A Great Scientific Paper},
  journal = {Journal of Science},
  year = {2024},
  doi = {10.1234/js.2024}
}

@software{tool1,
  author = {Developer, Alice},
  title = {Amazing Software},
  url = {https://github.com/example/tool},
  year = {2023}
}
"""
    bib_file = tmp_path / "refs.bib"
    bib_file.write_text(bib_content)

    load_bibtex(bib_file)

    # Check paper1
    assert "paper1" in Registry.items
    item1 = Registry.items["paper1"]
    assert item1["type"] == "article"
    assert "Smith, John" in item1["authors"]
    assert "Doe, Jane" in item1["authors"]
    assert item1["year"] == 2024
    assert item1["doi"] == "10.1234/js.2024"

    # Check tool1
    assert "tool1" in Registry.items
    item2 = Registry.items["tool1"]
    assert item2["type"] == "software"
    assert item2["authors"] == ["Developer, Alice"]
    assert item2["url"] == "https://github.com/example/tool"
