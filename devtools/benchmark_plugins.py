"""Measure controlled, normally installed citation/format packs.

Cold import reuses benchmark_lifecycle's minimal fresh process. Warm stages use
another fresh process. Build/install/setup and integrity checks are not timed.
Requires a directory containing manifest.json and its original core wheels;
the manifest maps import/distribution names to qualification_bundle records.
Fixtures model registration work, not third-party scientific implementations.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import sys
import tempfile
import venv
from pathlib import Path

import benchmark_lifecycle as lifecycle
import qualification_bundle as qualification


def write_pack(source: Path, index: int, references: int, failure=None) -> str:
    """Create an installable fixture using the actual two entry-point contracts."""
    if (
        index < 0
        or references < 1
        or failure
        not in {
            None,
            "citations",
            "formats",
            "conflict",
        }
    ):
        raise ValueError("Invalid plugin fixture dimensions or failure mode")
    name = f"ackredit_bench_pack{index}"
    package = source / name
    package.mkdir(parents=True)
    (source / "pyproject.toml").write_text(
        f'''[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"
[project]
name = "{name}"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = []
[project.entry-points."ackredit.citations"]
pack{index} = "{name}:register"
[project.entry-points."ackredit.formats"]
pack{index} = "{name}.formats:register"
[tool.setuptools.packages.find]
include = ["{name}"]
'''
    )
    (package / "__init__.py").write_text(
        f"""__version__ = "1.0.0"
registration_calls = 0
REFERENCES = {references}
def register():
    global registration_calls
    registration_calls += 1
    if {failure == "citations"}:
        raise RuntimeError("Controlled broken citation pack")
    import ackredit
    ids = []
    for index in range(REFERENCES):
        item_id = f"pack{index}:reference{{index}}"
        ackredit.register_item(id=item_id, title=f"Pack {index} reference {{index}}",
                              note="Fixture version " + __version__)
        ids.append(item_id)
    ackredit.bind(__name__ + ".compute", ids)
    ackredit.add_injection("fixture_host{index}", ids)
def compute(value):
    try:
        import ackredit
    except ModuleNotFoundError as error:
        if error.name != "ackredit":
            raise
    else:
        ackredit.credit_bound(__name__ + ".compute")
    return value * value
