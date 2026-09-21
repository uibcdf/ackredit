"""Reading CITATION.cff, the file a project writes to say how it wants to be cited.

This used to be regular expressions over lines, which cannot know whether an
`authors:` block belongs to the root document or to `preferred-citation`. That is
not a limitation that tighter patterns fix: it produced a confident wrong answer
on three documented constructs, dropping entity authors, merging two unrelated
author lists, and missing a DOI written where the specification puts it.

It is a structured document, so it is read as one.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import CitationFileWarning

# Fields Ackredit reads. A CITATION.cff carries more, and a `preferred-citation`
# carries a different set again; these are the ones a citation item needs.
_SCALARS = ("title", "version", "url", "message", "date-released")


def _author(entry: Any) -> str | None:
    """Render one CFF author, person or entity.

    An author may be a person, with `family-names` and `given-names`, or an
    organisation, with a single `name`. Both are valid, and the second used to be
    discarded silently, which under-credits exactly the institutions least able
    to notice.
    """
    if not isinstance(entry, dict):
        return None

    if name := entry.get("name"):
        return str(name).strip()

    family = str(entry.get("family-names", "")).strip()
    given = str(entry.get("given-names", "")).strip()
    if family and given:
        return f"{family}, {given}"
    return family or given or None


def _authors(block: Any) -> List[str]:
    if not isinstance(block, list):
        return []
    return [name for entry in block if (name := _author(entry))]


def _doi(document: Dict[str, Any]) -> str | None:
    """Find the DOI wherever the specification allows it to be written.

    A top-level `doi` is the short form; `identifiers` is the canonical one, and
    is what a Zenodo deposition writes.
    """
    if doi := document.get("doi"):
        return str(doi).strip()

    identifiers = document.get("identifiers")
    if isinstance(identifiers, list):
        for identifier in identifiers:
            if isinstance(identifier, dict) and identifier.get("type") == "doi":
                if value := identifier.get("value"):
                    return str(value).strip()
    return None


def _citation_fields(document: Dict[str, Any]) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for field in _SCALARS:
        if (value := document.get(field)) is not None:
            data[field] = str(value).strip()
    if authors := _authors(document.get("authors")):
        data["authors"] = authors
    if doi := _doi(document):
        data["doi"] = doi
    return data


def parse_cff(content: str) -> Dict[str, Any]:
    """Return the citation a CITATION.cff asks for.

    When the file carries a `preferred-citation`, that block *is* the citation:
    the specification exists so a project can say "cite this paper rather than
    this software". Its fields are used, falling back to the root document for
    anything it does not state, rather than being merged with it — its authors
    are a different set of people.
    """
    document = yaml.safe_load(content)
    if not isinstance(document, dict):
        return {}

    data = _citation_fields(document)

    preferred = document.get("preferred-citation")
    if isinstance(preferred, dict):
        # The preferred citation replaces, it does not merge. Merging credited a
        # list of authors belonging to neither the software nor the paper.
        data = {**data, **_citation_fields(preferred)}
        if preferred_authors := _authors(preferred.get("authors")):
            data["authors"] = preferred_authors

    return data


def find_and_parse_cff(package_path: Path) -> Dict[str, Any] | None:
    """Look for CITATION.cff in the package directory or its parent."""
    search_paths = [package_path / "CITATION.cff", package_path.parent / "CITATION.cff"]
    for p in search_paths:
        if p.exists():
            try:
                return parse_cff(p.read_text(encoding="utf-8"))
            except Exception as error:
                warn(
                    CitationFileWarning(
                        extra={
                            "package": package_path.name,
                            "path": str(p),
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    )
                )
                continue
    return None
