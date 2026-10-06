"""Ackredit lifecycle study, not a release gate or a universal overhead promise.

Run with the intended interpreter and dependencies. Every sample uses a fresh
process outside the checkout. Timing and tracemalloc runs are separate; memory
means Python allocations during the named stages, not RSS or dependency size.
Scientific cases require PyUnitWizard, NumPy, Pint and unyt; no import skips.
Existing benchmark_portable.py remains the warmed repeated-credit tool.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib
import importlib.metadata
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import tracemalloc
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter_ns
from types import ModuleType

_COLD = """
import sys, time
memory = sys.argv[2] == 'memory'
if memory:
    import gc, tracemalloc
    gc.collect()
    tracemalloc.start()
measurements = {}
preloaded = sorted(sys.modules)
def measure(name, operation):
    if memory:
        tracemalloc.reset_peak()
        before = tracemalloc.get_traced_memory()[0]
        result = operation()
        current, peak = tracemalloc.get_traced_memory()
        measurements[name] = dict(retained_delta_bytes=current-before, peak_extra_bytes=peak-before)
    else:
        start = time.perf_counter_ns()
        result = operation()
        measurements[name] = dict(elapsed_us=(time.perf_counter_ns()-start)/1000)
    return result
ackredit = measure('import', lambda: __import__('ackredit'))
roots = sorted({name.split('.')[0] for name in sys.modules})
measure('first_registration', lambda: ackredit.register_item(id='lifecycle:first', title='First reference'))
measure('first_credit', lambda: ackredit.track_item('lifecycle:first'))
if memory:
    tracemalloc.stop()
# Import the benchmark machinery only after all measured stages have finished.
import runpy, json
tools = runpy.run_path(sys.argv[1])
print(json.dumps(tools['cold_finished'](measurements, roots, preloaded)))
"""


def cold_finished(measurements, roots, preloaded):
    return {
        "measurements": measurements,
        "facts": {
            "loaded_roots_after_import": roots,
            "modules_before_import": preloaded,
            "plugins": [
                {"name": ep.name, "value": ep.value, "distribution": ep.dist.name}
                for ep in importlib.metadata.entry_points(group="ackredit.citations")
            ],
        },
        "identities": identities(),
    }


def child(command, **kwargs):
    """Preserve the failed process's evidence as well as its exit status."""
    try:
        return subprocess.run(
            command, text=True, capture_output=True, check=True, timeout=180, **kwargs
        )
    except subprocess.CalledProcessError as error:
        print(error.stdout + error.stderr, file=sys.stderr, end="")
        raise


