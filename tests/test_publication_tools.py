"""Real publication engines must retain identifiable exported works (#120)."""

import hashlib
import importlib
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import ackredit
from ackredit.core.cff import parse_cff
from ackredit.core.registry import Registry

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/publication"


def test_retained_receipt_binds_the_same_original_input_to_verified_wheels():
    receipt = json.loads(
        (ROOT / "devtools/receipts/publication_tools_120_2026-10-06.json").read_text()
    )
    assert receipt["issue"] == "uibcdf/ackredit#120"
    candidate = receipt["candidate"]
    assert candidate["before"] == candidate["after"]
    assert (
        candidate["before"]["original_wheel"]["source_commit"]
        != receipt["baseline"]["installed_identity"]["original_wheel"]["source_commit"]
    )
    original = ackredit.Attribution.from_dict(
        receipt["paired_input"]["payload"]
    ).to_json()
    assert (
        hashlib.sha256(original.encode()).hexdigest()
        == receipt["paired_input"]["sha256"]
        == candidate["probe"]["input_sha256"]
    )
    for relative, digest in receipt["fixtures"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    # #122 evolves the process owner to retain non-UTF-8 TeX bytes. Verify the
    # original #120 source snapshot rather than requiring that tool to freeze.
    followup = json.loads(
        (ROOT / "devtools/receipts/biblatex_receiving_122_2026-10-06.json").read_text()
    )
    assert (
        hashlib.sha256(followup["previous_process_owner"]["text"].encode()).hexdigest()
        == candidate["probe"]["tool_sha256"]
        == followup["previous_process_owner"]["sha256"]
    )
    for side in (receipt["baseline"], candidate):
        for export in side["exports"].values():
            assert (
                hashlib.sha256(export["text"].encode()).hexdigest() == export["sha256"]
            )
    assert candidate["probe"]["bibtex_warnings"] == []
    before_bib = receipt["baseline"]["exports"]["references.bib"]["text"]
    after_bib = candidate["exports"]["references.bib"]["text"]
    assert "editors =" in before_bib and "@misc{preferred:collection," in before_bib
    assert "editor =" in after_bib and "@book{preferred:collection," in after_bib
    assert (
        "Research and Development, Consortium}, editors"
        in candidate["exports"]["references.bbl"]["text"]
    )


def test_publication_guidance_states_the_executed_receiving_boundary():
    receipt = json.loads(
        (ROOT / "devtools/receipts/publication_tools_120_2026-10-06.json").read_text()
    )
    page = (ROOT / "docs/content/user_guide/publication_tools.md").read_text()
    prose = " ".join(page.split())
    for executable in ("bibtex", "pandoc"):
        first_line = receipt["candidate"]["probe"]["versions"][executable].splitlines()[
            0
        ]
        version = re.search(r"\d+\.\d+[a-z]?", first_line).group()
        assert version in prose
    assert receipt["candidate"]["csl_style_identity"]["title"] in prose.replace(
        "**", ""
    )
    for boundary in (
        "immutable public 0.11.0",
        "full URL",
        "BibLaTeX/Biber",
        "duplicate identity",
        "--require-publication-tools",
    ):
        assert boundary in prose


@pytest.fixture
def detached(tmp_path, clean_registry, monkeypatch):
    with ackredit.capture("publication-fixture") as captured:
        for item in json.loads((FIXTURES / "records.json").read_text()):
            ackredit.register_item(**item)
            ackredit.track_item(item["id"])
        # Mirror CFF discovery's internal normalized record insertion. Private
        # source hints are not accepted keyword arguments to public registration.
        Registry.register_item(
            id="preferred:collection",
            **parse_cff((FIXTURES / "preferred.cff").read_text()),
        )
        ackredit.track_item("preferred:collection")
    saved = captured.attribution.to_json()
    monkeypatch.setattr(Registry, "items", {})
    ackredit.current_session().clear()
    path = tmp_path / "original.json"
    path.write_text(saved)
    return ackredit.Attribution.from_json(saved), path


@pytest.fixture
def tools(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "devtools"))
    return importlib.import_module("check_publication_tools")