"""
    )
    (package / "formats.py").write_text(
        f'''registration_calls = 0
def render(used, items):
    return "|".join(sorted(used))
def register():
    global registration_calls
    registration_calls += 1
    if {failure == "formats"}:
        raise RuntimeError("Controlled broken format pack")
    import ackredit
    ackredit.available_formats()  # Reentry must not start another discovery.
    ackredit.register_format("{"bibtex" if failure == "conflict" else f"pack{index}"}",
                             render, "pack{index}.txt")
'''
    )
    return name


def build_packs(sources: list[Path], wheels: Path, *, isolated=True) -> dict:
    """Use the standard backend; retain original wheel bytes and package files."""
    wheels.mkdir(parents=True)
    lifecycle.child(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            *([] if isolated else ["--no-build-isolation"]),
            "--wheel-dir",
            str(wheels),
            *map(str, sources),
        ]
    )
    return {
        wheel.name.split("-", 1)[0]: qualification.wheel_record(
            wheel,
            package=wheel.name.split("-", 1)[0],
            source_commit="controlled fixture; source files bound by wheel file digests",
        )
        for wheel in sorted(wheels.glob("*.whl"))
    }


def environment(directory: Path, wheels: list[Path]) -> Path:
    """Normally install local wheels in a disposable, inherited-dependency venv."""
    venv.EnvBuilder(system_site_packages=True, with_pip=True).create(directory)
    python = directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if wheels:
        lifecycle.child(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--ignore-installed",
                *map(str, wheels),
            ],
            cwd=directory,
        )
    return python


def operations(case: dict, memory=False) -> dict:
    """Measure reload/discovery/capture/report while guarding original references."""
    import ackredit
    from ackredit.core.registry import Registry

    packs = [importlib.import_module(name) for name in case["packs"]]
    assert all(pack.registration_calls == 1 for pack in packs)
    assert not any(pack.__name__ + ".formats" in sys.modules for pack in packs)
    assert ackredit.get_used_items() == {}, "Plugin registration must not credit use"
    expected = {
        f"pack{index}:reference{reference}"
        for index, pack in enumerate(packs)
        for reference in range(pack.REFERENCES)
    }
    if not packs:
        ackredit.register_item(id="control", title="No-plugin control")
        expected = {"control"}
    with lifecycle.Stages(memory) as stages:
        stages.call("citation_reload", ackredit.load_plugins)
        formats = stages.call("format_discovery", ackredit.available_formats)
        stages.call("format_discovery_repeat", ackredit.available_formats)

        def captures():
            results = []
            for label in ("first", "reused"):
                with ackredit.capture(label) as run:
                    if packs:
                        for pack in packs:
                            assert pack.compute(3) == 9
                    else:
                        ackredit.track_item("control")
                results.append(run.attribution)
            return results

        results = stages.call("independent_captures", captures)
        result = results[0]
        requested = "pack0" if packs else "text"
        rendered = stages.call(
            "requested_report", lambda: result.report(format=requested)
        )
        repeated = stages.call(
            "repeated_report", lambda: result.report(format=requested)
        )
        encoded = stages.call("detached_export", result.to_json)
        restored = stages.call(
            "detached_read", lambda: ackredit.Attribution.from_json(encoded)
        )
        workflow = stages.call(
            "workflow_report", lambda: restored.report(format="workflow")
        )
        measurements = stages.finish()
    assert rendered == repeated
    assert restored.to_dict() == result.to_dict()
    for captured in results:
        data = captured.to_dict()
        assert {item["id"] for item in data["items"]} == expected
        if packs:
            assert all(
                item["note"] == "Fixture version 1.0.0" for item in data["items"]
            )
    assert results[0].to_dict()["items"] == results[1].to_dict()["items"]
    assert len(Registry.items) == len(expected)
    for index, pack in enumerate(packs):
        assert pack.registration_calls == 2
        assert f"pack{index}" in formats
        assert (
            importlib.import_module(pack.__name__ + ".formats").registration_calls == 1
        )
        assert len(Registry.injections[f"fixture_host{index}"]) == pack.REFERENCES
    if packs:
        assert rendered == "|".join(sorted(expected))
    verified = {
        name: qualification.verify_installed(importlib.import_module(name), record)
        for name, record in {**case.get("core", {}), **case["packs"]}.items()
    }
    return {
        "measurements": measurements,
        "facts": {
            "packs": len(packs),
            "references": len(expected),
            "captures": len(results),
            "format_callbacks": len(packs),
            "citation_callbacks_per_pack": 2,
            "json_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            "workflow_bytes": len(workflow.encode()),
            "plugin_files_verified": verified,
        },
        "identities": lifecycle.identities(),
        "detached": encoded,
    }


def study(
    core_directory: Path,
    destination: Path,
    samples=7,
    memory_samples=3,
    *,
    isolated=True,
):
    """Keep separate installed variants and fresh processes per stage/sample."""
    if destination.exists() or min(samples, memory_samples) < 2:
        raise ValueError(
            "A new destination and at least two samples per mode are required"
        )
    tool_paths = [
        Path(__file__).resolve(),
        Path(lifecycle.__file__),
        Path(qualification.__file__),
    ]
    tool_digests = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in tool_paths
    }
    core = json.loads((core_directory / "manifest.json").read_text())
    core_wheels = []
    for name, record in core.items():
        wheel = core_directory / record["filename"]
        assert (
            qualification.wheel_record(
                wheel, package=name, source_commit=record["source_commit"]
            )
            == record
        )
        core_wheels.append(wheel)
    destination.mkdir(parents=True)
    cases = {}
    for count, references in ((0, 1), (1, 1), (10, 1), (1, 1000), (10, 100)):
        name = f"packs_{count}_references_{references}"
        directory = destination / name
        sources = [directory / "sources" / f"pack{index}" for index in range(count)]
        for index, source in enumerate(sources):
            write_pack(source, index, references)
        packs = (
            build_packs(sources, directory / "wheels", isolated=isolated)
            if sources
            else {}
        )
        python = environment(
            directory / "env",
            core_wheels
            + [directory / "wheels" / r["filename"] for r in packs.values()],
        )
        case = {"packs": packs, "core": core}
        (directory / "case.json").write_text(json.dumps(case, indent=2) + "\n")
        cases[name] = {
            "case": case,
            "python": str(python),
            "timing_samples": [],
            "memory_samples": [],
        }
    script = str(Path(__file__).resolve())
    for memory, count in ((False, samples), (True, memory_samples)):
        for index in range(count):
            ordered = list(cases.items())
            if index % 2:
                ordered.reverse()
            for name, record in ordered:
                sample = {}
                for stage in ("cold", "operations"):
                    with tempfile.TemporaryDirectory(
                        prefix="ackredit-plugin-sample-"
                    ) as cwd:
                        response = lifecycle.child(
                            [
                                record["python"],
                                script,
                                "--worker",
                                stage,
                                "--case",
                                str(destination / name / "case.json"),
                                *(["--memory"] if memory else []),
                            ],
                            cwd=cwd,
                        )
                    result = json.loads(response.stdout)
                    if stage == "operations":
                        (destination / name / "detached.json").write_text(
                            result.pop("detached")
                        )
                    sample[stage] = result
                    sample[stage]["stderr"] = response.stderr
                record["memory_samples" if memory else "timing_samples"].append(sample)
            print(
                f"Completed {'allocation' if memory else 'timing'} sample {index + 1}/{count}",
                file=sys.stderr,
            )
    fingerprints = {}
    for name, record in cases.items():
        for mode in ("timing", "memory"):
            for stage in ("cold", "operations"):
                records = [sample[stage] for sample in record[f"{mode}_samples"]]
                record.setdefault(f"{mode}_summary", {})[stage] = lifecycle.summarize(
                    records
                )
                for sample in records:
                    for package, identity in sample["identities"].items():
                        fingerprints.setdefault(package, set()).add(
                            (
                                identity["source_tree_sha256"],
                                identity["runtime_version"],
                                identity["distribution_version"],
                            )
                        )
        reader = lifecycle.child(
            [
                cases["packs_0_references_1"]["python"],
                script,
                "--reader",
                str(destination / name / "detached.json"),
            ],
            cwd=destination,
        )
        record["plugin_free_reader"] = json.loads(reader.stdout)
        assert (
            record["plugin_free_reader"]["references"]
            == record["timing_samples"][0]["operations"]["facts"]["references"]
        )
        assert (
            record["plugin_free_reader"]["json_sha256"]
            == record["memory_samples"][-1]["operations"]["facts"]["json_sha256"]
        )
    assert all(len(values) == 1 for values in fingerprints.values()), (
        "Core sources changed during study"
    )
    assert tool_digests == {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in tool_paths
    }, "Measurement tools changed during study"
    return {
        "schema": "ackredit.plugin-benchmark@1",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "benchmark_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "tool_sha256": tool_digests,
        "method": "Controlled normal wheel installations; inherited Conda dependencies. Alternating case order; fresh cold and separate warm-stage processes per sample; timing without tracing, separate Python allocations. Build/install and integrity checks excluded. No third-party workload, clean dependency closure, RSS or release qualification.",
        "cases": cases,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core-wheels", type=Path)
    parser.add_argument("--destination", type=Path)
    parser.add_argument("--samples", type=int, default=7)
    parser.add_argument("--memory-samples", type=int, default=3)
    parser.add_argument("--no-build-isolation", action="store_true")
    parser.add_argument(
        "--worker", choices=("cold", "operations"), help=argparse.SUPPRESS
    )
    parser.add_argument("--case", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--memory", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--reader", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.reader:
        import ackredit

        assert not importlib.metadata.entry_points(group="ackredit.citations")
        assert not importlib.metadata.entry_points(group="ackredit.formats")
        encoded = args.reader.read_text()
        detached = ackredit.Attribution.from_json(encoded)
        assert detached.to_dict() == json.loads(encoded)
        assert detached.report(format="workflow")
        assert ackredit.get_used_items() == {}
        assert not any(name.startswith("ackredit_bench_pack") for name in sys.modules)
        print(
            json.dumps(
                {
                    "references": len(detached.to_dict()["items"]),
                    "execution_credit": False,
                    "json_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
                }
            )
        )
    elif args.worker:
        result = (
            lifecycle.worker({"kind": "import"}, args.memory)
            if args.worker == "cold"
            else operations(json.loads(args.case.read_text()), args.memory)
        )
        print(json.dumps(result))
    else:
        if not args.core_wheels or not args.destination:
            parser.error("core-wheels and destination are required")
        result = study(
            args.core_wheels.resolve(),
            args.destination.resolve(),
            args.samples,
            args.memory_samples,
            isolated=not args.no_build_isolation,
        )
        (args.destination / "receipt.json").write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print(
            f"Recorded {len(result['cases'])} installed variants in {args.destination}"
        )


if __name__ == "__main__":
    main()
