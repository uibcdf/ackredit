from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from depdigest import get_info
from smonitor import signal

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import PdfCompilationWarning, PdfToolWarning
from ..formats import bibtex, csl_json, jsonfmt, latex, markdown, provenance, text
from .collector import get_used_items
from .registry import Registry

logger = logging.getLogger(__name__)


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
    used = get_used_items()
    items = Registry.items

    if format == "markdown":
        return markdown.render(used, items)
    if format == "text":
        return text.render(used, items)
    if format == "bibtex":
        return bibtex.render(used, items)
    if format == "json":
        return jsonfmt.render(used, items)
    if format == "csl-json" or format == "csl":
        return csl_json.render(used, items)
    if format == "provenance":
        return provenance.render(used, items)
    if format == "latex":
        return latex.render(used, items, **kwargs)
    # default fallback
    return text.render(used, items)


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

    # Extensions map
    ext_map = {
        "markdown": "md",
        "bibtex": "bib",
        "json": "json",
        "csl-json": "csl.json",
        "csl": "csl.json",
        "provenance": "txt",
        "latex": "tex",
        "text": "txt",
    }

    if path.is_dir() or not path.suffix:
        path.mkdir(parents=True, exist_ok=True)
        for fmt in formats:
            ext = ext_map.get(fmt, "txt")
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
