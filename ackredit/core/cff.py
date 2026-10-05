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

from .._private.dates import calendar_date_parts
from .._private.smonitor.emitter import warn
from .._private.smonitor.warnings import CitationFileWarning

# Normalize the selected work into the fields the existing report formats read.
# CFF page counts and page bounds have different meanings; see below.
_SCALARS = (
    "title",
    "version",
    "url",
    "message",
    "date-released",
    "date-published",
    "year",
    "month",
    "journal",
    "volume",
    "isbn",
    "issn",
    "edition",
    "abstract",
)
_ALIASES = {
    "issue": "number",
    "collection-title": "booktitle",
    "pages": "page-count",
}
_WORK_TYPES = {
    "article": "article",
    "software": "software",
    "software-code": "software",
    "software-container": "software",
    "software-executable": "software",
    "software-virtual-machine": "software",
    "dataset": "dataset",
    "data": "dataset",
    "database": "dataset",
    "website": "web",
}
_NAME_FIELDS = (
    "name",
    "family-names",
    "given-names",
    "name-particle",
    "name-suffix",
    "orcid",
)


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


def _source_names(block: list, text: List[str]) -> dict:
    """Detach declared name identity without changing legacy display strings."""
    return {
        "text": list(text),
        "names": [
            {
                field: str(entry[field]).strip()
                for field in _NAME_FIELDS
                if entry.get(field) is not None
            }
            for entry in block
            if _author(entry)
        ],
    }


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
    for field, normalized in _ALIASES.items():
        if (value := document.get(field)) is not None:
            data[normalized] = str(value).strip()
    if work_type := document.get("type"):
        data["type"] = _WORK_TYPES.get(work_type, "other")
        if work_type != data["type"]:
            data["_cff_type"] = work_type
    if authors := _authors(document.get("authors")):
        data["authors"] = authors
        data["_cff_authors"] = _source_names(document["authors"], authors)
    if editors := _authors(document.get("editors")):
        data["editors"] = editors
        data["_cff_editors"] = _source_names(document["editors"], editors)
    if publisher := _author(document.get("publisher")):
        data["publisher"] = publisher
    if doi := _doi(document):
        data["doi"] = doi
    # A count of fifteen pages does not mean the work begins on page fifteen.
    if document.get("start") is not None:
        data["pages"] = str(document["start"]).strip()
        if document.get("end") is not None:
            data["pages"] += "--" + str(document["end"]).strip()
    elif document.get("end") is not None:
        # A lone end page does not supply a range or a beginning page.
        data["end-page"] = str(document["end"]).strip()
    if "year" not in data:
        for field in ("date-published", "date-released"):
            if value := data.get(field):
                if parts := calendar_date_parts(value):
                    data["year"] = str(parts[0])
                # A stated publication date takes precedence even when it is
                # literal text. Do not borrow a year from another date field.
                break
    return data


def parse_cff(content: str) -> Dict[str, Any]:
    """Return the citation a CITATION.cff asks for.

    A typed `preferred-citation` is a separate work. Missing fields stay missing:
    the software's DOI, version or authors do not belong to its preferred paper.
    Historically accepted untyped partial blocks retain their root fallback.
    """
    document = yaml.safe_load(content)
    if not isinstance(document, dict) or not document:
        return {}

    data = _citation_fields(document)
    data.setdefault("type", "software")

    preferred = document.get("preferred-citation")
    if isinstance(preferred, dict):
        fields = _citation_fields(preferred)
        if preferred.get("type"):
            return {**fields, "_cff_source": "preferred-citation"}
        # Compatibility for incomplete historical files, not a typed work's
        # bibliography. Authors, when supplied, still replace the root list.
        data = {**data, **fields}

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
