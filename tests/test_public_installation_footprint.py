"""Guard public-installation provenance and statements, never timing thresholds."""

import hashlib
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "devtools/receipts/public_installation_118_2026-10-06.json"


def _current_footprint():
    records = [
        json.loads(path.read_text())
        for path in (ROOT / "devtools/receipts").glob("public_*.json")
    ]
    return max(
        (
            record
            for record in records
            if record.get("schema") == "ackredit.public-footprint@1"
        ),
        key=lambda record: record["checked_at"],
    )


@pytest.fixture
def tools(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "devtools"))
    module = importlib.import_module("benchmark_public_installation")
    # Unit cases exercise this bounded Linux profile even in the macOS CI lane.
    # Replace the consumer's handles, never the process-wide sys/platform modules.
    monkeypatch.setattr(
        module, "sys", SimpleNamespace(prefix=sys.prefix, platform="linux")
    )
    monkeypatch.setattr(module, "platform", SimpleNamespace(machine=lambda: "x86_64"))
    return module


@pytest.fixture
def native(tmp_path):
    prefix = tmp_path / "prefix"
    (prefix / "conda-meta").mkdir(parents=True)
    (prefix / "payload").write_bytes(b"installed payload")
    (prefix / "alias").symlink_to("payload")
    archive = tmp_path / "original.conda"
    archive.write_bytes(b"original archive")
    record = {
        "name": "python",
        "version": "3.14.8",
        "build": "fixture",
        "subdir": "linux-64",
        "fn": archive.name,
        "url": "https://conda.anaconda.org/conda-forge/linux-64/original.conda",
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "size": archive.stat().st_size,
        "depends": [],
        "files": ["payload", "alias"],
        "package_tarball_full_path": str(archive),
    }
    metadata = prefix / "conda-meta/python.json"
    metadata.write_text(json.dumps(record))
    return prefix, archive, record, metadata


def test_linked_size_is_logical_and_does_not_count_symlink_targets_twice(tools, native):
    prefix, _, _, _ = native
    result = tools._inventory(prefix)
    assert result["archive_bytes"] == len(b"original archive")
    assert result["linked_regular_bytes"] == len(b"installed payload")
    assert result["packages"]["python"]["linked"] == {
        "regular_bytes": len(b"installed payload"),
        "regular_file_count": 1,
        "symlink_count": 1,
    }


@pytest.mark.parametrize("system,machine", [("win32", "x86_64"), ("linux", "aarch64")])
def test_other_platforms_cannot_be_reported_as_the_linux_x86_profile(
    tools, monkeypatch, tmp_path, system, machine
):
    monkeypatch.setattr(tools.sys, "platform", system)
    monkeypatch.setattr(tools.platform, "machine", lambda: machine)
    with pytest.raises(ValueError, match="requires Linux x86-64"):
        tools.measure(tmp_path, {}, {})


def test_replaced_transitive_archive_cannot_keep_its_original_identity(tools, native):
    prefix, archive, _, _ = native
    archive.write_bytes(b"replaced archive")  # Same length, different bytes.
    with pytest.raises(ValueError, match="Cached original archive differs"):
        tools._inventory(prefix)


@pytest.mark.parametrize("relative", ["../outside", "/tmp/outside"])
def test_native_linked_paths_cannot_escape_the_receiving_prefix(
    tools, native, relative
):
    prefix, _, record, metadata = native
    record["files"] = [relative]
    metadata.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="Linked path outside"):
        tools._inventory(prefix)


def test_missing_linked_files_are_not_omitted_from_the_measurement(tools, native):
    prefix, _, _, _ = native
    (prefix / "payload").unlink()
    with pytest.raises(FileNotFoundError):
        tools._inventory(prefix)


@pytest.mark.parametrize(
    "url",
    [
        "https://conda.anaconda.org/uibcdf/label/staging/noarch/original.conda",
        "https://conda.anaconda.org/other/linux-64/original.conda",
    ],
)
def test_staging_and_other_channels_cannot_establish_public_closure(tools, native, url):
    prefix, _, record, metadata = native
    record["url"] = url
    metadata.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="ordinary public channels"):
        tools._inventory(prefix)


