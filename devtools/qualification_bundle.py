"""Build one immutable development wheel bundle for installed receiving tests.

This is source qualification, not Conda staging or public release publication.
The released API baseline is built from its original source commit separately.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from email.parser import BytesParser
from pathlib import Path


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wheel_record(wheel: Path, *, package: str, source_commit: str) -> dict:
    """Identify wheel bytes, distribution identity and all shipped package files."""
    with zipfile.ZipFile(wheel) as archive:
        metadata_files = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        assert len(metadata_files) == 1, metadata_files
        metadata = BytesParser().parsebytes(archive.read(metadata_files[0]))
        assert metadata["Name"] == package, metadata["Name"]
        wheel_metadata = archive.read(metadata_files[0].replace("METADATA", "WHEEL"))
        assert b"Root-Is-Purelib: true" in wheel_metadata, wheel_metadata
        assert b"Tag: py3-none-any" in wheel_metadata, wheel_metadata
        files = {
            name: sha256(archive.read(name))
            for name in archive.namelist()
            if name.startswith(f"{package}/") and not name.endswith("/")
        }
        assert files and f"{package}/__init__.py" in files, files
    return {
        "package": package,
        "source_commit": source_commit,
        "version": metadata["Version"],
        "filename": wheel.name,
        "sha256": sha256(wheel.read_bytes()),
        "files": files,
    }


def build_bundle(sources: dict[str, Path], destination: Path) -> dict:
    """Refuse dirty sources and build each candidate only once, using isolation."""
    assert not destination.exists(), destination
    commits = {}
    for role, source in sources.items():
        state = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=source, text=True
        )
        assert not state, (role, state)
        commits[role] = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=source, text=True
        ).strip()
    destination.mkdir(parents=True)
    records = {}
    for role, source in sources.items():
        directory = destination / role
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--wheel-dir",
                str(directory),
                str(source),
            ],
            check=True,
            cwd=destination,
        )
        wheels = list(directory.glob("*.whl"))
        assert len(wheels) == 1, wheels
        package = "pyunitwizard" if role == "producer" else "ackredit"
        record = wheel_record(wheels[0], package=package, source_commit=commits[role])
        record["wheel"] = f"{role}/{wheels[0].name}"
        records[role] = record
    assert records["released"]["version"] == "0.9.0", records["released"]
    manifest = {"schema": "ackredit.receiving-bundle@1", "packages": records}
    (destination / "bundle.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def verify_bundle(directory: Path) -> dict:
    """Refuse changed archives or inconsistent captured distribution contents."""
    manifest = json.loads((directory / "bundle.json").read_text())
    assert manifest["schema"] == "ackredit.receiving-bundle@1", manifest["schema"]
    assert set(manifest["packages"]) == {"candidate", "producer", "released"}
    for role, record in manifest["packages"].items():
        relative = Path(record["wheel"])
        assert relative == Path(role) / record["filename"], relative
        wheel = directory / relative
        expected = wheel_record(
            wheel, package=record["package"], source_commit=record["source_commit"]
        )
        assert expected == {k: v for k, v in record.items() if k != "wheel"}, role
    return manifest


def verify_installed(module, record: dict) -> dict:
    """Reject editable/shadowed imports and compare installed files with the wheel."""
    import importlib.metadata

    origin = Path(module.__file__).resolve()
    assert "site-packages" in origin.parts, origin
    assert origin.is_relative_to(Path(sys.prefix).resolve()), (origin, sys.prefix)
    version = importlib.metadata.version(record["package"])
    assert module.__version__ == version == record["version"], (
        module.__version__,
        version,
        record["version"],
    )
    for relative, digest in record["files"].items():
        path = origin.parent.parent / relative
        assert sha256(path.read_bytes()) == digest, relative
    return {"version": version, "origin": str(origin), "wheel_sha256": record["sha256"]}


def summarize(directory: Path, bundle: Path) -> dict:
    """Require all eight passing cells with complete, non-skipped test evidence."""
    from pytest_receptor import read_artifact

    manifest = verify_bundle(bundle)
    expected = {
        (system, minor)
        for system in ("linux", "darwin")
        for minor in ("3.11", "3.12", "3.13", "3.14")
    }
    cells = list(directory.glob("*/identity.json"))
    assert len(cells) == len(expected), (len(cells), len(expected))
    seen = set()
    receipts = []
    for identity in cells:
        receipt = json.loads(identity.read_text())
        cell = (receipt["platform"], ".".join(receipt["python"].split(".")[:2]))
        assert cell in expected and cell not in seen, cell
        seen.add(cell)
        assert receipt["packages"] == manifest["packages"], cell
        if cell[0] == "darwin":
            assert receipt["architecture"] == "arm64", receipt["architecture"]
        events = read_artifact(identity.parent / "events.jsonl")
        assert events.complete and events.integrity_valid, cell
        final = events.final.data
        assert final["complete"] and final["outcome"] == "PASS", final
        assert final["exitstatus"] == 0, final
        counts = final["counts"]
        assert counts["collected"] == counts["executed"] == counts["passed"] == 5, (
            counts
        )
        assert not any(
            counts[name]
            for name in (
                "failed",
                "skipped",
                "xfailed",
                "xpassed",
                "errors",
                "not_executed",
                "deselected",
            )
        ), counts
        for filename in (
            "pipeline.json",
            "reader.json",
            "absence.json",
            "released-fallback.json",
            "tests.xml",
        ):
            assert (identity.parent / filename).is_file(), (cell, filename)
        receipt["test_outcome"] = {"outcome": final["outcome"], "counts": counts}
        receipts.append(receipt)
    assert seen == expected, (seen, expected)
    return {"schema": "ackredit.receiving-matrix@1", "cells": receipts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    for role in ("candidate", "producer", "released"):
        build.add_argument(f"--{role}", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("directory", type=Path)
    summary = subparsers.add_parser("summarize")
    summary.add_argument("directory", type=Path)
    summary.add_argument("--bundle", type=Path, required=True)
    summary.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    if arguments.command == "build":
        result = build_bundle(
            {
                role: getattr(arguments, role).resolve()
                for role in ("candidate", "producer", "released")
            },
            arguments.output.resolve(),
        )
    elif arguments.command == "verify":
        result = verify_bundle(arguments.directory.resolve())
    else:
        result = summarize(arguments.directory.resolve(), arguments.bundle.resolve())
        arguments.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"outcome": "PASS", "cells": len(result["cells"])}))
        return
    print(json.dumps({role: r["sha256"] for role, r in result["packages"].items()}))


if __name__ == "__main__":
    main()
