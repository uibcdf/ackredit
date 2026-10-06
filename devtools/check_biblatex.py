"""Receive detached BibTeX with optional Biber and BibLaTeX standard styles.

Run outside the checkout with the intended normally installed Ackredit. Required
system tools are biber, kpsewhich, pdflatex and pdftotext; TeX must find biblatex.
TEXINPUTS may select an isolated TeX tree. No tool is installed or downloaded by
this probe. A new destination retains reader XML, backend BBL, compiled PDF,
extracted presentation, process output, loaded TeX resources and their hashes.
Original attribution and exported fields are never replaced by engine output.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from check_publication_tools import _run, _sha

import ackredit
from ackredit.formats.bibtex import cite_keys

STYLES = ("authoryear", "numeric")


def check(attribution_path: Path, destination: Path, *, style="authoryear") -> dict:
    """Run the selected real receiving route, preserving failures and warnings.

    Standard authoryear/numeric styles are accepted; neither is a journal style.
    Each resolved executable is also the command actually executed. Missing
    tools/resources fail, subprocess failures retain evidence and propagate,
    and an existing destination is refused. No backend or engine fallback occurs.
    """
    if style not in STYLES:
        raise ValueError(f"Unsupported publication probe style: {style}")
    executables = {}
    for name in ("biber", "kpsewhich", "pdflatex", "pdftotext"):
        if (path := shutil.which(name)) is None:
            raise FileNotFoundError(f"Required BibLaTeX probe tool unavailable: {name}")
        executables[name] = path

    original = attribution_path.read_bytes()
    attribution = ackredit.Attribution.from_json(original.decode("utf-8"))
    before = attribution.to_dict()
    used_before = ackredit.get_used_items()
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "attribution.json").write_bytes(original)
    exported = attribution.report("bibtex").encode("utf-8")
    (destination / "references.bib").write_bytes(exported)
    steps: list[dict] = []
    versions = {
        name: _run([executables[name], "--version"], destination, steps)
        for name in ("biber", "pdflatex")
    }
    _run([executables["pdftotext"], "-v"], destination, steps)
    resources = {}
    for name in ("biblatex.sty", f"{style}.bbx", f"{style}.cbx"):
        found = _run([executables["kpsewhich"], name], destination, steps).strip()
        path = Path(found)
        if not found or not path.is_file():
            raise FileNotFoundError(f"Required BibLaTeX resource unavailable: {name}")
        resources[name] = {"path": str(path), "sha256": _sha(path.read_bytes())}
    package = Path(resources["biblatex.sty"]["path"]).read_text(encoding="utf-8")
    versions["biblatex"] = re.search(r"\\def\\abx@version\{([^}]+)\}", package)[1]

    # Tool-mode reading is observed separately from the manuscript's data model.
    _run(
        [
            executables["biber"],
            "--tool",
            "--output-format=biblatexml",
            "--output-file=reader.xml",
            "references.bib",
        ],
        destination,
        steps,
    )
    (destination / "manuscript.tex").write_text(
        "\\documentclass{article}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[utf8]{inputenc}\n"
        f"\\usepackage[backend=biber,style={style}]{{biblatex}}\n"
        "\\addbibresource{references.bib}\n"
        "\\begin{document}\n\\nocite{*}\n\\printbibliography\n\\end{document}\n",
        encoding="utf-8",
    )
    latex = [
        executables["pdflatex"],
        "-no-shell-escape",
        "-recorder",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "manuscript.tex",
    ]
    _run(latex, destination, steps)
    _run([executables["biber"], "manuscript"], destination, steps)
    _run(latex, destination, steps)
    _run(latex, destination, steps)
    _run(
        [executables["pdftotext"], "-layout", "manuscript.pdf", "rendered.txt"],
        destination,
        steps,
    )

    # Identify every external file actually consumed by the final TeX pass,
    # including format, style dependencies and fonts rather than only its name.
    loaded = {}
    for line in (destination / "manuscript.fls").read_text().splitlines():
        if not line.startswith("INPUT "):
            continue
        path = Path(line[6:])
        if not path.is_absolute():
            path = destination / path
        path = path.resolve()
        if path.is_file() and not path.is_relative_to(destination.resolve()):
            loaded[str(path)] = {
                "sha256": _sha(path.read_bytes()),
                "bytes": path.stat().st_size,
            }
    for resource in resources.values():
        if (
            resource["sha256"]
            != loaded[str(Path(resource["path"]).resolve())]["sha256"]
        ):
            raise RuntimeError("Resolved BibLaTeX resource differs from loaded file")
    if attribution.to_dict() != before or attribution_path.read_bytes() != original:
        raise RuntimeError("BibLaTeX probe changed original attribution")
    if (destination / "references.bib").read_bytes() != exported:
        raise RuntimeError("BibLaTeX probe changed exported bibliography")
    if ackredit.get_used_items() != used_before:
        raise RuntimeError("BibLaTeX probe recorded new execution credit")
    warnings = {
        filename: [
            line
            for line in (destination / filename)
            .read_bytes()
            .decode("utf-8", errors="backslashreplace")
            .splitlines()
            if "WARN -" in line or "Warning:" in line
        ]
        for filename in ("references.bib.blg", "manuscript.blg", "manuscript.log")
    }
    return {
        "schema": "ackredit.biblatex-tools@1",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "ackredit": {"version": version("ackredit"), "origin": ackredit.__file__},
        "tool_sha256": _sha(Path(__file__).read_bytes()),
        "process_owner_sha256": _sha(
            Path(__file__).with_name("check_publication_tools.py").read_bytes()
        ),
        "executables": {
            name: {"path": path, "sha256": _sha(Path(path).read_bytes())}
            for name, path in executables.items()
        },
        "versions": versions,
        "style": style,
        "resources": resources,
        "loaded_tex_files": loaded,
        "citation_keys": cite_keys(item["id"] for item in before["items"]),
        "input_sha256": _sha(original),
        "original_preserved": True,
        "export_preserved": True,
        "new_execution_credit": False,
        "processes": steps,
        "warnings": warnings,
        "files": {
            path.name: {"sha256": _sha(path.read_bytes()), "bytes": path.stat().st_size}
            for path in sorted(destination.iterdir())
            if path.is_file()
        },
        "limits": [
            "Only the explicitly selected BibLaTeX/Biber pair and standard style",
            "Biber tool-mode XML and manuscript BBL are separate receiving outputs",
            "Reader recoding and style presentation do not replace original metadata",
            "No manager GUI, journal style, arbitrary Unicode or release qualification",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attribution", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--style", choices=STYLES, default="authoryear")
    args = parser.parse_args()
    result = check(args.attribution.resolve(), args.output.resolve(), style=args.style)
    (args.output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "style": args.style,
                "warnings": result["warnings"],
            }
        )
    )


if __name__ == "__main__":
    main()
