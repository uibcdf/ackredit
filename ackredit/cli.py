"""The `ackredit` command, for session files a run left behind.

Every subcommand here works on a saved session, so the one rule it lives by is
that reading must not write. `report` used to open its input with
`enable_persistence`, which exists to append and therefore creates: a mistyped
name produced an empty journal, a report saying the session held nothing, and a
success exit code.

What a session file can say is bounded, and that is worth knowing before
reading a report from one. A journal records events — which id was credited and
by whom — not the metadata of the items, which lives in the registry of the
process that declared them. In a process that costs nothing, because the host
library registers its items at import; a command line opening a file on its own
has nothing to import, so it names the items it found and cannot describe them.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ._private.smonitor.exceptions import AckreditError
from .core import session
from .core.collector import (
    aggregate,
    close_persistence,
    enable_persistence,
    get_used_items,
)
from .core.report import available_formats, dump, report


def _fail(message: str) -> int:
    print(f"ackredit: {message}", file=sys.stderr)
    return 1


def _load(path_text: str) -> Path | None:
    """Validate a session file and fold it into this process's session.

    The read happens twice: once here to know whether the file can be read at
    all, and once through `aggregate`, which is the supported way to merge one.
    A session file is small and being able to report the failure is worth more
    than the second pass.
    """
    path = Path(path_text)
    if not path.exists():
        print(f"ackredit: no session file at '{path}'", file=sys.stderr)
        return None

    try:
        session.read(path)
    except Exception as error:
        print(
            f"ackredit: '{path}' could not be read: {type(error).__name__}: {error}",
            file=sys.stderr,
        )
        return None

    aggregate([path])
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ackredit",
        description="Ackredit CLI - Citation management for scientific workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # The formats are asked for rather than listed, so the command reaches every
    # one the library has, including a format a plugin registered. `choices` is
    # deliberately not used: it would refuse the `csl` alias, and an unknown name
    # already raises ACKREDIT-E004, which names what exists.
    formats = ", ".join(available_formats())

    report_parser = subparsers.add_parser(
        "report", help="Generate report from a session file."
    )
    report_parser.add_argument("session_file", help="Path to a saved session file.")
    report_parser.add_argument(
        "--format",
        "-f",
        default="text",
        help=f"Output format (default: text). One of: {formats}",
    )

    agg_parser = subparsers.add_parser(
        "aggregate", help="Merge multiple session files."
    )
    agg_parser.add_argument("files", nargs="+", help="Session files to merge.")
    agg_parser.add_argument(
        "--output", "-o", required=True, help="Output path for the merged session."
    )

    dump_parser = subparsers.add_parser(
        "dump", help="Generate all report formats from a session."
    )
    dump_parser.add_argument("session_file", help="Path to a saved session file.")
    dump_parser.add_argument("output_dir", help="Directory to save the reports.")
    dump_parser.add_argument(
        "--pdf", action="store_true", help="Attempt to compile PDF report."
    )

    return parser


def _report(args) -> int:
    if _load(args.session_file) is None:
        return 1
    try:
        print(report(format=args.format))
    except AckreditError:
        # The catalog already reported it, with the code and what to use
        # instead. Printing it again would be the hardcoded second message the
        # diagnostics policy exists to prevent.
        return 1
    return 0


def _dump(args) -> int:
    if _load(args.session_file) is None:
        return 1
    dump(args.output_dir, build_pdf=args.pdf)
    print(f"All reports generated in {args.output_dir}")
    return 0


def _aggregate(args) -> int:
    """Merge the readable inputs into the output, and say which were not.

    The output journal is opened before the merge, not after, so the merge is
    recorded in it — `uibcdf/ackredit#39`.
    """
    readable, skipped = [], []
    for path_text in args.files:
        path = Path(path_text)
        if not path.exists():
            skipped.append((path, "not found"))
            continue
        try:
            session.read(path)
        except Exception as error:
            skipped.append((path, f"{type(error).__name__}: {error}"))
            continue
        readable.append(path)

    for path, reason in skipped:
        print(f"ackredit: skipped '{path}': {reason}", file=sys.stderr)

    if not readable:
        return _fail("no session file could be read; nothing was written")

    enable_persistence(args.output)
    try:
        aggregate(readable)
        citations = len(get_used_items())
    finally:
        close_persistence()

    files = "file" if len(args.files) == 1 else "files"
    found = "citation" if citations == 1 else "citations"
    print(
        f"Merged {len(readable)} of {len(args.files)} session {files} into "
        f"{args.output} ({citations} {found})."
    )
    return 1 if skipped else 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    handlers = {"report": _report, "aggregate": _aggregate, "dump": _dump}
    handler = handlers.get(args.command)
    if handler is None:
        parser.print_help()
        return 0
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
