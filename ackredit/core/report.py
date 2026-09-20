from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ..formats import bibtex, csl_json, jsonfmt, latex, markdown, provenance, text
from .collector import get_used_items
from .registry import Registry

logger = logging.getLogger(__name__)


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
        logger.error(f"Cannot compile PDF: {tex_file} not found.")
        return

    pdflatex = shutil.which("pdflatex")
    bibtex = shutil.which("bibtex")

    if not pdflatex:
        logger.warning("pdflatex not found in PATH. PDF compilation skipped.")
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

    except subprocess.CalledProcessError as e:
        logger.error(f"PDF compilation failed: {e.stderr.decode()}")
