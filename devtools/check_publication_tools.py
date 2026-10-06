"""Probe a saved bibliography with optional BibTeX/plain and Pandoc/citeproc.

Run outside the producing checkout with a normally installed Ackredit. This is
an offline receiving probe, not a reference-manager import or a release gate.
An existing destination is refused so inputs and engine results cannot be
silently replaced. Engines/style files and all outputs are identified by SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import ackredit
from ackredit.formats.bibtex import cite_keys


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _run(command: list[str], directory: Path, steps: list[dict]) -> str:
    """Retain exact process bytes; render undecodable bytes as explicit escapes.

    TeX output can mix encodings. Capture bytes before decoding so a diagnostic
    cannot prevent preservation of either stream or the real process status.
    """
    process = subprocess.run(
        command,
        cwd=directory,
        capture_output=True,
        timeout=60,
        env={**os.environ, "TEXMFVAR": str(directory / "texmf-var")},
    )
    name = f"process-{len(steps) + 1}"
    (directory / f"{name}.stdout.txt").write_bytes(process.stdout)
    (directory / f"{name}.stderr.txt").write_bytes(process.stderr)
    steps.append(
        {
            "command": command,
            "exit_code": process.returncode,
            "stdout_sha256": _sha(process.stdout),
            "stderr_sha256": _sha(process.stderr),
            "stderr": process.stderr.decode("utf-8", errors="backslashreplace"),
            "text_rendering": "UTF-8 with explicit backslash escapes for undecodable bytes",
        }
    )
    (directory / "processes.json").write_text(json.dumps(steps, indent=2) + "\n")
    process.check_returncode()
    return process.stdout.decode("utf-8", errors="backslashreplace")


def check(attribution_path: Path, destination: Path) -> dict:
    """Export detached attribution and retain actual engine receiving results.

    Required executables are optional system tools, not Ackredit dependencies.
    Process failures propagate and retain their stdout/stderr at the destination.
    No engine output is used to replace original attribution or exported fields.
    """
    executables = {}
    for name in ("bibtex", "kpsewhich", "pdflatex", "pandoc"):
        if (executable := shutil.which(name)) is None:
            raise FileNotFoundError(
                f"Required publication probe tool unavailable: {name}"
            )
        executables[name] = executable

    original = attribution_path.read_bytes()
    attribution = ackredit.Attribution.from_json(original.decode("utf-8"))
    before = attribution.to_dict()
    used_before = ackredit.get_used_items()
    modules_before = set(sys.modules)
    destination.mkdir(parents=True, exist_ok=False)
    steps: list[dict] = []
    (destination / "attribution.json").write_bytes(original)
    for fmt, filename in (
        ("bibtex", "references.bib"),
        ("csl-json", "references.csl.json"),
    ):
        (destination / filename).write_text(attribution.report(fmt), encoding="utf-8")

    versions = {}
    for name in ("bibtex", "pdflatex", "pandoc"):
        versions[name] = _run([executables[name], "--version"], destination, steps)
    style_path = Path(
        _run([executables["kpsewhich"], "plain.bst"], destination, steps).strip()
    )
    (destination / "plain.bst").write_bytes(style_path.read_bytes())
    csl = _run(
        [executables["pandoc"], "--print-default-data-file=default.csl"],
        destination,
        steps,
    )
    (destination / "style.csl").write_text(csl, encoding="utf-8")

    # Probe the engine readers separately from style-driven presentation.
    for fmt, filename, output in (
        ("csljson", "references.csl.json", "csl-read.json"),
        ("bibtex", "references.bib", "bibtex-read.json"),
    ):
        _run(
            [executables["pandoc"], "-f", fmt, "-t", "csljson", filename, "-o", output],
            destination,
            steps,
        )

    (destination / "references.aux").write_text(
        "\\citation{*}\n\\bibdata{references}\n\\bibstyle{plain}\n", encoding="utf-8"
    )
    _run([executables["bibtex"], "references"], destination, steps)
    (destination / "manuscript.tex").write_text(
        "\\documentclass{article}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\begin{document}\n"
        "\\input{references.bbl}\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    _run(
        [
            executables["pdflatex"],
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "manuscript.tex",
        ],
        destination,
        steps,
    )
    (destination / "manuscript.md").write_text(
        "---\nnocite: '@*'\n---\n\nDetached bibliography.\n", encoding="utf-8"
    )
    _run(
        [
            executables["pandoc"],
            "--citeproc",
            "--csl=style.csl",
            "--bibliography=references.csl.json",
            "-f",
            "markdown",
            "-t",
            "html",
            "manuscript.md",
            "-o",
            "bibliography.html",
        ],
        destination,
        steps,
    )

    if attribution.to_dict() != before or attribution_path.read_bytes() != original:
        raise RuntimeError("Publication probe changed original attribution")
    if ackredit.get_used_items() != used_before:
        raise RuntimeError("Publication probe recorded new execution credit")
    files = {
        path.name: {"sha256": _sha(path.read_bytes()), "bytes": path.stat().st_size}
        for path in sorted(destination.iterdir())
        if path.is_file()
    }
    return {
        "schema": "ackredit.publication-tools@1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "ackredit": {"version": version("ackredit"), "origin": ackredit.__file__},
        "tool_sha256": _sha(Path(__file__).read_bytes()),
        "executables": {
            name: {"path": path, "sha256": _sha(Path(path).read_bytes())}
            for name, path in executables.items()
        },
        "versions": versions,
        "styles": {
            "bibtex": {"name": "plain.bst", "sha256": files["plain.bst"]["sha256"]},
            "csl": {
                "name": "Pandoc default.csl",
                "sha256": files["style.csl"]["sha256"],
            },
        },
        "citation_keys": cite_keys(item["id"] for item in before["items"]),
        "input_sha256": _sha(original),
        "original_preserved": True,
        "new_execution_credit": False,
        "modules_added": sorted(set(sys.modules) - modules_before),
        "processes": steps,
        "bibtex_warnings": [
            line
            for line in (destination / "references.blg").read_text().splitlines()
            if line.startswith("Warning--")
        ],
        "files": files,
        "limits": [
            "No reference-manager GUI import, BibLaTeX/Biber or journal-style qualification",
            "Metadata preservation and selected-style output are separate observations",
            "No duplicate merging or new public-release qualification",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attribution", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check(args.attribution.resolve(), args.output.resolve())
    (args.output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {"output": str(args.output), "bibtex_warnings": result["bibtex_warnings"]}
        )
    )


if __name__ == "__main__":
    main()
