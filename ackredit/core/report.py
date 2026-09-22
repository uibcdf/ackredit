from __future__ import annotations

import inspect
import json
import logging
import re
import shutil
import subprocess
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping

from depdigest import get_info
from smonitor import signal

from .._private.argdigest import arg_digest
from .._private.smonitor.emitter import warn
from .._private.smonitor.exceptions import (
    FormatNameTakenError,
    InvalidFormatError,
    ManyFormatsOneFileError,
    UnknownFormatError,
)
from .._private.smonitor.warnings import (
    DependencySchemaWarning,
    FormatExtensionWarning,
    FormatPluginWarning,
    PdfCompilationWarning,
    PdfToolWarning,
)
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

# Entry-point group, mirroring `ackredit.citations`. An entry point loads a
# callable that registers, so one package can ship several formats.
_PLUGIN_GROUP = "ackredit.formats"

# Names keep one style, so `available_formats()` stays coherent and the case
# confusion refused in the unknown-format work cannot enter through a plugin:
# lookups match exactly, so "BibTeX" would be a second, silently different name.
_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

_PLUGINS_LOADED = False


def _read_only(items: dict) -> Mapping:
    """The registry as a renderer sees it: readable, and not writable.

    `used` was always a copy, built fresh by `get_used_items`. `items` was the
    registry itself, so a renderer could empty it — and since formats became
    extensible, that renderer may come from anywhere. Both levels are wrapped,
    because a proxy over the mapping alone still lets an item be rewritten
    through it.
    """
    return MappingProxyType(
        {item_id: MappingProxyType(item) for item_id, item in items.items()}
    )


def _options(render: Callable) -> list[str]:
    """The names a renderer takes beyond what every renderer takes."""
    return [
        name
        for name in list(inspect.signature(render).parameters)[2:]
        if not name.startswith("*")
    ]


@arg_digest()
def register_format(name: str, renderer: Callable, extension: str) -> None:
    """Add an output format, for this process.

    **What a renderer is handed.** ``renderer(used, items)``, returning the
    report as text.

    - ``used`` maps an item id to the names that credited it, in the order they
      appeared. It is a copy: writing to it changes nothing.
    - ``items`` is the registry, an item id to its fields. It is **read only**,
      at both levels, because a renderer may come from anywhere and the
      declarations belong to every later report as well.
    - An id in ``used`` need not be in ``items``. A host may credit an id it
      never declared, and every built-in renderer reports it with what is
      known — the id as its own title.

    A renderer may take further arguments, which reach it from
    ``report(format=..., **options)``. A format asked for an option it does not
    take refuses with ``ACKREDIT-E007`` and says what it accepts.

    *extension* is what :func:`dump` names the file, without a leading dot::

        def render(used, items):
            return ", ".join(sorted(used))

        ackredit.register_format("ids", render, "txt")
        ackredit.report(format="ids")

    A package ships one by declaring an entry point that calls this::

        [project.entry-points."ackredit.formats"]
        anything = "my_package.formats:register"

    **A name that exists is never replaced**, built-in or from another plugin.
    Letting a third party take over ``bibtex`` would make a request succeed and
    return a report that is not the one asked for, which is the defect
    ``ACKREDIT-E004`` exists to prevent.
    """
    reason = None
    if not isinstance(name, str) or not _NAME.match(name):
        reason = "a name must be lower case, and start with a letter or a digit"
    elif not callable(renderer):
        reason = "the renderer is not callable"
    elif not isinstance(extension, str) or not extension.strip(". "):
        reason = "a file extension is required, without a leading dot"

    if reason is not None:
        raise InvalidFormatError(extra={"format": name, "reason": reason})

    if name in _RENDERERS or name in _ALIASES:
        raise FormatNameTakenError(extra={"format": name})

    _RENDERERS[name] = (renderer, extension.strip(". "))


def _load_plugins_once() -> None:
    """Discover formats other packages provide, the first time it matters.

    Lazily, because requiring a call before ``report(format="mine")`` works
    would make an unknown-format refusal the normal first experience of the
    feature. Once, because it scans the installed distributions.

    The flag is set before the work, not after: a plugin's register function may
    itself ask what formats exist, and that would otherwise recurse. The import
    hook marks a package the same way and for the same reason.
    """
    global _PLUGINS_LOADED
    if _PLUGINS_LOADED:
        return
    _PLUGINS_LOADED = True

    from importlib import metadata

    for entry_point in metadata.entry_points(group=_PLUGIN_GROUP):
        try:
            entry_point.load()()
        except Exception as error:
            # Never propagate: a broken third-party format must not take the
            # host down, and the built-in formats are unaffected.
            warn(
                FormatPluginWarning(
                    extra={
                        "plugin": getattr(entry_point, "name", str(entry_point)),
                        "error_type": type(error).__name__,
                        "error": str(error),
                    }
                )
            )


def available_formats() -> list[str]:
    """The formats :func:`report` and :func:`dump` accept, canonical names only."""
    _load_plugins_once()
    return sorted(_RENDERERS)


