"""Actual Biber records and selected BibLaTeX styles are separate evidence (#122)."""

import hashlib
import importlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import ackredit

ROOT = Path(__file__).resolve().parents[1]
NAMESPACES = {"b": "http://biblatex-biber.sourceforge.net/biblatexml"}
EXPECTED_IDS = {
    "software:1.0",
    "software:2.0",
    "dataset:2024",
    "article:2023",
    "edited:structured",
    "preferred:collection",
}


def _records(xml):
    return {node.get("id"): node for node in ET.fromstring(xml)}


def _text(node, query):
    found = node.find(query, NAMESPACES)
    assert found is not None, query
    return " ".join(" ".join(found.itertext()).split())


def _presentation(text):
    # pdftotext retains TeX's discretionary hyphens at line breaks. Keep the
    # original export intact; join only those breaks for bounded display checks.
    return " ".join(re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text).split())


def _assert_reader(xml, bbl):
    records = _records(xml)
    assert set(records) == EXPECTED_IDS
    assert set(re.findall(r"\\entry\{([^}]+)\}", bbl)) == EXPECTED_IDS
    for item_id, version in (
        ("software:1.0", "1.0"),
        ("software:2.0", "2.0"),
        ("dataset:2024", "2024.1"),
    ):
        assert _text(records[item_id], "b:version") == version
        assert f"\\field{{version}}{{{version}}}" in bbl
    assert _text(records["software:2.0"], "b:doi") == (
        "https://doi.org/10.5555/ackredit.fixture.software"
    )
    for item_id in ("software:1.0", "software:2.0"):
        names = records[item_id].findall("b:names/b:name", NAMESPACES)
        assert len(names) == 1
        assert _text(names[0], "b:namepart[@type='family']") == (
            "Research and Development, Consortium"
        )
    assert (
        _text(records["dataset:2024"], "b:title") == r"Datos de México: 50\% coverage"
    )
    preferred = records["preferred:collection"]
    assert preferred.get("entrytype") == "book"
    assert preferred.find("b:version", NAMESPACES) is None
    assert _text(preferred, "b:doi") == "10.5555/ackredit.fixture.collection"
    editors = preferred.findall("b:names[@type='editor']/b:name", NAMESPACES)
    assert len(editors) == 2
    for part, text in (
        ("family", "Cruz"),
        ("given", "María"),
        ("prefix", "de la"),
        ("suffix", "III"),
    ):
        assert _text(editors[0], f"b:namepart[@type='{part}']") == text
    assert _text(editors[1], "b:namepart[@type='family']") == (
        "Research and Development, Consortium"
    )
    assert len(records["edited:structured"].findall("b:names/b:name", NAMESPACES)) == 2


@pytest.fixture
def tools(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "devtools"))
    return importlib.import_module("check_biblatex")


@pytest.fixture
def detached(tmp_path):
    receipt = json.loads(
        (ROOT / "devtools/receipts/doi_presentation_121_2026-10-06.json").read_text()
    )
    path = tmp_path / "original.json"
    path.write_text(
        ackredit.Attribution.from_dict(receipt["paired_input"]["payload"]).to_json()
    )
    return path


@pytest.fixture
def engines(request):
    missing = [
        name
        for name in ("biber", "kpsewhich", "pdflatex", "pdftotext")
        if shutil.which(name) is None
    ]
    if not missing:
        found = subprocess.run(
            ["kpsewhich", "biblatex.sty"], capture_output=True, text=True, timeout=60
        )
        if found.returncode != 0 or not found.stdout.strip():
            missing.append("biblatex.sty")
    if missing:
        message = "BibLaTeX tools unavailable: " + ", ".join(missing)
        if request.config.getoption("--require-biblatex-tools"):
            pytest.fail(message)
        pytest.skip(message)


@pytest.mark.parametrize("style", ["authoryear", "numeric"])
def test_real_biber_reader_and_biblatex_style_keep_distinct_releases(
    tools, detached, tmp_path, engines, style
):
    original = detached.read_bytes()
    used = ackredit.get_used_items()
    directory = tmp_path / style
    result = tools.check(detached, directory, style=style)
    _assert_reader(
        (directory / "reader.xml").read_text(),
        (directory / "manuscript.bbl").read_text(),
    )
    rendered = _presentation((directory / "rendered.txt").read_text())
    for text in (
        "Version 1.0",
        "Version 2.0",
        "Version 2024.1",
        "Méthodes & données",
        "Structured editor collection",
    ):
        assert text in rendered
    assert ("García, Ana" if style == "authoryear" else "Ana García") in rendered
    assert (directory / "manuscript.pdf").read_bytes().startswith(b"%PDF-")
    assert result["style"] == style
    assert all(step["exit_code"] == 0 for step in result["processes"])
    assert result["original_preserved"] and result["export_preserved"]
    assert not result["new_execution_credit"]
    for filename in ("references.bib.blg", "manuscript.blg"):
        assert len(result["warnings"][filename]) == 1
        assert "ISBN '978-0-00-000000-0'" in result["warnings"][filename][0]
    assert detached.read_bytes() == original
    assert ackredit.get_used_items() == used


