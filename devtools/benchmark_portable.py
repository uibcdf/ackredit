"""Measure repeated credits; never use these timings as a scientific release gate.

Run from the repository root with ``python devtools/benchmark_portable.py``.
Samples use fresh sessions, warm each scenario, and report all samples in
microseconds per operation. Imports, declaration and capture entry/exit are
outside the timed credit loop. Snapshot/render measurements include detachment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
from contextlib import ExitStack
from pathlib import Path
from time import perf_counter_ns
from types import ModuleType

import ackredit


def measure(iterations: int, samples: int) -> dict:
    ackredit.register_item(
        id="benchmark:article",
        type="article",
        title="Portable capture benchmark",
        authors=["Example, Ana", "Example, Ben"],
        year=2026,
        doi="10.1234/example",
    )
    context = {"software": "benchmark", "version": "1", "options": ["a", "b"]}
    results = {}
    scenarios = ["plain", "contextual", "capture", "nested", "snapshot", "bibtex"]
    provider = ModuleType("benchmark_provider")

    def compute(value):
        return value * value

    provider.compute = compute
    provider.__ackredit__ = {
        "schema": "ackredit.provider@1",
        "software": {"name": "benchmark", "version": "1"},
        "items": [
            {
                "id": "benchmark:article",
                "type": "article",
                "title": "Portable capture benchmark",
                "authors": ["Example, Ana", "Example, Ben"],
                "year": 2026,
                "doi": "10.1234/example",
            }
        ],
        "functions": {
            "compute": [
                {"item_id": "benchmark:article", "roles": ["software_description"]}
            ]
        },
    }
    if hasattr(ackredit, "observe_calls"):
        scenarios.extend(
            [
                "provider_inactive",
                "provider_active",
                "provider_capture",
                "provider_nested",
            ]
        )
    prepared_credit = None
    if hasattr(ackredit, "prepare_credit"):
        prepared_credit = ackredit.prepare_credit(
            "benchmark:article",
            "benchmark.compute",
            roles=["software_description"],
            context=context,
        )
        scenarios.extend(["prepared", "prepared_capture", "prepared_nested"])
    for scenario in scenarios:
        timings = []
        count = (
            min(iterations, 100) if scenario in ("snapshot", "bibtex") else iterations
        )
        for _ in range(samples):
            with ackredit.session("benchmark"), ExitStack() as stack:
                if scenario in (
                    "capture",
                    "nested",
                    "prepared_capture",
                    "prepared_nested",
                ):
                    stack.enter_context(ackredit.capture("outer"))
                if scenario in ("nested", "prepared_nested"):
                    stack.enter_context(ackredit.capture("inner"))
                if scenario in (
                    "provider_active",
                    "provider_capture",
                    "provider_nested",
                ):
                    stack.enter_context(ackredit.observe_calls(provider))
                if scenario in ("provider_capture", "provider_nested"):
                    stack.enter_context(ackredit.capture("outer"))
                if scenario == "provider_nested":
                    stack.enter_context(ackredit.capture("inner"))

                def credit():
                    ackredit.track_item(
                        "benchmark:article",
                        used_by="benchmark.compute",
                        **(
                            {}
                            if scenario == "plain"
                            else {"roles": ["software_description"], "context": context}
                        ),
                    )

                credit()
                operation = credit
                if scenario.startswith("prepared"):
                    operation = prepared_credit
                elif scenario.startswith("provider_"):

                    def operation():
                        return provider.compute(3)
                elif scenario == "snapshot":
                    operation = ackredit.get_attribution
                elif scenario == "bibtex":

                    def operation():
                        return ackredit.get_attribution().report(format="bibtex")

                operation()
                start = perf_counter_ns()
                for _ in range(count):
                    operation()
                timings.append((perf_counter_ns() - start) / count / 1000)
        results[scenario] = {
            "iterations": count,
            "samples_us": timings,
            "median_us": statistics.median(timings),
            "minimum_us": min(timings),
            "spread_us": max(timings) - min(timings),
        }
    source = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
    ).stdout.strip()
    return {
        "schema": "ackredit.benchmark.portable@1",
        "source": source,
        "dirty": bool(dirty),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "ackredit_origin": ackredit.__file__,
        "runtime_files_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name in (
                "core/attribution.py",
                "core/collector.py",
                "core/providers.py",
            )
            if (path := Path(ackredit.__file__).parent / name).is_file()
        },
        "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "samples": samples,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--samples", type=int, default=7)
    arguments = parser.parse_args()
    if arguments.iterations < 1 or arguments.samples < 2:
        parser.error("iterations must be positive and samples at least two")
    print(json.dumps(measure(arguments.iterations, arguments.samples), indent=2))


if __name__ == "__main__":
    main()
