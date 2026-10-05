"""Receiving evidence must reject changed bytes and editable source imports."""

import importlib.util
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "devtools"
spec = importlib.util.spec_from_file_location(
    "qualification_bundle", TOOLS / "qualification_bundle.py"
)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


@pytest.fixture
def candidate(tmp_path):
    records = {}
    for role, package in (
        ("candidate", "ackredit"),
        ("producer", "pyunitwizard"),
        ("released", "ackredit"),
    ):
        directory = tmp_path / role
        directory.mkdir()
        wheel = directory / f"{package}-0.9.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel, "w") as archive:
            archive.writestr(f"{package}/__init__.py", "__version__ = '0.9.0'\n")
            archive.writestr(f"{package}/CITATION.cff", "title: Original citation\n")
            archive.writestr(
                f"{package}-0.9.0.dist-info/METADATA",
                f"Name: {package}\nVersion: 0.9.0\n",
            )
            archive.writestr(
                f"{package}-0.9.0.dist-info/WHEEL",
                "Root-Is-Purelib: true\nTag: py3-none-any\n",
            )
        record = bundle.wheel_record(wheel, package=package, source_commit="a" * 40)
        record["wheel"] = f"{role}/{wheel.name}"
        records[role] = record
    manifest = {"schema": "ackredit.receiving-bundle@1", "packages": records}
    (tmp_path / "bundle.json").write_text(json.dumps(manifest))
    return tmp_path, manifest


def test_changed_archive_cannot_reuse_the_original_receiving_identity(candidate):
    directory, manifest = candidate
    assert bundle.verify_bundle(directory) == manifest
    wheel = directory / manifest["packages"]["candidate"]["wheel"]
    # ZIP readers allow appended data; payload equivalence is weaker than identity.
    wheel.write_bytes(wheel.read_bytes() + b"changed archive")
    with pytest.raises(AssertionError):
        bundle.verify_bundle(directory)


def test_editable_origin_is_not_an_installed_receiving_gate(candidate):
    directory, manifest = candidate
    source = directory / "ackredit" / "__init__.py"
    module = SimpleNamespace(__file__=str(source), __version__="0.9.0")
    with pytest.raises(AssertionError):
        bundle.verify_installed(module, manifest["packages"]["candidate"])


def test_one_successful_cell_cannot_certify_the_receiving_matrix(candidate):
    directory, _ = candidate
    cells = directory / "cells"
    cell = cells / "receiving-linux-py314"
    cell.mkdir(parents=True)
    (cell / "identity.json").write_text("{}")
    with pytest.raises(AssertionError):
        bundle.summarize(cells, directory)


@pytest.fixture
def complete_matrix(candidate, monkeypatch):
    import pytest_receptor

    directory, manifest = candidate
    counts = {
        "collected": 7,
        "executed": 7,
        "passed": 7,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
        "errors": 0,
        "not_executed": 0,
        "deselected": 0,
    }
    final = {"complete": True, "outcome": "PASS", "exitstatus": 0, "counts": counts}
    # Test the consumer's interpretation of the provider's public parsed result.
    # Integrity parsing remains owned by Pytest Receptor, not copied here.
    parsed = SimpleNamespace(
        complete=True, integrity_valid=True, final=SimpleNamespace(data=final)
    )
    monkeypatch.setattr(pytest_receptor, "read_artifact", lambda path: parsed)
    cells = directory / "cells"
    for system in ("linux", "darwin"):
        for minor in ("3.11", "3.12", "3.13", "3.14"):
            cell = cells / f"{system}-{minor}"
            cell.mkdir(parents=True)
            receipt = {
                "platform": system,
                "python": f"{minor}.0",
                "architecture": "arm64" if system == "darwin" else "x86_64",
                "packages": manifest["packages"],
            }
            (cell / "identity.json").write_text(json.dumps(receipt))
            for filename in (
                "pipeline.json",
                "reader.json",
                "reported-pipeline.json",
                "workflow-report.md",
                "workflow-reader.json",
                "absence.json",
                "released-fallback.json",
                "prepared-reuse.json",
                "tests.xml",
            ):
                (cell / filename).write_text("test fixture")
    return cells, directory, final


