"""A citation key names one work, and is the name the manuscript cites.

Keys used to be the item id with every `:`, `_` and space rewritten to `-`. That
mapped `Smith_2020` and `Smith:2020` to one key, so BibTeX kept one entry and a
citation was lost; it renamed every key read from a `.bib` file, so the user's
`\\cite{Smith_2020}` stopped resolving; and it did not do what it was for, since
natbib labels an authorless entry with the first three characters of its key and
every discovered package printed as "(dis, 2020)" (`uibcdf/ackredit#109`).
"""

import re
import shutil
import subprocess

import pytest

import ackredit
from ackredit.formats.bibtex import cite_keys

# Ids that the old rewrite, or BibTeX's case-insensitive comparison, collapsed.
CLASHING = [
    "Smith_2020",
    "Smith:2020",
    "Smith-2020",
    "smith_2020",
    "a b",
    "a,b",
    "a-b",
    "odd id, with {braces} & 100%",
    "ünïcode",
    "unicode",
]


def _entry_keys(bib: str) -> list[str]:
    return re.findall(r"^@\w+\{([^,]+),", bib, flags=re.MULTILINE)


def test_distinct_ids_never_share_a_key():
    keys = cite_keys(CLASHING)

    assert len({key.casefold() for key in keys.values()}) == len(CLASHING)


def test_every_key_is_one_bibtex_can_read():
    for key in cite_keys(CLASHING).values():
        assert re.fullmatch(r"[A-Za-z0-9_:./+-]+", key), key


def test_a_valid_id_is_its_own_key():
    ids = ["Smith_2020", "smith:2020a", "10.1021/ct500000x", "discovered:numpy"]

    assert cite_keys(ids) == {item_id: item_id for item_id in ids}


def test_a_key_does_not_depend_on_what_else_is_cited_unless_they_clash():
    alone = cite_keys(["Smith_2020"])
    together = cite_keys(["Smith_2020", "Jones:2021"])

    assert alone["Smith_2020"] == together["Smith_2020"] == "Smith_2020"


def test_generated_keys_cannot_take_original_or_second_generation_keys():
    import hashlib

    invalid = "a b"
    generated = "a-b-" + hashlib.sha256(invalid.encode()).hexdigest()[:8]
    regenerated = generated + "-" + hashlib.sha256(generated.encode()).hexdigest()[:8]
    ids = [invalid, generated, regenerated, generated + "-2"]

    keys = cite_keys(ids)

    assert len({key.casefold() for key in keys.values()}) == len(ids)
    assert all(keys[item_id] == item_id for item_id in ids[1:])
    assert keys == cite_keys(reversed(ids))


def test_hash_collisions_still_keep_distinct_keys(monkeypatch):
    import ackredit.formats.bibtex as bibtex

    monkeypatch.setattr(bibtex, "_digest", lambda _: "samehash")
    ids = ["a b", "a,b", "a-b-samehash", "a-b-samehash-2"]
    keys = cite_keys(ids)

    assert len({key.casefold() for key in keys.values()}) == len(ids)
    assert keys["a-b-samehash"] == "a-b-samehash"
    assert keys["a-b-samehash-2"] == "a-b-samehash-2"
    assert keys == cite_keys(reversed(ids))


def test_a_trailing_newline_is_not_a_valid_citation_key():
    ids = ["id", "id\n"]
    keys = cite_keys(ids)

    assert keys["id"] == "id"
    assert keys["id\n"] != "id\n"
    assert all(re.fullmatch(r"[A-Za-z0-9_:./+-]+", key) for key in keys.values())


def test_a_loaded_bib_file_is_written_back_under_its_own_keys(tmp_path, clean_registry):
    source = tmp_path / "refs.bib"
    source.write_text(
        "@article{Smith_2020, title = {A}, author = {Smith, J.}, year = {2020}}\n"
        "@article{Smith:2020, title = {B}, author = {Smith, J.}, year = {2020}}\n"
    )
    ackredit.load_bibtex(source)
    ackredit.track_item("Smith_2020")
    ackredit.track_item("Smith:2020")

    assert _entry_keys(ackredit.report(format="bibtex")) == [
        "Smith_2020",
        "Smith:2020",
    ]


def test_the_latex_report_cites_the_keys_the_bibtex_report_defines(clean_registry):
    for item_id in CLASHING:
        ackredit.register_item(id=item_id, type="software", title=item_id)
        ackredit.track_item(item_id)

    cited = re.findall(r"\\citep\{([^}]+)\}", ackredit.report(format="latex"))

    assert cited == _entry_keys(ackredit.report(format="bibtex"))


def test_an_authorless_entry_carries_the_field_its_label_comes_from(clean_registry):
    ackredit.register_item(id="discovered:numpy", type="software", title="NumPy")
    ackredit.register_item(
        id="with:author", type="software", title="T", authors=["Ruiz, Ana"]
    )
    ackredit.track_item("discovered:numpy")
    ackredit.track_item("with:author")

    entries = ackredit.report(format="bibtex").split("\n\n")

    assert "key = {NumPy}" in entries[0]
    assert "key = " not in entries[1]


@pytest.mark.skipif(
    not (shutil.which("pdflatex") and shutil.which("bibtex")),
    reason="pdflatex and bibtex are optional system binaries, not installed here",
)
def test_a_compiled_report_resolves_every_citation_and_labels_by_name(
    tmp_path, clean_registry
):
    for item_id in CLASHING + ["discovered:numpy"]:
        title = "NumPy" if item_id == "discovered:numpy" else f"Work {len(item_id)}"
        ackredit.register_item(id=item_id, type="software", title=title, year=2020)
        ackredit.track_item(item_id)

    ackredit.dump(tmp_path, formats=["latex", "bibtex"])
    for command in (
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "ackredit_report"],
        ["bibtex", "ackredit_report"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "ackredit_report"],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "ackredit_report"],
    ):
        result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout[-2000:]

    log = (tmp_path / "ackredit_report.log").read_text(errors="replace")
    assert "undefined" not in log
    assert "multiply defined" not in log

    labels = re.findall(
        r"\\bibitem\[([^\]]*)\]", (tmp_path / "ackredit_report.bbl").read_text()
    )
    assert len(labels) == len(CLASHING) + 1
    assert any(label.startswith("NumPy") for label in labels)
    assert not any(label.startswith("dis") for label in labels)
