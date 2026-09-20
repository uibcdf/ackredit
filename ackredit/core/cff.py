from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List


def parse_cff(content: str) -> Dict[str, Any]:
    """
    Very lightweight and limited YAML parser for CITATION.cff files.
    Zero-dependency.
    """
    data: Dict[str, Any] = {}

    # Extract simple fields (title, doi, version, url)
    fields = ["title", "doi", "version", "url", "message", "date-released"]
    for field in fields:
        match = re.search(
            rf'^{field}:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE | re.IGNORECASE
        )
        if match:
            data[field] = match.group(1).strip()

    # Extract authors (simplified list parsing)
    authors: List[str] = []
    # Find the authors: block and capture until the next top-level block
    authors_block = re.search(
        r"^authors:\s*(.*?)(?=\n\w+:|\Z)", content, re.DOTALL | re.MULTILINE
    )
    if authors_block:
        # Match each author block starting with -
        author_entries = re.findall(
            r"-\s*(.*?)(?=\n\s*-|\Z)", authors_block.group(1), re.DOTALL
        )
        for entry in author_entries:
            family = re.search(
                r'family-names:\s*["\']?(.*?)["\']?\s*$', entry, re.MULTILINE
            )
            given = re.search(
                r'given-names:\s*["\']?(.*?)["\']?\s*$', entry, re.MULTILINE
            )
            if family or given:
                name = f"{family.group(1) if family else ''}, {given.group(1) if given else ''}".strip(
                    ", "
                )
                authors.append(name)

    if authors:
        data["authors"] = authors

    return data


def find_and_parse_cff(package_path: Path) -> Dict[str, Any] | None:
    """Look for CITATION.cff in the package directory or its parent."""
    search_paths = [package_path / "CITATION.cff", package_path.parent / "CITATION.cff"]
    for p in search_paths:
        if p.exists():
            try:
                return parse_cff(p.read_text())
            except Exception:
                continue
    return None
