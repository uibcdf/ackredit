"""What `register_item` may be told about a work.

A citation field is open on purpose: `CitationItem` names the ones Ackredit
renders and the BibTeX renderer passes through whatever else an item carries,
so `publisher`, `isbn` and `booktitle` are all admissible without being listed.

What is *not* admissible is a key Ackredit keeps for itself. `_source` tells the
LaTeX escaper that a field is already LaTeX, and a caller who sets it reaches
straight past the escaping closed in `uibcdf/ackredit#7` and `#9`:

    register_item(id="x", title=r"Cost in \\textbf{$}", _source="bibtex")
    # title = {Cost in \\textbf{$}}      raw LaTeX, unescaped

So the domain is every field name except the reserved ones.
"""

from __future__ import annotations

from argdigest import Domain

# The fields Ackredit itself renders, for the message a refusal prints. The
# domain admits more than these; it is the reserved names it excludes.
KNOWN = (
    "id",
    "type",
    "title",
    "authors",
    "year",
    "doi",
    "url",
    "note",
    "journal",
    "volume",
    "number",
    "pages",
    "version",
    "publisher",
    "isbn",
    "issn",
    "edition",
    "series",
    "editor",
    "booktitle",
    "school",
    "institution",
    "address",
    "abstract",
    "language",
    "chapter",
    "how_to_cite",
)


def is_citation_field(name: str) -> bool:
    """Any field name that is not Ackredit's own bookkeeping."""
    return isinstance(name, str) and bool(name) and not name.startswith("_")


domain = Domain(
    name="citation_field",
    contains=is_citation_field,
    members=lambda: KNOWN,
    description=(
        "a field of a citation; any name except the underscore-prefixed ones "
        "Ackredit keeps for itself"
    ),
)
