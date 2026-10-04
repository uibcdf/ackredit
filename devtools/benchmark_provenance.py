"""Measure requested graph rendering, preserving before/after samples and sources."""

import argparse
import hashlib
import importlib.util
import json
import platform
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

import ackredit
from ackredit.formats import provenance


def measure(renderer, tree, samples, iterations):
    renderer(tree, {})
    times = []
    for _ in range(samples):
        start = time.perf_counter_ns()
        for _ in range(iterations):
            renderer(tree, {})
        times.append((time.perf_counter_ns() - start) / iterations / 1000)
    return {
        "unit": "microseconds per render",
        "samples": times,
        "median": statistics.median(times),
        "output_lines": len(renderer(tree, {}).splitlines()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline", default="136b5d6fb2751659dcfd5cacd68b30e82157c881"
    )
    parser.add_argument("--samples", type=int, default=15)
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    assert arguments.samples > 0 and arguments.iterations > 0
    root = Path(__file__).resolve().parents[1]
    original = subprocess.check_output(
        ["git", "show", f"{arguments.baseline}:ackredit/formats/provenance.py"],
        cwd=root,
    )
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "baseline.py"
        path.write_bytes(original)
        spec = importlib.util.spec_from_file_location(
            "ackredit.formats._benchmark_baseline", path
        )
        baseline = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(baseline)
        shared = {
            f"step{level}{suffix}": {
                "items": [],
                "children": [f"step{level + 1}a", f"step{level + 1}b"]
                if level < 9
                else [],
            }
            for level in range(10)
            for suffix in "ab"
        }
        ordinary = {
            f"step{index}": {
                "items": [],
                "children": [f"step{index + 1}"] if index < 19 else [],
            }
            for index in range(20)
        }
        results = {}
        for name, tree in (("ordinary_tree", ordinary), ("shared_graph", shared)):
            results[name] = {
                "nodes": len(tree),
                "edges": sum(len(n["children"]) for n in tree.values()),
                "before": measure(
                    baseline.render_tree, tree, arguments.samples, arguments.iterations
                ),
                "after": measure(
                    provenance.render_tree,
                    tree,
                    arguments.samples,
                    arguments.iterations,
                ),
            }
    receipt = {
        "schema": "ackredit.provenance-benchmark@1",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "ackredit": ackredit.__version__,
        "baseline_source": arguments.baseline,
        "baseline_provenance_sha256": hashlib.sha256(original).hexdigest(),
        "provenance_sha256": hashlib.sha256(
            Path(provenance.__file__).read_bytes()
        ).hexdigest(),
        "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "samples": arguments.samples,
        "iterations": arguments.iterations,
        "scope": "Synthetic graph rendering only; excludes tracking, capture, imports and report setup. Shared targets are expanded once after the fix; every edge remains drawn.",
        "cases": results,
    }
    arguments.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