def test_probe_refuses_to_overwrite_prior_evidence(
    tools, detached, tmp_path, monkeypatch
):
    monkeypatch.setattr(tools.shutil, "which", lambda name: sys.executable)
    destination = tmp_path / "retained"
    destination.mkdir()
    original = destination / "retained.txt"
    original.write_text("Original evidence")
    with pytest.raises(FileExistsError):
        tools.check(detached, destination)
    assert original.read_text() == "Original evidence"


def test_missing_requested_engine_does_not_choose_another_route(
    tools, detached, tmp_path, monkeypatch
):
    monkeypatch.setattr(tools.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError, match="biber"):
        tools.check(detached, tmp_path / "missing")
    assert not (tmp_path / "missing").exists()


def test_engine_failure_propagates_with_retained_process_evidence(tools, tmp_path):
    steps = []
    with pytest.raises(subprocess.CalledProcessError) as caught:
        tools._run(
            [sys.executable, "-c", "import sys; print('reader failed'); sys.exit(7)"],
            tmp_path,
            steps,
        )
    assert caught.value.returncode == 7
    assert steps[0]["exit_code"] == 7
    assert (tmp_path / "process-1.stdout.txt").read_text() == "reader failed\n"
    assert json.loads((tmp_path / "processes.json").read_text())[0]["exit_code"] == 7


def test_mixed_encoding_diagnostics_retain_exact_bytes_and_process_status(
    tools, tmp_path
):
    steps = []
    command = [
        sys.executable,
        "-c",
        "import sys; sys.stdout.buffer.write(bytes([243])); sys.stderr.buffer.write(bytes([241])); sys.exit(9)",
    ]
    with pytest.raises(subprocess.CalledProcessError) as caught:
        tools._run(command, tmp_path, steps)
    assert caught.value.returncode == 9
    assert (tmp_path / "process-1.stdout.txt").read_bytes() == b"\xf3"
    assert (tmp_path / "process-1.stderr.txt").read_bytes() == b"\xf1"
    assert steps[0]["stdout_sha256"] == hashlib.sha256(b"\xf3").hexdigest()
    assert steps[0]["stderr_sha256"] == hashlib.sha256(b"\xf1").hexdigest()
    assert steps[0]["stderr"] == r"\xf1"
    assert json.loads((tmp_path / "processes.json").read_text())[0]["exit_code"] == 9


def test_retained_receipt_binds_originals_to_real_readers_and_styles():
    receipt = json.loads(
        (ROOT / "devtools/receipts/biblatex_receiving_122_2026-10-06.json").read_text()
    )
    assert receipt["issue"] == "uibcdf/ackredit#122"
    assert receipt["installed"]["before"] == receipt["installed"]["after"]
    original = ackredit.Attribution.from_dict(receipt["paired_input"]["payload"])
    assert (
        hashlib.sha256(original.to_json().encode()).hexdigest()
        == receipt["paired_input"]["sha256"]
    )
    for style, study in receipt["studies"].items():
        assert study["probe"]["style"] == style
        assert study["probe"]["input_sha256"] == receipt["paired_input"]["sha256"]
        assert study["probe"]["versions"]["biblatex"] == "3.19"
        assert study["probe"]["versions"]["biber"].strip() == "biber version: 2.19"
        for name, export in study["exports"].items():
            digest = hashlib.sha256(export["text"].encode()).hexdigest()
            assert digest == export["sha256"] == study["probe"]["files"][name]["sha256"]
        assert study["exports"]["references.bib"]["text"] == original.report("bibtex")
        _assert_reader(
            study["exports"]["reader.xml"]["text"],
            study["exports"]["manuscript.bbl"]["text"],
        )
        assert "Version 2.0" in _presentation(study["exports"]["rendered.txt"]["text"])
        for path, resource in study["probe"]["resources"].items():
            assert (
                resource["sha256"]
                == study["probe"]["loaded_tex_files"][resource["path"]]["sha256"]
            )
        for field, relative in (
            ("tool_sha256", "devtools/check_biblatex.py"),
            ("process_owner_sha256", "devtools/check_publication_tools.py"),
        ):
            assert (
                study["probe"][field]
                == receipt["sources"][relative]["sha256"]
                == hashlib.sha256(
                    receipt["sources"][relative]["text"].encode()
                ).hexdigest()
            )
    assert (
        receipt["studies"]["authoryear"]["exports"]["references.bib"]
        == receipt["studies"]["numeric"]["exports"]["references.bib"]
    )


def test_guidance_matches_the_observed_tools_and_warning_boundary():
    receipt = json.loads(
        (ROOT / "devtools/receipts/biblatex_receiving_122_2026-10-06.json").read_text()
    )
    prose = " ".join(
        (ROOT / "docs/content/user_guide/publication_tools.md").read_text().split()
    )
    assert (
        f"BibLaTeX {receipt['official_tools']['biblatex']['version']} / Biber {receipt['official_tools']['biber']['version']}"
        in prose
    )
    for style in receipt["studies"]:
        assert f"`{style}`" in prose
    assert "978-0-00-000000-0" in prose and "warning is retained" in prose
    assert "--require-biblatex-tools" in prose
    assert "general BibLaTeX/Biber compatibility" in prose
