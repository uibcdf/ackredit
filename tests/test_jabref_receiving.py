"""Real manager import and persisted libraries preserve original works (#123)."""

import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import ackredit

ROOT = Path(__file__).resolve().parents[1]
IDS = {
    "software:1.0",
    "software:2.0",
    "dataset:2024",
    "article:2023",
    "edited:structured",
    "preferred:collection",
}


def _assert_records(source, imported, reopened):
    # The reader can recode titles/pages. Compare manager output to the same
    # independent reader's original export, never to replacement source records.
    assert imported == reopened == source
    items = {item["id"]: item for item in imported}
    assert set(items) == IDS
    for item_id, version in (
        ("software:1.0", "1.0"),
        ("software:2.0", "2.0"),
        ("dataset:2024", "2024.1"),
    ):
        assert items[item_id]["version"] == version
    assert items["software:1.0"]["DOI"] == "10.5555/ackredit.fixture.software"
    assert (
        items["software:2.0"]["DOI"]
        == "https://doi.org/10.5555/ackredit.fixture.software"
    )
    assert items["software:2.0"]["author"] == [
        {"literal": "Research and Development, Consortium"}
    ]
    assert items["dataset:2024"]["author"] == [
        {"literal": "Instituto de Investigación, México"}
    ]
    assert items["article:2023"]["author"] == [{"family": "García", "given": "Ana"}]
    assert items["edited:structured"]["publisher"] == "Example Press"
    preferred = items["preferred:collection"]
    assert preferred["type"] == "book" and "version" not in preferred
    assert preferred["DOI"] == "10.5555/ackredit.fixture.collection"
    assert preferred["editor"] == [
        {
            "family": "Cruz",
            "given": "María",
            "dropping-particle": "de la",
            "suffix": "III",
        },
        {"literal": "Research and Development, Consortium"},
    ]


@pytest.fixture
def tools(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "devtools"))
    return importlib.import_module("check_jabref")


@pytest.fixture
def detached(tmp_path):
    prior = json.loads(
        (ROOT / "devtools/receipts/doi_presentation_121_2026-10-06.json").read_text()
    )
    path = tmp_path / "original.json"
    path.write_text(
        ackredit.Attribution.from_dict(prior["paired_input"]["payload"]).to_json()
    )
    return path


@pytest.fixture
def engines(request):
    root = request.config.getoption("--jabref-distribution")
    missing = []
    if not root or not (Path(root) / "lib/runtime/bin/JabRef").is_file():
        missing.append("--jabref-distribution with a portable Linux launcher")
    if shutil.which("pandoc") is None:
        missing.append("pandoc")
    if missing:
        message = "JabRef receiving tools unavailable: " + ", ".join(missing)
        if request.config.getoption("--require-jabref-tools"):
            pytest.fail(message)
        pytest.skip(message)
    return Path(root)


@pytest.mark.parametrize("directory_name", ["receiving", "receiving with spaces"])
def test_real_manager_import_and_fresh_preferences_reopen_preserve_originals(
    tools, detached, tmp_path, engines, directory_name
):
    original = detached.read_bytes()
    used = ackredit.get_used_items()
    directory = tmp_path / directory_name
    result = tools.check(detached, directory, distribution=engines)
    _assert_records(
        *(
            json.loads((directory / name).read_text())
            for name in ("source-read.json", "imported-read.json", "reopened-read.json")
        )
    )
    exported = (directory / "references.bib").read_bytes()
    assert (directory / "imported.bib").read_bytes() == exported + b"\n"
    assert (directory / "reopened.bib").read_bytes() == exported + b"\n"
    assert result["distribution"]["before"] == result["distribution"]["after"]
    assert result["original_preserved"] and result["export_preserved"]
    assert not result["new_execution_credit"]
    assert all(step["exit_code"] == 0 for step in result["processes"])
    manager = [
        step
        for step in result["processes"]
        if step["command"][0] == str(engines.resolve() / "lib/runtime/bin/JabRef")
    ]
    assert len(manager) == 3 and all("-n" in step["command"] for step in manager)
    profiles = [step["environment_overrides"]["JAVA_TOOL_OPTIONS"] for step in manager]
    assert len(set(profiles)) == 3
    assert all(str(directory) in profile for profile in profiles)
    assert detached.read_bytes() == original
    assert ackredit.get_used_items() == used


@pytest.fixture
def fake_distribution(tmp_path):
    root = tmp_path / "manager"
    launcher = root / "lib/runtime/bin/JabRef"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("#!/bin/sh\nprintf 'manager failed\\n'\nexit 7\n")
    launcher.chmod(0o700)
    return root


def test_missing_requested_manager_fails_without_fallback(tools, detached, tmp_path):
    with pytest.raises(FileNotFoundError, match="JabRef launcher"):
        tools.check(detached, tmp_path / "evidence", distribution=tmp_path / "absent")
    assert not (tmp_path / "evidence").exists()


