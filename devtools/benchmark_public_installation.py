"""Measure an existing public Ackredit Conda installation against a Python control.

This bounded profile requires Linux x86-64/Python 3.14. Create both environments
with native Conda first, using separate fresh caches
and the documented strict public channels. Run this script with the public
environment's interpreter outside the checkout. It requires the original
archives to remain in their native caches and a shared public-verification
receipt. It never installs, publishes or changes dependency requirements.

Archive bytes mean compressed package sizes. Linked regular-file bytes are
logical lengths, including recorded bytecode, excluding symlinks, directories,
unrecorded files and Conda metadata. They are not physical disk usage or RSS.
Import timing and Python allocations reuse benchmark_lifecycle's fresh workers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import benchmark_lifecycle as lifecycle
import installed_smoke


def _inventory(prefix: Path) -> dict:
    records = {}
    for path in sorted((prefix / "conda-meta").glob("*.json")):
        native = json.loads(path.read_text())
        name = native["name"]
        if name in records:
            raise ValueError(f"Duplicate installed package: {name}")
        url = urlparse(native["url"])
        if (
            url.scheme != "https"
            or url.hostname != "conda.anaconda.org"
            or url.path.split("/")[1] not in {"uibcdf", "conda-forge"}
            or "/label/" in url.path
        ):
            raise ValueError(f"Package outside the ordinary public channels: {name}")
        archive = Path(native["package_tarball_full_path"])
        with archive.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != native["sha256"] or archive.stat().st_size != native["size"]:
            raise ValueError(f"Cached original archive differs: {name}")
        files = native["files"]
        if len(files) != len(set(files)):
            raise ValueError(f"Duplicate linked paths: {name}")
        regular_bytes = regular_count = symlinks = 0
        for relative in files:
            item = Path(relative)
            if item.is_absolute() or ".." in item.parts:
                raise ValueError(f"Linked path outside the environment: {relative}")
            item = prefix / item
            # Never walk through a linked parent into another environment.
            if not item.parent.resolve().is_relative_to(prefix):
                raise ValueError(f"Linked parent outside the environment: {relative}")
            info = item.lstat()  # Missing installed files must fail, not disappear.
            if stat.S_ISREG(info.st_mode):
                regular_bytes += info.st_size
                regular_count += 1
            elif stat.S_ISLNK(info.st_mode):
                symlinks += 1
            else:
                raise ValueError(f"Unexpected linked file type: {relative}")
        records[name] = {
            key: native[key]
            for key in (
                "name",
                "version",
                "build",
                "subdir",
                "fn",
                "url",
                "sha256",
                "size",
                "depends",
            )
        }
        records[name]["linked"] = {
            "regular_bytes": regular_bytes,
            "regular_file_count": regular_count,
            "symlink_count": symlinks,
        }
    if "python" not in records:
        raise ValueError("The control and receiving prefixes need Conda Python records")
    return {
        "prefix": str(prefix),
        "packages": records,
        "package_count": len(records),
        "archive_bytes": sum(r["size"] for r in records.values()),
        "linked_regular_bytes": sum(
            r["linked"]["regular_bytes"] for r in records.values()
        ),
    }


def measure(
    control: Path,
    delivery: dict,
    public: dict,
    samples=7,
    memory_samples=3,
    *,
    issue="uibcdf/ackredit#118",
):
    """Retain actual public closure and bounded Ackredit import/first-report costs.

    Refuse source/shadowed providers, a stale public identity, replaced cached
    archives, changed control coordinates or changed recorded file lengths
    during the study. The Python-only control must not contain Ackredit.
    This observes one host/closure; it does not qualify a new release or solver.
    """
    if samples < 2 or memory_samples < 2:
        raise ValueError("Timing and allocation each require at least two samples")
    if not re.fullmatch(r"uibcdf/ackredit#[1-9][0-9]*", issue):
        raise ValueError("The study needs an owning Ackredit issue")
    if sys.platform != "linux" or platform.machine() != "x86_64":
        raise ValueError("This study profile requires Linux x86-64")
    prefix, control = Path(sys.prefix).resolve(), control.resolve()
    before, baseline = _inventory(prefix), _inventory(control)
    if prefix == control or "ackredit" in baseline["packages"]:
        raise ValueError("Use an independent Python-only control")
    installed = before["packages"]["ackredit"]
    if (
        public["state"] != "verified"
        or public["schema"] != "molsyssuite.public-conda@1"
    ):
        raise ValueError("A successful shared public-verification receipt is required")
    coordinate = next(p for p in public["files"] if p["package"] == "ackredit")
    for key, actual in (
        ("version", installed["version"]),
        ("filename", installed["fn"]),
        ("sha256", installed["sha256"]),
        ("url", installed["url"]),
    ):
        if coordinate[key] != actual:
            raise ValueError(f"Public receipt differs from the installed file: {key}")
    if (
        delivery["published_version"] != installed["version"]
        or delivery["filename"] != installed["fn"]
        or delivery["sha256"] != installed["sha256"]
        or delivery["public_poststate"]["state"] != "verified"
    ):
        raise ValueError("The installed public file differs from its original delivery")
    a, b = before["packages"], baseline["packages"]
    changed = [
        name
        for name in a.keys() & b.keys()
        if {key: value for key, value in a[name].items() if key != "linked"}
        != {key: value for key, value in b[name].items() if key != "linked"}
    ]
    if changed or b.keys() - a.keys():
        raise ValueError(
            f"The public environment changes the Python control: {changed}"
        )
    tools = {
        path.name: path
        for path in (
            Path(__file__),
            Path(lifecycle.__file__),
            Path(installed_smoke.__file__),
        )
    }
    hashes = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in tools.items()
    }
    # Native recorded-file size is captured before any behavioral imports here.
    smoke = installed_smoke.verify(
        expected_python="3.14", expected_version=installed["version"]
    )
    results = lifecycle.study(
        {
            "cold_import": {"kind": "import"},
            "first_report": {"kind": "references", "size": 1, "repeat_report": True},
        },
        samples,
        memory_samples,
    )
    if _inventory(prefix) != before or _inventory(control) != baseline:
        raise RuntimeError("Recorded installed file lengths changed during the study")
    if hashes != {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in tools.items()
    }:
        raise RuntimeError("Measurement tools changed during the study")
    for identities in results["identities"].values():
        for name, identity in identities.items():
            origin = Path(identity["origin"])
            if not origin.is_relative_to(prefix) or "site-packages" not in origin.parts:
                raise ValueError(
                    f"Loaded provider outside the receiving prefix: {name}"
                )
            package = "pyyaml" if name == "yaml" else name
            if identity["distribution_version"] != a[package]["version"]:
                raise ValueError(
                    f"Loaded provider differs from its Conda version: {name}"
                )
    added = sorted(a.keys() - b.keys())
    return {
        "schema": "ackredit.public-footprint@1",
        "issue": issue,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "platform": sys.platform,
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "public_identity": {
            "filename": installed["fn"],
            "sha256": installed["sha256"],
            "producer_source": delivery["producer_source"],
        },
        "shared_public_verification": public,
        "control": baseline,
        "receiving": before,
        "increment": {
            "packages": added,
            "archive_bytes": sum(a[name]["size"] for name in added),
            "linked_regular_bytes": sum(
                a[name]["linked"]["regular_bytes"] for name in added
            ),
            "changed_control_packages": changed,
            "shared_linked_regular_bytes_delta": sum(
                a[name]["linked"]["regular_bytes"] - b[name]["linked"]["regular_bytes"]
                for name in a.keys() & b.keys()
            ),
        },
        "installed_smoke": smoke,
        "lifecycle": results,
        "tools": hashes,
        "limits": [
            "One Linux/Python 3.14 public closure; no new release qualification.",
            "Archive lengths and recorded regular-file lengths, not RSS or physical disk usage.",
            "Native recorded files include bytecode; unrecorded later imports are excluded.",
            "Fresh processes use warmed OS/filesystem caches after smoke verification.",
            "No installation latency benchmark, scientific workload or third-party plugin claim.",
            "Public runtime identities differ from the newer developer-wheel studies.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--delivery-receipt", type=Path, required=True)
    parser.add_argument("--public-verification", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=7)
    parser.add_argument("--memory-samples", type=int, default=3)
    parser.add_argument("--issue", default="uibcdf/ackredit#118")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be new; retain original receipts")
    result = measure(
        args.control,
        json.loads(args.delivery_receipt.read_text()),
        json.loads(args.public_verification.read_text()),
        args.samples,
        args.memory_samples,
        issue=args.issue,
    )
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
