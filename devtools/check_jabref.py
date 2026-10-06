"""Receive a saved bibliography in an isolated portable JabRef no-GUI CLI.

The caller supplies an official Linux portable distribution. Its exact
lib/runtime/bin/JabRef launcher imports/saves BibTeX, then a fresh process with
separate preferences reopens/resaves the manager library. Pandoc independently
reads each file; its conversions never replace original attribution or fields.
No tools are installed or downloaded. Prior destinations and missing requested
tools fail. GUI interaction, synchronization and online enrichment are untested.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from check_publication_tools import _run, _sha

import ackredit
from ackredit.formats.bibtex import cite_keys


def _inventory(directory: Path) -> dict:
    """Identify all shipped regular files by relative name, bytes and digest."""
    return {
        path.relative_to(directory).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": _sha(path.read_bytes()),
        }
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _preferences(destination: Path, name: str) -> dict:
    """Select fresh preferences/cache roots for one manager process only."""
    root = destination / name
    for child in ("home", "preferences", "tmp", "config", "cache", "data"):
        (root / child).mkdir(parents=True, exist_ok=False)
    properties = {
        "user.home": root / "home",
        "java.util.prefs.userRoot": root / "preferences",
        "java.util.prefs.systemRoot": root / "preferences",
        "java.io.tmpdir": root / "tmp",
    }
    return {
        "JAVA_TOOL_OPTIONS": " ".join(
            f"-D{key}={shlex.quote(str(path))}" for key, path in properties.items()
        ),
        "JDK_JAVA_OPTIONS": "",
        "_JAVA_OPTIONS": "",
        "XDG_CONFIG_HOME": str(root / "config"),
        "XDG_CACHE_HOME": str(root / "cache"),
        "XDG_DATA_HOME": str(root / "data"),
    }


def check(attribution_path: Path, destination: Path, *, distribution: Path) -> dict:
    """Run actual import/resave and independent readers with original-byte guards.

    Supports the official Linux portable layout and its runtime launcher, not a
    generic GUI executable or alternate Java runtime. Manager and output trees
    must be separate. Each manager invocation receives independent preferences.
    Missing/broken tools and nonzero commands fail without route substitution.
    """
    distribution = distribution.resolve()
    destination = destination.resolve()
    launcher = distribution / "lib/runtime/bin/JabRef"
    if not launcher.is_file():
        raise FileNotFoundError(
            f"Required portable JabRef launcher unavailable: {launcher}"
        )
    if destination.is_relative_to(distribution):
        raise ValueError("JabRef evidence must be outside the distribution tree")
    if (pandoc := shutil.which("pandoc")) is None:
        raise FileNotFoundError(
            "Required independent publication reader unavailable: pandoc"
        )
    original = attribution_path.read_bytes()
    attribution = ackredit.Attribution.from_json(original.decode("utf-8"))
    before = attribution.to_dict()
    used_before = ackredit.get_used_items()
    shipped_before = _inventory(distribution)
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "attribution.json").write_bytes(original)
    exported = attribution.report("bibtex").encode("utf-8")
    (destination / "references.bib").write_bytes(exported)
    steps: list[dict] = []
    versions = {
        "jabref": _run(
            [str(launcher), "-n", "-v"],
            destination,
            steps,
            env=_preferences(destination, "version-profile"),
        ),
        "pandoc": _run([pandoc, "--version"], destination, steps),
    }
    _run(
        [str(launcher), "-n", "-i", "references.bib,bibtex", "-o", "imported.bib"],
        destination,
        steps,
        env=_preferences(destination, "import-profile"),
    )
    _run(
        [str(launcher), "-n", "-o", "reopened.bib", "imported.bib"],
        destination,
        steps,
        env=_preferences(destination, "reopen-profile"),
    )
    for role, filename in (
        ("source", "references.bib"),
        ("imported", "imported.bib"),
        ("reopened", "reopened.bib"),
    ):
        _run(
            [
                pandoc,
                "-f",
                "bibtex",
                "-t",
                "csljson",
                filename,
                "-o",
                f"{role}-read.json",
            ],
            destination,
            steps,
        )
    shipped_after = _inventory(distribution)
    if shipped_before != shipped_after:
        raise RuntimeError("JabRef receiving changed original distribution files")
    if attribution.to_dict() != before or attribution_path.read_bytes() != original:
        raise RuntimeError("JabRef receiving changed original attribution")
    if (destination / "references.bib").read_bytes() != exported:
        raise RuntimeError("JabRef receiving changed original BibTeX export")
    if ackredit.get_used_items() != used_before:
        raise RuntimeError("JabRef receiving recorded new execution credit")
    return {
        "schema": "ackredit.jabref-tools@1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "ackredit": {"version": version("ackredit"), "origin": ackredit.__file__},
        "tool_sha256": _sha(Path(__file__).read_bytes()),
        "process_owner_sha256": _sha(
            Path(__file__).with_name("check_publication_tools.py").read_bytes()
        ),
        "executables": {
            name: {"path": str(path), "sha256": _sha(Path(path).read_bytes())}
            for name, path in (("jabref", launcher), ("pandoc", pandoc))
        },
        "distribution": {
            "path": str(distribution),
            "before": shipped_before,
            "after": shipped_after,
        },
        "versions": versions,
        "route": "JabRef no-GUI explicit BibTeX import/save, fresh-process native reopen/resave",
        "citation_keys": cite_keys(item["id"] for item in before["items"]),
        "input_sha256": _sha(original),
        "original_preserved": True,
        "export_preserved": True,
        "new_execution_credit": False,
        "processes": steps,
        "warnings": [
            line
            for step in steps
            for line in step["stderr"].splitlines()
            if "WARN:" in line or "ERROR:" in line
        ],
        "files": {
            path.name: {"sha256": _sha(path.read_bytes()), "bytes": path.stat().st_size}
            for path in sorted(destination.iterdir())
            if path.is_file()
        },
        "limits": [
            "Exactly the selected portable distribution and no-GUI CLI route",
            "Pandoc independently observes saved files; it is not the manager importer",
            "Original attribution, manager-library bytes and reader conversions are separate evidence",
            "No GUI, enrichment, synchronization, duplicate merging or other-manager qualification",
            "No journal styling, arbitrary-Unicode, platform or new-release qualification",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attribution", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--distribution", type=Path, required=True)
    args = parser.parse_args()
    result = check(
        args.attribution.resolve(),
        args.output.resolve(),
        distribution=args.distribution,
    )
    (args.output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "warnings": result["warnings"],
                "jabref": result["versions"]["jabref"].strip(),
            }
        )
    )


if __name__ == "__main__":
    main()