@pytest.mark.parametrize(
    "failure", ["public_marker", "public_digest", "control_version"]
)
def test_contradictory_receipts_fail_before_behavioral_measurement(
    tools, monkeypatch, failure
):
    receipt = json.loads(RECEIPT.read_text())
    delivery = json.loads(
        (
            ROOT
            / "devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json"
        ).read_text()
    )
    public = receipt["shared_public_verification"]
    if failure == "public_marker":
        public["state"] = "unverified"
    elif failure == "public_digest":
        public["files"][0]["sha256"] = "0" * 64
    else:
        receipt["control"]["packages"]["python"]["version"] = "3.13.0"
    current = Path(sys.prefix).resolve()
    monkeypatch.setattr(
        tools,
        "_inventory",
        lambda path: receipt["receiving"] if path == current else receipt["control"],
    )

    def must_not_measure(**kwargs):
        raise AssertionError("A contradictory installation reached the smoke stage")

    monkeypatch.setattr(tools.installed_smoke, "verify", must_not_measure)
    with pytest.raises(ValueError, match="receipt|Python control"):
        tools.measure(Path(receipt["control"]["prefix"]), delivery, public)


def test_source_loaded_by_a_worker_cannot_count_as_installed_evidence(
    tools, monkeypatch
):
    receipt = json.loads(RECEIPT.read_text())
    delivery = json.loads(
        (
            ROOT
            / "devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json"
        ).read_text()
    )
    current = Path(sys.prefix).resolve()
    monkeypatch.setattr(
        tools,
        "_inventory",
        lambda path: receipt["receiving"] if path == current else receipt["control"],
    )
    monkeypatch.setattr(tools.installed_smoke, "verify", lambda **kwargs: {})
    monkeypatch.setattr(
        tools.lifecycle,
        "study",
        lambda *args: {
            "identities": {
                "shadowed": {
                    "ackredit": {
                        "origin": str(ROOT / "ackredit/__init__.py"),
                        "distribution_version": "0.11.0",
                    }
                }
            }
        },
    )
    with pytest.raises(ValueError, match="Loaded provider outside"):
        tools.measure(
            Path(receipt["control"]["prefix"]),
            delivery,
            receipt["shared_public_verification"],
        )


def test_footprint_retains_the_original_public_file_and_unchanged_python_control():
    receipt = json.loads(RECEIPT.read_text())
    delivery = json.loads(
        (
            ROOT
            / "devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json"
        ).read_text()
    )
    assert receipt["public_identity"] == {
        "filename": delivery["filename"],
        "sha256": delivery["sha256"],
        "producer_source": delivery["producer_source"],
    }
    control = receipt["control"]["packages"]
    receiving = receipt["receiving"]["packages"]
    for name, record in control.items():
        assert {k: v for k, v in record.items() if k != "linked"} == {
            k: v for k, v in receiving[name].items() if k != "linked"
        }
    added = sorted(receiving.keys() - control.keys())
    assert added == receipt["increment"]["packages"]
    assert receipt["increment"]["archive_bytes"] == sum(
        receiving[n]["size"] for n in added
    )
    assert receipt["increment"]["linked_regular_bytes"] == sum(
        receiving[n]["linked"]["regular_bytes"] for n in added
    )
    for environment in ("control", "receiving"):
        records = receipt[environment]["packages"]
        assert receipt[environment]["package_count"] == len(records)
        assert receipt[environment]["archive_bytes"] == sum(
            r["size"] for r in records.values()
        )
        assert receipt[environment]["linked_regular_bytes"] == sum(
            r["linked"]["regular_bytes"] for r in records.values()
        )
    assert receipt["receiving"]["linked_regular_bytes"] - receipt["control"][
        "linked_regular_bytes"
    ] == (
        receipt["increment"]["linked_regular_bytes"]
        + receipt["increment"]["shared_linked_regular_bytes_delta"]
    )


