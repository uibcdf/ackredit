from __future__ import annotations

import argparse

from .core.collector import Collector
from .core.report import dump, report


def main():
    parser = argparse.ArgumentParser(
        description="Ackredit CLI - Citation management for scientific workflows."
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Command: report
    report_parser = subparsers.add_parser(
        "report", help="Generate report from a session file."
    )
    report_parser.add_argument(
        "session_file", help="Path to a saved session JSON file."
    )
    report_parser.add_argument(
        "--format",
        "-f",
        default="text",
        choices=["text", "markdown", "bibtex", "csl-json", "provenance", "latex"],
        help="Output format (default: text)",
    )

    # Command: aggregate
    agg_parser = subparsers.add_parser(
        "aggregate", help="Merge multiple session files."
    )
    agg_parser.add_argument("files", nargs="+", help="Session files to merge.")
    agg_parser.add_argument(
        "--output", "-o", required=True, help="Output path for the merged session."
    )

    # Command: dump
    dump_parser = subparsers.add_parser(
        "dump", help="Generate all report formats from a session."
    )
    dump_parser.add_argument("session_file", help="Path to a saved session JSON file.")
    dump_parser.add_argument("output_dir", help="Directory to save the reports.")
    dump_parser.add_argument(
        "--pdf", action="store_true", help="Attempt to compile PDF report."
    )

    args = parser.parse_args()

    if args.command == "report":
        Collector.enable_persistence(args.session_file)
        print(report(format=args.format))

    elif args.command == "aggregate":
        Collector.aggregate(args.files)
        Collector.enable_persistence(args.output)
        Collector._save_state()
        print(f"Successfully merged {len(args.files)} sessions into {args.output}")

    elif args.command == "dump":
        Collector.enable_persistence(args.session_file)
        dump(args.output_dir, build_pdf=args.pdf)
        print(f"All reports generated in {args.output_dir}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