def test_missing_independent_reader_fails(
    tools, detached, tmp_path, fake_distribution, monkeypatch
):
    monkeypatch.setattr(tools.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError, match="pandoc"):
        tools.check(detached, tmp_path / "evidence", distribution=fake_distribution)
    assert not (tmp_path / "evidence").exists()


def test_existing_evidence_is_never_replaced(
    tools, detached, tmp_path, fake_distribution, monkeypatch
):
    monkeypatch.setattr(tools.shutil, "which", lambda name: sys.executable)
    destination = tmp_path / "evidence"
    destination.mkdir()
    retained = destination / "retained.txt"
    retained.write_text("Original evidence")
    with pytest.raises(FileExistsError):
        tools.check(detached, destination, distribution=fake_distribution)
    assert retained.read_text() == "Original evidence"


def test_broken_selected_launcher_preserves_failure_and_exact_command(
    tools, detached, tmp_path, fake_distribution, monkeypatch
):
    monkeypatch.setattr(tools.shutil, "which", lambda name: sys.executable)
    destination = tmp_path / "evidence"
    with pytest.raises(subprocess.CalledProcessError) as caught:
        tools.check(detached, destination, distribution=fake_distribution)
    assert caught.value.returncode == 7
    recorded = json.loads((destination / "processes.json").read_text())[0]
    assert recorded["command"] == [
        str(fake_distribution.resolve() / "lib/runtime/bin/JabRef"),
        "-n",
        "-v",
    ]
    assert recorded["exit_code"] == 7
    assert (destination / "process-1.stdout.txt").read_bytes() == b"manager failed\n"


def test_receiving_cannot_write_inside_the_distribution(
    tools, detached, fake_distribution
):
    with pytest.raises(ValueError, match="outside the distribution"):
        tools.check(
            detached, fake_distribution / "evidence", distribution=fake_distribution
        )
    assert not (fake_distribution / "evidence").exists()


def test_process_environment_override_is_child_local_and_explicit(
    tools, tmp_path, monkeypatch
):
    monkeypatch.setenv("ACKREDIT_RECEIVING_PROFILE", "parent")
    steps = []
    response = tools._run(
        [
            sys.executable,
            "-c",
            "import os; print(os.environ['ACKREDIT_RECEIVING_PROFILE'])",
        ],
        tmp_path,
        steps,
        env={"ACKREDIT_RECEIVING_PROFILE": "child"},
    )
    assert response == "child\n"
    assert os.environ["ACKREDIT_RECEIVING_PROFILE"] == "parent"
    assert steps[0]["environment_overrides"] == {"ACKREDIT_RECEIVING_PROFILE": "child"}


def test_retained_receipt_binds_real_manager_output_to_verified_originals():
    receipt = json.loads(
        (ROOT / "devtools/receipts/jabref_receiving_123_2026-10-06.json").read_text()
    )
    assert receipt["issue"] == "uibcdf/ackredit#123"
    assert receipt["installed"]["before"] == receipt["installed"]["after"]
    probe = receipt["study"]["probe"]
    assert probe["distribution"]["before"] == probe["distribution"]["after"]
    assert "JabRef 5.15--2024-07-10--1eb3493" in probe["versions"]["jabref"]
    attribution = ackredit.Attribution.from_dict(receipt["original_input"]["payload"])
    assert (
        hashlib.sha256(attribution.to_json().encode()).hexdigest()
        == probe["input_sha256"]
        == receipt["original_input"]["sha256"]
    )
    exports = receipt["study"]["exports"]
    for name, export in exports.items():
        assert (
            hashlib.sha256(export["text"].encode()).hexdigest()
            == export["sha256"]
            == probe["files"][name]["sha256"]
        )
    assert exports["references.bib"]["text"] == attribution.report("bibtex")
    assert (
        exports["imported.bib"]["text"]
        == exports["reopened.bib"]["text"]
        == exports["references.bib"]["text"] + "\n"
    )
    _assert_records(
        *(
            json.loads(exports[name]["text"])
            for name in ("source-read.json", "imported-read.json", "reopened-read.json")
        )
    )
    for field, relative in (
        ("tool_sha256", "devtools/check_jabref.py"),
        ("process_owner_sha256", "devtools/check_publication_tools.py"),
    ):
        assert (
            probe[field]
            == receipt["sources"][relative]["sha256"]
            == hashlib.sha256(receipt["sources"][relative]["text"].encode()).hexdigest()
        )
    assert "WARN: JabRef could not open the key store" in probe["warnings"]


def test_guidance_names_the_actual_manager_route_and_qualification_limits():
    page = " ".join(
        (ROOT / "docs/content/user_guide/publication_tools.md").read_text().split()
    )
    assert "JabRef 5.15" in page
    assert "--require-jabref-tools" in page and "--jabref-distribution" in page
    assert "one final newline" in page
    assert "WARN: JabRef could not open the key store" in page
    assert "GUI interaction, enrichment, synchronization" in page
    assert "Additional managers, GUI routes and styles need their own" in page