def test_documented_public_argdigest_closure_does_not_require_numpy():
    receipt = _current_footprint()
    installed = receipt["receiving"]["packages"]
    assert "numpy" not in installed
    assert not any(d.split()[0] == "numpy" for d in installed["argdigest"]["depends"])
    page = (ROOT / "docs/content/about/installation.md").read_text()
    assert (
        f"ArgDigest {installed['argdigest']['version']} does not require NumPy" in page
    )
    assert "requires `numpy`, which conda brings with it" not in page
    assert "PyYAML" in page and "libyaml" in page
    assert f"{receipt['increment']['archive_bytes'] / 1024:.0f} KiB" in page
    assert f"{receipt['increment']['linked_regular_bytes'] / 1048576:.2f} MiB" in page
    performance = " ".join(
        (ROOT / "docs/content/about/performance.md").read_text().split()
    )
    assert f"{receipt['increment']['archive_bytes']:,} compressed bytes" in performance
    assert f"{receipt['increment']['linked_regular_bytes']:,}" in performance
    assert receipt["installed_smoke"]["portable_attribution"] == "passed"
    samples = receipt["lifecycle"]["results"]["cold_import"]
    for sample in samples["timing_samples"] + samples["memory_samples"]:
        assert "numpy" not in sample["facts"]["loaded_roots_after_import"]
        assert "ackredit" not in sample["facts"]["modules_before_import"]
        assert sample["stderr"] == ""


def test_followup_records_the_selected_public_providers_and_owning_issue():
    receipt = _current_footprint()
    assert receipt["issue"] == "uibcdf/ackredit#119"
    installed = receipt["receiving"]["packages"]
    expected = {
        "smonitor": (
            "0.19.0",
            "py_1",
            "4b876b4993b1e2caeed40851402a931f3b245ed7c1916d9483d81bc90274e31c",
        ),
        "argdigest": (
            "0.15.0",
            "py_0",
            "b0f22038a8ad1c888dca10adedaca0fa14d2383a685a97c0602b7ca05f29d6a1",
        ),
    }
    public = {r["package"]: r for r in receipt["shared_public_verification"]["files"]}
    for name, (version, build, digest) in expected.items():
        assert (
            installed[name]["version"],
            installed[name]["build"],
            installed[name]["sha256"],
        ) == (version, build, digest)
        assert public[name]["sha256"] == digest
    assert receipt["comparison_with_118"]["changed_packages"] == [
        "argdigest",
        "smonitor",
    ]
    assert (
        receipt["public_identity"] == json.loads(RECEIPT.read_text())["public_identity"]
    )


def test_measurement_rejects_a_foreign_or_missing_owning_issue(tools, tmp_path):
    for issue in ("uibcdf/smonitor#1", "uibcdf/ackredit#0", ""):
        with pytest.raises(ValueError, match="owning Ackredit issue"):
            tools.measure(tmp_path, {}, {}, issue=issue)


def test_public_samples_keep_timing_and_allocations_separate():
    receipt = json.loads(RECEIPT.read_text())
    for result in receipt["lifecycle"]["results"].values():
        for mode, expected_fields, count in (
            ("timing", {"elapsed_us"}, 7),
            ("memory", {"peak_extra_bytes", "retained_delta_bytes"}, 3),
        ):
            samples = result[f"{mode}_samples"]
            assert len(samples) == count
            for sample in samples:
                assert sample["stderr"] == ""
                assert all(
                    set(m) == expected_fields for m in sample["measurements"].values()
                )
                identities = receipt["lifecycle"]["identities"][sample["identity_id"]]
                for name, identity in identities.items():
                    assert Path(identity["origin"]).is_relative_to(
                        receipt["receiving"]["prefix"]
                    )
                    package = "pyyaml" if name == "yaml" else name
                    assert (
                        identity["distribution_version"]
                        == receipt["receiving"]["packages"][package]["version"]
                    )
