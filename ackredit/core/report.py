from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from depdigest import get_info
from smonitor import signal

from .._private.smonitor.emitter import warn
from .._private.smonitor.exceptions import UnknownFormatError
from .._private.smonitor.warnings import PdfCompilationWarning, PdfToolWarning
from ..formats import bibtex, csl_json, jsonfmt, latex, markdown, provenance, text
from .collector import get_used_items
from .registry import Registry

logger = logging.getLogger(__name__)


# One table, so the renderer and the file extension cannot disagree about which
# formats exist. `csl` stays as an alias for `csl-json` because it was published;
# an alias resolves to its canonical name before anything uses it.
_RENDERERS = {
    "markdown": (markdown.render, "md"),
    "text": (text.render, "txt"),
    "bibtex": (bibtex.render, "bib"),
    "json": (jsonfmt.render, "json"),
    "csl-json": (csl_json.render, "csl.json"),
    "provenance": (provenance.render, "txt"),
    "latex": (latex.render, "tex"),
}

_ALIASES = {"csl": "csl-json"}


def available_formats() -> list[str]:
    """The formats :func:`report` and :func:`dump` accept, canonical names only."""
    return sorted(_RENDERERS)


def _resolve_format(name: str) -> str:
    """Return the canonical name, or refuse and say what exists.

    An unknown name used to fall through to plain text, so a typo in "bibtex"
    produced a citation list that looked like a report and was not the one asked
    for.
    """
    canonical = _ALIASES.get(name, name)
    if canonical not in _RENDERERS:
        raise UnknownFormatError(
            extra={"format": name, "available": ", ".join(available_formats())}
        )
    return canonical


def dependency_info(format: str = "table"):
    """Report which optional dependencies this environment provides.

    Ackredit's core needs none of them; each unlocks one optional feature.
    ``format`` is ``"table"`` for people, or ``"dict"`` or ``"json"`` for a
    machine, following the ``depdigest.get_info@1.0`` schema.
    """
    return get_info("ackredit", format=format)


@signal(
    tags=["ackredit", "report"],
    extra_factory=lambda args, kwargs: {"format": kwargs.get("format", "markdown")},
)
def report(format: str = "markdown", **kwargs: Any) -> str:
    canonical = _resolve_format(format)
    render, _ = _RENDERERS[canonical]
    used = get_used_items()
    items = Registry.items

    if canonical == "latex":
        return render(used, items, **kwargs)
    return render(used, items)


@signal(
    tags=["ackredit", "report"],
    extra_factory=lambda args, kwargs: {
        "path": str(args[0]) if args else str(kwargs.get("path"))
    },
)
def dump(
    path: str | Path, formats: list[str] | None = None, build_pdf: bool = False
) -> None:
    """
    Save citation reports in multiple formats to a file or directory.
    If path is a directory, it will save multiple files (e.g., report.md, report.bib).
    If formats is None, it defaults to ["markdown", "bibtex", "provenance", "latex"].
    If build_pdf is True, it attempts to compile the latex report into a PDF.
    """
    if formats is None:
        formats = ["markdown", "bibtex", "provenance", "latex"]

    path = Path(path)

    if path.is_dir() or not path.suffix:
        path.mkdir(parents=True, exist_ok=True)
        for fmt in formats:
            _, ext = _RENDERERS[_resolve_format(fmt)]
            filename = f"ackredit_report.{ext}"
            file_path = path / filename
            content = report(format=fmt)
            file_path.write_text(content)

        if build_pdf:
            compile_pdf(path)
    else:
        # If a single file path is provided, we just save the first format or markdown
        fmt = formats[0] if formats else "markdown"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report(format=fmt))


def compile_pdf(directory: str | Path) -> None:
    """
    Attempt to compile ackredit_report.tex into a PDF using pdflatex.
    Requires pdflatex and bibtex to be installed on the system.
    """
    dir_path = Path(directory)
    tex_file = dir_path / "ackredit_report.tex"

    if not tex_file.exists():
        warn(
            PdfCompilationWarning(
                extra={
                    "directory": str(dir_path),
                    "tool": "pdflatex",
                    "status": f"no LaTeX source at {tex_file.name}",
                }
            )
        )
        return

    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")

    if not pdflatex:
        warn(PdfToolWarning(extra={"tool": "pdflatex"}))
        return

    try:
        # Standard compilation sequence: pdflatex -> bibtex -> pdflatex -> pdflatex
        subprocess.run(
            [pdflatex, "-interaction=nonstopmode", tex_file.name],
            cwd=dir_path,
            check=True,
            capture_output=True,
        )

        if bibtex:
            subprocess.run(
                [bibtex, "ackredit_report"],
                cwd=dir_path,
                check=True,
                capture_output=True,
            )

            subprocess.run(
                [pdflatex, "-interaction=nonstopmode", tex_file.name],
                cwd=dir_path,
                check=True,
                capture_output=True,
            )

            subprocess.run(
                [pdflatex, "-interaction=nonstopmode", tex_file.name],
                cwd=dir_path,
                check=True,
                capture_output=True,
            )

        # Cleanup auxiliary files
        for ext in ["aux", "log", "out", "blg", "bbl"]:
            aux_file = dir_path / f"ackredit_report.{ext}"
            if aux_file.exists():
                aux_file.unlink()

        logger.info(f"PDF successfully compiled: {dir_path / 'ackredit_report.pdf'}")

    except subprocess.CalledProcessError as error:
        warn(
            PdfCompilationWarning(
                extra={
                    "directory": str(dir_path),
                    "tool": Path(error.cmd[0]).name if error.cmd else "pdflatex",
                    "status": error.returncode,
                }
            )
        )