@pytest.fixture
def engines(request):
    missing = [
        name
        for name in ("pandoc", "bibtex", "kpsewhich", "pdflatex")
        if shutil.which(name) is None
    ]
    if missing:
        message = "Publication tools unavailable: " + ", ".join(missing)
        if request.config.getoption("--require-publication-tools"):
            pytest.fail(message)
        pytest.skip(message)


@pytest.fixture
def received(detached, tmp_path, tools, engines):
    _, path = detached
    directory = tmp_path / "receiving"
    return tools.check(path, directory), directory


def test_detached_exports_preserve_releases_names_and_original_preferred_work(detached):
    attribution, path = detached
    original = path.read_text()
    records = {item["id"]: item for item in attribution.to_dict()["items"]}
    bibtex = attribution.report("bibtex")
    csl = {item["id"]: item for item in json.loads(attribution.report("csl-json"))}
    assert set(csl) == set(records)
    for item_id in ("software:1.0", "software:2.0", "dataset:2024"):
        assert csl[item_id]["version"] == records[item_id]["version"]
        expected = (
            "10.5555/ackredit.fixture.software"
            if item_id.startswith("software:")
            else "10.5555/ackredit.fixture.dataset"
        )
        assert csl[item_id]["DOI"] == expected
    assert (
        records["software:2.0"]["doi"]
        == "https://doi.org/10.5555/ackredit.fixture.software"
    )
    assert "doi = {https://doi.org/10.5555/ackredit.fixture.software}" in bibtex
    assert "version = {1.0}" in bibtex and "version = {2.0}" in bibtex
    assert "@book{preferred:collection," in bibtex
    assert (
        "editor = {de la Cruz, III, María and {Research and Development, Consortium}}"
        in bibtex
    )
    assert "editor = {García, Ana and {Research and Development, Consortium}}" in bibtex
    assert "editors =" not in bibtex and "{'family'" not in bibtex
    preferred = csl["preferred:collection"]
    assert preferred["type"] == "book"
    assert preferred["editor"] == [
        {"family": "de la Cruz", "given": "María", "suffix": "III"},
        {"literal": "Research and Development, Consortium"},
    ]
    assert "version" not in preferred and "author" not in preferred
    assert all("fixture.root" not in json.dumps(item) for item in csl.values())
    assert records["preferred:collection"]["_cff_type"] == "edited-work"
    assert path.read_text() == original
    assert attribution.to_json() == original
    assert Registry.items == {} and ackredit.get_used_items() == {}


@pytest.mark.parametrize("field", ["editor", "editors"])
def test_explicit_editor_objects_are_names_in_bibtex(field, clean_registry):
    ackredit.register_item(
        id="editor:explicit",
        title="Collection",
        **{
            field: [{"family": "García", "given": "Ana"}, {"literal": "A and B, Group"}]
        },
    )
    ackredit.track_item("editor:explicit")
    assert "editor = {García, Ana and {A and B, Group}}" in ackredit.report("bibtex")


@pytest.mark.parametrize(
    "kind,entry", [("book", "book"), ("edited-work", "book"), ("report", "misc")]
)
def test_only_selected_cff_book_kinds_use_the_new_bibtex_mapping(
    kind, entry, clean_registry
):
    Registry.register_item(
        id="cff:kind", **parse_cff(f"type: {kind}\ntitle: Original kind\n")
    )
    ackredit.track_item("cff:kind")
    assert ackredit.report("bibtex").startswith(f"@{entry}{{cff:kind,")
    Registry.items["cff:kind"]["_bibtex_type"] = "manual"
    assert ackredit.report("bibtex").startswith("@manual{cff:kind,")


@pytest.mark.parametrize(
    "field,hint", [("authors", "_cff_authors"), ("editors", "_cff_editors")]
)
def test_cff_name_identity_survives_bibtex_but_explicit_replacement_wins(
    field, hint, clean_registry
):
    parsed = parse_cff(
        f"title: Names\n{field}:\n"
        "  - name: Research and Development, Consortium\n"
        "  - family-names: Cruz\n    given-names: María\n"
        "    name-particle: de la\n    name-suffix: III\n"
    )
    Registry.register_item(id="cff:names", **parsed)
    ackredit.track_item("cff:names")
    bib_field = "author" if field == "authors" else "editor"
    assert (
        f"{bib_field} = {{{{Research and Development, Consortium}} and de la Cruz, III, María}}"
        in ackredit.report("bibtex")
    )
    Registry.items["cff:names"][field] = ["Replacement, Person"]
    assert hint in Registry.items["cff:names"]
    assert f"{bib_field} = {{Replacement, Person}}" in ackredit.report("bibtex")


