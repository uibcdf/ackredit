"""Guard measurement isolation and retained results, never a timing threshold."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "benchmark_lifecycle", ROOT / "devtools/benchmark_lifecycle.py"
)
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def test_startup_separates_discovery_and_preserves_repeated_report():
    result = benchmark.study(
        {
            "first": {"kind": "references", "repeat_report": True},
            "separated": {
                "kind": "references",
                "separate_format_discovery": True,
                "repeat_report": True,
            },
        },
        2,
        2,
    )
    for mode in ("timing_samples", "memory_samples"):
        for first, separated in zip(
            result["results"]["first"][mode],
            result["results"]["separated"][mode],
        ):
            assert "format_discovery" not in first["measurements"]
            assert "format_discovery" in separated["measurements"]
            assert "repeated_workflow_report" in first["measurements"]
            assert "workflow" in separated["facts"]["formats"]
            assert (
                first["facts"]["workflow_bytes"] == separated["facts"]["workflow_bytes"]
            )


def test_cold_import_is_not_primed_by_benchmark_machinery(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = benchmark.worker({"kind": "import"})
    before = result["facts"]["modules_before_import"]
    assert "ackredit" not in before
    assert "importlib.metadata" not in before
    assert "numpy" not in before
    assert set(result["measurements"]) == {
        "import",
        "first_registration",
        "first_credit",
    }
    assert result["identities"]["ackredit"]["source_file_count"] > 0


@pytest.mark.parametrize("memory", [False, True])
def test_each_capture_gets_all_references_and_journal_round_trips(
    tmp_path, monkeypatch, memory, clean_registry
):
    monkeypatch.chdir(tmp_path)
    result = benchmark.worker({"kind": "journal", "size": 4, "captures": 3}, memory)
    assert result["facts"]["references"] == 4
    assert result["facts"]["nodes"] == 5
    assert result["facts"]["edges"] == 4
    assert result["facts"]["journal_bytes"] > 0
    assert "journal_close" in result["measurements"]
    for measurement in result["measurements"].values():
        assert set(measurement) == (
            {"retained_delta_bytes", "peak_extra_bytes"} if memory else {"elapsed_us"}
        )


def test_activation_restores_exports_and_separates_first_call(clean_registry):
    result = benchmark.worker({"kind": "activation", "size": 3})
    assert result["facts"] == {"declared_references": 3, "declared_functions": 3}
    assert set(result["measurements"]) == {
        "activation",
        "first_observed_call",
        "deactivation",
    }


def test_study_preserves_raw_samples_and_independent_results():
    result = benchmark.study({"independent": {"kind": "results", "size": 3}}, 2, 2)
    record = result["results"]["independent"]
    assert len(record["timing_samples"]) == len(record["memory_samples"]) == 2
    for sample in record["timing_samples"] + record["memory_samples"]:
        assert sample["facts"]["retained_results"] == 3
        assert "ackredit" in result["identities"][sample["identity_id"]]
        assert sample["stderr"] == ""
    times = [
        sample["measurements"]["independent_results"]["elapsed_us"]
        for sample in record["timing_samples"]
    ]
    summary = record["timing_summary"]["independent_results"]["elapsed_us"]
    assert summary["minimum"] == min(times)
    assert summary["maximum"] == max(times)


def test_journal_files_are_isolated_between_cases_and_samples():
    result = benchmark.study(
        {
            "small": {"kind": "journal", "size": 2},
            "larger": {"kind": "journal", "size": 3},
        },
        2,
        2,
    )
    for record in result["results"].values():
        samples = record["timing_samples"] + record["memory_samples"]
        assert all(s["facts"]["references"] == record["case"]["size"] for s in samples)
        assert len({s["facts"]["journal_bytes"] for s in samples}) == 1


def test_failing_worker_cannot_be_summarized_as_success():
    import subprocess

    with pytest.raises(subprocess.CalledProcessError):
        benchmark.study(
            {
                "broken": {
                    "kind": "unknown",
                }
            },
            2,
            2,
        )


def test_changing_loaded_sources_cannot_produce_a_successful_study(monkeypatch):
    import json
    from types import SimpleNamespace

    calls = []

    def changing_child(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(
            stdout=json.dumps(
                {
                    "measurements": {"stage": {"elapsed_us": 1}},
                    "facts": {},
                    "identities": {
                        "provider": {
                            "source_tree_sha256": "before"
                            if len(calls) == 1
                            else "after",
                            "runtime_version": "1",
                            "distribution_version": "1",
                        }
                    },
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(benchmark, "child", changing_child)
    with pytest.raises(RuntimeError, match="Loaded package changed.*provider"):
        benchmark.study({"case": {"kind": "references", "size": 1}}, 2, 2)


def test_scoped_diagnostics_require_actual_scientific_cases(tmp_path):
    import subprocess
    import sys

    output = tmp_path / "study.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "devtools/benchmark_lifecycle.py"),
            "--scoped-diagnostics",
            "--output",
            str(output),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "scoped diagnostics require the scientific cases" in result.stderr
    assert not output.exists()