def identities() -> dict:
    """Fingerprint actual loaded code separately from distribution metadata."""
    result = {}
    for name, distribution in (
        ("ackredit", "ackredit"),
        ("smonitor", "smonitor"),
        ("depdigest", "depdigest"),
        ("argdigest", "argdigest"),
        ("yaml", "PyYAML"),
        ("numpy", "numpy"),
        ("pyunitwizard", "pyunitwizard"),
        ("pint", "pint"),
        ("unyt", "unyt"),
    ):
        module = sys.modules.get(name)
        if module is None:
            continue
        origin = Path(module.__file__).resolve()
        digest = hashlib.sha256()
        paths = sorted(
            p
            for p in origin.parent.rglob("*")
            if p.is_file() and p.suffix in {".py", ".cff", ".yaml", ".toml"}
        )
        for path in paths:
            digest.update(path.relative_to(origin.parent).as_posix().encode() + b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
        metadata = importlib.metadata.distribution(distribution)
        entry = {
            "origin": str(origin),
            "runtime_version": getattr(module, "__version__", None),
            "distribution_version": metadata.version,
            "requirements": metadata.requires or [],
            "source_tree_sha256": digest.hexdigest(),
            "source_file_count": len(paths),
            "direct_url": json.loads(metadata.read_text("direct_url.json") or "null"),
        }
        root = origin.parent.parent
        if (root / ".git").exists():
            entry["checkout_head"] = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            entry["checkout_dirty"] = bool(
                subprocess.check_output(
                    ["git", "status", "--porcelain"], cwd=root, text=True
                ).strip()
            )
        result[name] = entry
    return result


class Stages:
    """Retain named timings or separate traced allocation peaks, never both."""

    def __init__(self, memory: bool):
        self.memory = memory
        self.values = {}
        if memory:
            gc.collect()
            tracemalloc.start()

    def call(self, name, operation):
        if self.memory:
            tracemalloc.reset_peak()
            before = tracemalloc.get_traced_memory()[0]
            result = operation()
            current, peak = tracemalloc.get_traced_memory()
            self.values[name] = {
                "retained_delta_bytes": current - before,
                "peak_extra_bytes": peak - before,
            }
        else:
            start = perf_counter_ns()
            result = operation()
            self.values[name] = {"elapsed_us": (perf_counter_ns() - start) / 1000}
        return result

    def finish(self):
        if self.memory:
            tracemalloc.stop()
        return self.values


def provider(size):
    """Controlled declarations: one reference and one exported function per unit."""
    module = ModuleType("lifecycle_provider")
    items, functions = [], {}
    for index in range(size):
        name = f"compute_{index}"
        setattr(module, name, lambda value: value * value)
        item_id = f"lifecycle:{index}"
        items.append({"id": item_id, "title": f"Reference {index}"})
        functions[name] = [{"item_id": item_id, "roles": ["software_description"]}]
    module.__ackredit__ = {
        "schema": "ackredit.provider@1",
        "software": {"name": module.__name__, "version": "1"},
        "items": items,
        "functions": functions,
    }
    return module


def worker(case: dict, memory=False) -> dict:
    kind, size = case["kind"], case.get("size", 1)
    if kind not in {
        "import",
        "activation",
        "science",
        "results",
        "references",
        "journal",
    }:
        raise ValueError(f"Unknown lifecycle case: {kind}")
    if size < 1 or case.get("captures", 1) < 1 or case.get("iterations", 1) < 1:
        raise ValueError("Case sizes, capture counts and iterations must be positive")
    facts = {}
    if kind == "import":
        response = child(
            [
                sys.executable,
                "-c",
                _COLD,
                str(Path(__file__).resolve()),
                "memory" if memory else "timing",
            ],
        )
        if response.stderr:
            print(response.stderr, file=sys.stderr, end="")
        return json.loads(response.stdout)
    else:
        import ackredit

        if kind == "activation":
            module = provider(size)
            original = module.compute_0
            observer = ackredit.observe_calls(module)
            stages = Stages(memory)
            stages.call("activation", observer.__enter__)
            stages.call("first_observed_call", lambda: module.compute_0(3))
            stages.call("deactivation", lambda: observer.__exit__(None, None, None))
            assert module.compute_0 is original
            facts["declared_references"] = size
            facts["declared_functions"] = size
        elif kind == "science":
            facts, stages = scientific(case, memory)
        else:
            for index in range(1 if kind == "results" else size):
                ackredit.register_item(
                    id=f"lifecycle:{index}", title=f"Reference {index}"
                )
            stages = Stages(memory)
            with ackredit.session("lifecycle"), ExitStack() as stack:
                if kind == "results":

                    def results():
                        retained = []
                        for index in range(size):
                            with ackredit.capture(f"result-{index}") as run:
                                ackredit.track_item("lifecycle:0", used_by="compute")
                            retained.append(run.attribution)
                        return retained

                    retained = stages.call("independent_results", results)
                    assert all(len(r.to_dict()["items"]) == 1 for r in retained)
                    facts["retained_results"] = len(retained)
                else:
                    runs = stages.call(
                        "capture_entry",
                        lambda: [
                            stack.enter_context(ackredit.capture(f"capture-{index}"))
                            for index in range(case.get("captures", 1))
                        ],
                    )
                    journal = Path.cwd() / "journal.jsonl"
                    if kind == "journal":
                        stages.call(
                            "journal_open", lambda: ackredit.enable_persistence(journal)
                        )
                        stack.callback(ackredit.close_persistence)

                    def track():
                        for index in range(size):
                            ackredit.track_target(f"node-{index}", parent="root")
                            ackredit.track_item(
                                f"lifecycle:{index}", used_by=f"node-{index}"
                            )

                    stages.call("unique_tracking", track)
                    result = stages.call("snapshot", lambda: runs[0].attribution)
                    encoded = stages.call("json_export", result.to_json)
                    rendered = stages.call(
                        "workflow_report", lambda: result.report(format="workflow")
                    )
                    bibtex = stages.call(
                        "bibtex_report", lambda: result.report(format="bibtex")
                    )
                    if kind == "journal":
                        stages.call("journal_close", ackredit.close_persistence)
                        facts["journal_bytes"] = journal.stat().st_size
                        from ackredit.core.session import read

                        assert len(read(journal)["used_items"]) == size
                    stages.call("capture_exit", stack.close)
                    data = result.to_dict()
                    assert ackredit.Attribution.from_json(encoded).to_dict() == data
                    assert all(
                        len(r.attribution.to_dict()["items"]) == size for r in runs
                    )
                    facts.update(
                        {
                            "references": len(data["items"]),
                            "nodes": len(data["usage_tree"]),
                            "edges": sum(
                                len(n["children"]) for n in data["usage_tree"].values()
                            ),
                            "json_bytes": len(encoded.encode()),
                            "workflow_bytes": len(rendered.encode()),
                            "bibtex_bytes": len(bibtex.encode()),
                        }
                    )
    measurements = stages.finish()
    return {"measurements": measurements, "facts": facts, "identities": identities()}


def scientific(case, memory):
    """Real dispatch; check values, units and references outside timed loops."""
    import numpy as np
    import pyunitwizard as puw

    import ackredit

    puw.configure.reset()
    puw.configure.load_library(["pint", "unyt"])
    values = np.arange(case["size"], dtype=float) + 1
    quantity = puw.quantity(values, "meter", form="pint")
    target = quantity._REGISTRY.centimeter
    mode = case["mode"]
    with ackredit.session("scientific control"), ExitStack() as stack:
        if mode != "ordinary":
            stack.enter_context(puw.attribution())
        if mode in {"observed", "capture", "evidence"}:
            stack.enter_context(ackredit.observe_calls(puw))
        run = None
        if mode in {"capture", "evidence"}:
            run = stack.enter_context(
                ackredit.capture(
                    "scientific result", record_evidence=mode == "evidence"
                )
            )

        def convert():
            return puw.convert(quantity, to_unit=target)

        convert()
        stages = Stages(memory)

        def repeated():
            for _ in range(case["iterations"]):
                result = convert()
            return result

        result = stages.call("conversions", repeated)
        measured = stages.finish()
        actual = puw.get_value(result)
        np.testing.assert_array_equal(actual, values * 100)
        assert result.units == target
        data = (run.attribution if run else ackredit.get_attribution()).to_dict()
        software = sorted({u["context"]["software"] for u in data["uses"]})
        expected_software = {"ordinary": [], "backend": ["pint"]}.get(
            mode, ["pint", "pyunitwizard"]
        )
        assert software == expected_software, (mode, software)
        for use in data["uses"]:
            version = importlib.metadata.version(use["context"]["software"])
            assert use["context"]["version"] == version
        evidence = run.evidence.to_dict() if mode == "evidence" else None
        if evidence is not None:
            assert run.evidence.attribution.to_dict() == data
        stages.values = measured
        return {
            "numerical_parity": True,
            "unit": str(result.units),
            "value_sha256": hashlib.sha256(actual.tobytes()).hexdigest(),
            "software": software,
            "references": len(data["items"]),
            "evidence_recorded": evidence is not None,
        }, stages


def summarize(samples):
    """Summarize every raw numeric field without hiding variation."""
    return {
        stage: {
            field: {
                "median": statistics.median(values),
                "minimum": min(values),
                "maximum": max(values),
                "spread": max(values) - min(values),
            }
            for field in measurements
            if (values := [sample["measurements"][stage][field] for sample in samples])
        }
        for stage, measurements in samples[0]["measurements"].items()
    }


def study(cases, samples, memory_samples):
    """Alternate scenario order; retain subprocess errors and actual identities."""
    results = {
        name: {"case": case, "timing_samples": [], "memory_samples": []}
        for name, case in cases.items()
    }
    identity_records = {}
    script = str(Path(__file__).resolve())
    with tempfile.TemporaryDirectory(prefix="ackredit-lifecycle-") as directory:
        for memory, count in ((False, samples), (True, memory_samples)):
            for index in range(count):
                ordered = list(cases.items())
                if index % 2:
                    ordered.reverse()
                for name, case in ordered:
                    sample_directory = Path(directory) / f"{memory}-{index}-{name}"
                    sample_directory.mkdir()
                    response = child(
                        [
                            sys.executable,
                            script,
                            "--worker",
                            json.dumps(case),
                            *(["--memory"] if memory else []),
                        ],
                        cwd=sample_directory,
                    )
                    sample = json.loads(response.stdout)
                    packages = sample.pop("identities")
                    identity_id = hashlib.sha256(
                        json.dumps(packages, sort_keys=True).encode()
                    ).hexdigest()
                    identity_records[identity_id] = packages
                    sample["identity_id"] = identity_id
                    sample["stderr"] = response.stderr
                    results[name][
                        "memory_samples" if memory else "timing_samples"
                    ].append(sample)
                print(
                    f"Completed {'allocation' if memory else 'timing'} sample {index + 1}/{count}",
                    file=sys.stderr,
                )
    for record in results.values():
        for mode in ("timing", "memory"):
            record[f"{mode}_summary"] = summarize(record[f"{mode}_samples"])
    for name in {name for packages in identity_records.values() for name in packages}:
        fingerprints = {
            (
                packages[name]["source_tree_sha256"],
                packages[name]["runtime_version"],
                packages[name]["distribution_version"],
            )
            for packages in identity_records.values()
            if name in packages
        }
        if len(fingerprints) != 1:
            raise RuntimeError(
                f"Loaded package changed during study: {name}; repeat with fixed sources"
            )
    return {"identities": identity_records, "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", help=argparse.SUPPRESS)
    parser.add_argument("--memory", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--samples", type=int, default=7)
    parser.add_argument("--memory-samples", type=int, default=3)
    parser.add_argument(
        "--scientific",
        action="store_true",
        help="Require and measure real PyUnitWizard conversion",
    )
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.worker:
        print(json.dumps(worker(json.loads(arguments.worker), arguments.memory)))
        return
    if arguments.samples < 2 or arguments.memory_samples < 2 or not arguments.output:
        parser.error("output is required; timing and memory need at least two samples")
    cases = {"cold_import": {"kind": "import"}}
    for size in (1, 100, 1000):
        cases[f"activation_{size}"] = {"kind": "activation", "size": size}
        cases[f"references_{size}"] = {"kind": "references", "size": size}
    for size in (1, 10, 100):
        cases[f"results_{size}"] = {"kind": "results", "size": size}
    for count in (4, 16):
        cases[f"captures_{count}"] = {
            "kind": "references",
            "size": 100,
            "captures": count,
        }
    for size in (100, 1000):
        cases[f"journal_{size}"] = {"kind": "journal", "size": size}
    if arguments.scientific:
        for size in (1, 100000):
            for mode in ("ordinary", "backend", "observed", "capture", "evidence"):
                cases[f"science_{size}_{mode}"] = {
                    "kind": "science",
                    "size": size,
                    "mode": mode,
                    "iterations": 1000 if size == 1 else 100,
                }
    receipt = {
        "schema": "ackredit.lifecycle-benchmark@1",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "method": "Fresh interpreter per case/sample, alternating case order; timing without tracemalloc; separate Python allocation runs. Import includes automatic installed plugin loading. Warm science excludes activation/setup; synthetic scaling includes first unique credits. No release qualification or distribution-installation measurement.",
        **study(cases, arguments.samples, arguments.memory_samples),
    }
    arguments.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Recorded {len(cases)} cases in {arguments.output}")


if __name__ == "__main__":
    main()