@pytest.mark.parametrize(
    "missing_evidence", ["skipped", "deselected", "not_executed", "failed"]
)
def test_a_pass_label_does_not_hide_unqualified_tests(
    complete_matrix, missing_evidence
):
    cells, directory, final = complete_matrix
    assert len(bundle.summarize(cells, directory)["cells"]) == 8
    final["counts"][missing_evidence] = 1
    with pytest.raises(AssertionError):
        bundle.summarize(cells, directory)


def test_duplicate_platform_minor_does_not_replace_a_missing_cell(complete_matrix):
    cells, directory, _ = complete_matrix
    duplicate = cells / "darwin-3.14" / "identity.json"
    duplicate.write_bytes((cells / "darwin-3.13" / "identity.json").read_bytes())
    with pytest.raises(AssertionError):
        bundle.summarize(cells, directory)


def test_previous_six_test_gate_does_not_qualify_combined_optimization(complete_matrix):
    cells, directory, final = complete_matrix
    for key in ("collected", "executed", "passed"):
        final["counts"][key] = 6
    with pytest.raises(AssertionError):
        bundle.summarize(cells, directory)


def test_missing_prepared_reuse_evidence_is_refused(complete_matrix):
    cells, directory, _ = complete_matrix
    (cells / "linux-3.14" / "prepared-reuse.json").unlink()
    with pytest.raises(AssertionError):
        bundle.summarize(cells, directory)


def test_changed_installed_citation_is_rejected_even_with_the_right_version(
    candidate, monkeypatch
):
    import importlib.metadata
    import sys

    directory, manifest = candidate
    record = manifest["packages"]["candidate"]
    prefix = directory / "environment"
    site = prefix / "site-packages"
    with zipfile.ZipFile(directory / record["wheel"]) as archive:
        archive.extractall(site)
    module = SimpleNamespace(
        __file__=str(site / "ackredit" / "__init__.py"), __version__="0.9.0"
    )
    monkeypatch.setattr(sys, "prefix", str(prefix))
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "0.9.0")
    assert bundle.verify_installed(module, record)["version"] == "0.9.0"
    (site / "ackredit" / "CITATION.cff").write_text("title: Different citation\n")
    with pytest.raises(AssertionError):
        bundle.verify_installed(module, record)


@pytest.fixture
def conda_matrix(complete_matrix):
    cells, directory, final = complete_matrix
    manifest = json.loads((directory / "bundle.json").read_text())
    candidate = {
        "kind": "conda",
        "package": "ackredit",
        "source_commit": "a" * 40,
        "version": "0.10.0",
        "filename": "ackredit-0.10.0-py_0.tar.bz2",
        "sha256": "b" * 64,
    }
    manifest["schema"] = "ackredit.receiving-bundle@2"
    manifest["packages"]["candidate"] = candidate
    (directory / "bundle.json").write_text(json.dumps(manifest))
    for identity in cells.glob("*/identity.json"):
        receipt = json.loads(identity.read_text())
        receipt["packages"] = manifest["packages"]
        receipt["providers"] = {"ackredit": {"conda_sha256": candidate["sha256"]}}
        identity.write_text(json.dumps(receipt))
        proof = dict(
            {
                key: candidate[key]
                for key in ("package", "version", "filename", "sha256")
            },
            state="verified",
            subdir="noarch",
            platform="linux-64" if receipt["platform"] == "linux" else "osx-arm64",
            python=".".join(receipt["python"].split(".")[:2]),
        )
        for name in ("conda-before.json", "conda-after.json"):
            (identity.parent / name).write_text(json.dumps(proof))
    return cells, directory, final


@pytest.mark.parametrize(
    "field", ["sha256", "version", "filename", "platform", "python", "state"]
)
def test_conda_receiving_requires_same_file_provenance_after_science(
    conda_matrix, field
):
    cells, directory, _ = conda_matrix
    assert len(bundle.summarize(cells, directory)["cells"]) == 8
    path = cells / "linux-3.14" / "conda-after.json"
    proof = json.loads(path.read_text())
    proof[field] = "different"
    path.write_text(json.dumps(proof))
    with pytest.raises(AssertionError):
        bundle.summarize(cells, directory)


def test_conda_receiving_refuses_a_wheel_identity(conda_matrix):
    _, directory, _ = conda_matrix
    manifest = json.loads((directory / "bundle.json").read_text())
    record = manifest["packages"]["candidate"]
    record["filename"] = "ackredit-0.10.0-py3-none-any.whl"
    (directory / "bundle.json").write_text(json.dumps(manifest))
    with pytest.raises(AssertionError):
        bundle.verify_bundle(directory)