def test_real_readers_retain_editor_identity_and_distinct_versions(received):
    receipt, directory = received
    source = {
        item["id"]: item
        for item in json.loads((directory / "references.csl.json").read_text())
    }
    for filename in ("csl-read.json", "bibtex-read.json"):
        records = {
            item["id"]: item for item in json.loads((directory / filename).read_text())
        }
        assert set(records) == set(source)
        for item_id in ("software:1.0", "software:2.0", "dataset:2024"):
            assert records[item_id]["version"] == source[item_id]["version"]
            expected = source[item_id]["DOI"]
            if filename == "bibtex-read.json" and item_id == "software:2.0":
                expected = "https://doi.org/10.5555/ackredit.fixture.software"
            assert records[item_id]["DOI"] == expected
        assert records["preferred:collection"]["type"] == "book"
        editors = records["preferred:collection"]["editor"]
        assert editors[1] == {"literal": "Research and Development, Consortium"}
        # BibTeX encodes the particle separately; CSL output can carry it in family.
        assert editors[0]["given"] == "María" and editors[0]["suffix"] == "III"
        assert "Cruz" in editors[0]["family"]
        assert (
            records["edited:structured"]["editor"]
            == source["edited:structured"]["editor"]
        )
    assert receipt["original_preserved"] and not receipt["new_execution_credit"]
    assert Registry.items == {} and ackredit.get_used_items() == {}


def test_real_selected_styles_render_works_editors_and_compile(received):
    receipt, directory = received
    bbl = (directory / "references.bbl").read_text()
    html = (directory / "bibliography.html").read_text()
    assert receipt["bibtex_warnings"] == []
    assert all(step["exit_code"] == 0 for step in receipt["processes"])
    assert (directory / "manuscript.pdf").read_bytes().startswith(b"%PDF-")
    for key in receipt["citation_keys"].values():
        assert f"\\bibitem{{{key}}}" in bbl
    for item_id in receipt["citation_keys"]:
        assert f'id="ref-{item_id}"' in html
    for text in (
        "García",
        "María",
        "Research and Development, Consortium",
        "Example Press",
    ):
        assert text in bbl and text in html
    assert "III" in bbl and "III" in html
    assert "Software, 2024" in bbl and "Dataset, 2024" in bbl
    # plain.bst retains entry identity, but ignores the additional DOI/version fields.
    assert "10.5555/ackredit.fixture" not in bbl
    assert "version" not in bbl.lower()
    assert "https://doi.org/10.5555/ackredit.fixture.article" in html
    assert "https://doi.org/<a" not in html
    assert "doi.org/https://" not in html


def test_imported_software_entry_is_retained_with_explicit_plain_style_limit(
    tmp_path, clean_registry, engines
):
    original = "@software{original:software, title={Imported software}, author={{Original Team}}, year={2024}}"
    source = tmp_path / "imported.bib"
    source.write_text(original)
    ackredit.load_bibtex(source)
    ackredit.track_item("original:software")
    exported = ackredit.report("bibtex")
    assert exported.startswith("@software{original:software,")
    source.write_text(exported)
    (tmp_path / "imported.aux").write_text(
        "\\citation{*}\n\\bibdata{imported}\n\\bibstyle{plain}\n"
    )
    result = subprocess.run(
        ["bibtex", "imported"], cwd=tmp_path, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "isn't style-file defined" in (tmp_path / "imported.blg").read_text()
    assert "\\bibitem{original:software}" in (tmp_path / "imported.bbl").read_text()


def test_probe_refuses_to_replace_prior_evidence(detached, tools, engines, tmp_path):
    _, path = detached
    existing = tmp_path / "receiving"
    existing.mkdir()
    retained = existing / "retained.txt"
    retained.write_text("Original evidence")
    with pytest.raises(FileExistsError):
        tools.check(path, existing)
    assert retained.read_text() == "Original evidence"