def _format_for_name(path: Path) -> str | None:
    """The format a file name asks for, or ``None`` if it asks for nothing.

    The longest extension wins, so ``refs.csl.json`` is CSL-JSON rather than
    JSON, and the table is read in its own order, so ``.txt`` is plain text
    rather than the provenance graph that shares the extension.
    """
    _load_plugins_once()
    name = path.name.lower()
    best: tuple[int, str] | None = None
    for fmt, (_, extension) in _RENDERERS.items():
        suffix = "." + extension.lower()
        if name.endswith(suffix) and (best is None or len(suffix) > best[0]):
            best = (len(suffix), fmt)
    return best[1] if best else None


def _resolve_format(name: str) -> str:
    """Return the canonical name, or refuse and say what exists.

    An unknown name used to fall through to plain text, so a typo in "bibtex"
    produced a citation list that looked like a report and was not the one asked
    for.
    """
    _load_plugins_once()
    canonical = _ALIASES.get(name, name)
    if canonical not in _RENDERERS:
        raise UnknownFormatError(
            extra={"format": name, "available": ", ".join(available_formats())}
        )
    return canonical


# The DepDigest payload Ackredit relays as its own contract. The table shape
# carries no version because it is a rendering; only the machine shape is
# promised, and only it can be checked.
_DEPENDENCY_SCHEMA = "1.0"


def _check_dependency_schema(info: Any) -> None:
    """Report a relayed payload that is not the one documented."""
    if isinstance(info, str):
        try:
            info = json.loads(info)
        except ValueError:
            return
    if not isinstance(info, dict):
        return

    found = info.get("schema", {}).get("version")
    if found is not None and found != _DEPENDENCY_SCHEMA:
        warn(
            DependencySchemaWarning(
                extra={"found": found, "promised": _DEPENDENCY_SCHEMA}
            )
        )


@arg_digest()
def dependency_info(format: str = "table"):
    """Report which optional dependencies this environment provides.

    Ackredit's core needs none of them; each unlocks one optional feature.

    **What is promised.** ``format="dict"`` and ``format="json"`` return the
    ``depdigest.get_info@1.0`` payload, which states its own schema under a
    ``"schema"`` key and lists each library under ``"dependencies"``. Ackredit
    relays that shape rather than defining one, and verifies the version it
    relays: a payload declaring another raises ``ACKREDIT-W017`` rather than
    being handed over in silence.

    ``format="table"`` is a rendering for a person to read, with capitalised
    keys and prose in the values. It is not part of the promise and may change.
    """
    info = get_info("ackredit", format=format)
    _check_dependency_schema(info)
    return info


@arg_digest()
@signal(
    tags=["ackredit", "report"],
    extra_factory=lambda args, kwargs: {"format": kwargs.get("format", "markdown")},
)
def report(format: str = "markdown", **kwargs: Any) -> str:
    canonical = _resolve_format(format)
    render, _ = _RENDERERS[canonical]
    used = get_used_items()
    items = _read_only(Registry.items)

    # Which keywords a format accepts is declared as a domain, in
    # `ackredit/_private/argdigest/domain/format_options.py`, and refused by
    # ArgDigest before this runs. It was checked here first, by binding the
    # renderer's signature; adopting ArgDigest means not doing by hand what the
    # suite does, so that check is gone and the domain reads `_options` below —
    # the same source, so the two cannot disagree.
    if not kwargs:
        return render(used, items)
    return render(used, items, **kwargs)


@arg_digest()
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
    Save citation reports to a file or a directory.

    A directory takes several formats and writes one file each, defaulting to
    ``["markdown", "bibtex", "provenance", "latex"]``.

    A file takes one. Asked for several it refuses, because writing the first
    and discarding the rest is how a report silently goes missing. Asked for
    none it reads the extension, so ``dump("refs.bib")`` is BibTeX; it used to
    write Markdown under that name.

    If build_pdf is True, it attempts to compile the latex report into a PDF.
    """
    path = Path(path)

    if path.is_dir() or not path.suffix:
        formats = formats or ["markdown", "bibtex", "provenance", "latex"]
        path.mkdir(parents=True, exist_ok=True)

        # Two formats can share an extension: `provenance` and `text` are both
        # `.txt`. Asking for both used to write one file twice, so the report
        # the caller saw was whichever came last. Only a clash is renamed, so
        # `ackredit_report.bib` keeps the name `\bibliography{ackredit_report}`
        # in the LaTeX report points at.
        extensions = [_RENDERERS[_resolve_format(fmt)][1] for fmt in formats]

        for fmt, ext in zip(formats, extensions):
            stem = "ackredit_report"
            if extensions.count(ext) > 1:
                stem = f"{stem}_{_resolve_format(fmt)}"
            file_path = path / f"{stem}.{ext}"
            content = report(format=fmt)
            file_path.write_text(content)

        if build_pdf:
            compile_pdf(path)
    else:
        implied = _format_for_name(path)

        if not formats:
            fmt = implied or "markdown"
        elif len(formats) > 1:
            raise ManyFormatsOneFileError(
                extra={
                    "count": len(formats),
                    "formats": ", ".join(formats),
                    "path": str(path),
                }
            )
        else:
            fmt = formats[0]

        written = _resolve_format(fmt)
        if implied is not None and implied != written:
            # The caller was explicit, so this is written as asked. The name is
            # what the next reader trusts, and it now says something else.
            warn(
                FormatExtensionWarning(
                    extra={"path": str(path), "format": written, "implied": implied}
                )
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(report(format=fmt))


@arg_digest()
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
