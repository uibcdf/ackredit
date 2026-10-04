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
