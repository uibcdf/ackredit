from __future__ import annotations

import hashlib
import re
from typing import Iterable

from ._latex import escape, is_latex_source
from ._names import cff_names

# The fields whose BibTeX name differs from Ackredit's, in the order a reader
# expects them. Everything else the item carries follows, alphabetically.
_ORDERED = [
    ("author", "authors"),
    ("year", "year"),
    ("doi", "doi"),
    ("url", "url"),
    ("note", "note"),
    ("journal", "journal"),
]

# Ackredit's own keys, which are not bibliographic fields.
_NOT_A_FIELD = {
    "id",
    "type",
    "title",
    "authors",
    "editor",
    "editors",
    "how_to_cite",
} | {fc_key for _, fc_key in _ORDERED}


def _bibtex_name(author: object, *, latex_source: bool = False) -> str:
    """Render an explicit CSL name or an existing BibTeX name string.

    Literal objects declare an indivisible author. Their protection braces are
    syntax, added after escaping the text. Structured objects use BibTeX's
    ``von Last, Jr, First`` order; dropping particles follow the given name.
    BibTeX cannot retain CSL's separate particle display/sorting controls.

    BibTeX's three-part form is "von Last, Jr, First", so two commas are valid and
    only a third is an error that aborts the run. Double braces make the whole
    string one literal name, the standard idiom for corporate and irregular names,
    at the cost of its sorting key and initials — so it is used only when BibTeX
    genuinely cannot read the name.
    """
    if isinstance(author, dict):
        if "literal" in author:
            text = escape(str(author["literal"]), latex_source=latex_source)
            return f"{{{text}}}"

        def part(*keys: str) -> str:
            text = " ".join(str(author[key]).strip() for key in keys if author.get(key))
            text = escape(text, latex_source=latex_source)
            # Commas and the author-list separator inside a declared name part
            # are content rather than BibTeX delimiters.
            if "," in text or " and " in text.lower():
                return f"{{{text}}}"
            return text

        family = part("non-dropping-particle", "family")
        given = part("given", "dropping-particle")
        suffix = part("suffix")
        if suffix:
            return f"{family}, {suffix}, {given}"
        return f"{family}, {given}" if family and given else family or given

    name = escape(str(author), latex_source=latex_source)
    return f"{{{name}}}" if name.count(",") > 2 else name


# What a citation key may carry and still be read the same by BibTeX, by
# `\citep` and by hyperref's anchors. Everything reference managers generate
# fits: `Smith_2020`, `smith:2020a`, `10.1021/ct500000x`.
_KEY = re.compile(r"^[A-Za-z0-9_:./+-]+$")
_NOT_KEY = re.compile(r"[^A-Za-z0-9_:./+-]+")

# A typed CFF preferred book/collection declares a work whose editors and
# publisher plain.bst can render. Other CFF kinds retain the existing fallback;
# an imported BibTeX entry always keeps its original type.
_FROM_CFF = {"book": "book", "edited-work": "book"}


def _digest(item_id: str) -> str:
    return hashlib.sha256(item_id.encode("utf-8")).hexdigest()[:8]


def _made_valid(item_id: str) -> str:
    """A readable fallback candidate for *item_id*.

    The readable part alone is lossy — "a b" and "a,b" both read "a-b" — so it
    carries a digest of the id itself, as the DOI cache names do (#38).
    The report-wide allocator resolves remaining collisions, including hashes.
    """
    readable = _NOT_KEY.sub("-", item_id).strip("-")
    return f"{readable}-{_digest(item_id)}" if readable else _digest(item_id)


def cite_keys(item_ids: Iterable[str]) -> dict[str, str]:
    """The citation key of each id, distinct for distinct ids.

    An id that is already a valid key is its own key, so an entry read from a
    `.bib` file is written back under the name the manuscript cites. This used
    to rewrite every `:`, `_` and space to `-`, which renamed what was loaded
    and mapped `Smith_2020` and `Smith:2020` to one key, losing a citation.

    BibTeX compares keys ignoring case, so ids that differ only in case need
    fallback keys. Reserve original nonclashing valid keys first, then allocate
    unique fallback keys in sorted id order. Even generated-key/hash collisions
    cannot rename those originals or collapse two works. One table for a whole
    report, so `bibtex` entries and `latex` `\\citep` calls cannot disagree.
    """
    ids = list(dict.fromkeys(item_ids))
    folded: dict[str, list[str]] = {}
    for item_id in ids:
        if _KEY.fullmatch(item_id):
            folded.setdefault(item_id.casefold(), []).append(item_id)
    keys = {group[0]: group[0] for group in folded.values() if len(group) == 1}
    reserved = {key.casefold() for key in keys.values()}
    for item_id in sorted(item_id for item_id in ids if item_id not in keys):
        base = _made_valid(item_id)
        candidate = base
        suffix = 2
        while candidate.casefold() in reserved:
            candidate = f"{base}-{suffix}"
            suffix += 1
        keys[item_id] = candidate
        reserved.add(candidate.casefold())

    return {item_id: keys[item_id] for item_id in ids}


def render(used: dict[str, list[str]], items: dict[str, dict]) -> str:
    """
    Render used items in BibTeX format.
    Supports basic mapping from Ackredit types to BibTeX entry types.
    """
    if not used:
        return ""

    entries: list[str] = []
    keys = cite_keys(used)

    # Ackredit's types mapped onto BibTeX's own vocabulary. `@software` and
    # `@dataset` come from biblatex and are not defined by a BibTeX style, so a
    # BibTeX run warns and falls back to a default layout, losing the distinction
    # entirely. Emitting `@misc` and carrying the kind in `howpublished` keeps it,
    # renders it to the reader, and compiles without warnings under any style.
    type_map = {
        "article": "article",
        "software": "misc",
        "repo": "misc",
        "web": "misc",
        "dataset": "misc",
        "other": "misc",
    }

    # What `howpublished` should say for a type that BibTeX has no entry for.
    kind_map = {
        "software": "Software",
        "dataset": "Dataset",
        "repo": "Software repository",
        "web": "Web resource",
    }

    for item_id in used:
        item = items.get(item_id)
        if not item:
            # If item not in registry, create a minimal misc entry
            item = {"title": item_id, "id": item_id}

        key = keys[item_id]

        latex_source = is_latex_source(item)

        fc_type = item.get("type", "other")
        # An item read from a .bib file is written back as the entry it was.
        bib_type = item.get("_bibtex_type") or _FROM_CFF.get(
            item.get("_cff_type", ""), type_map.get(fc_type, "misc")
        )

        fields: list[str] = []

        # Helper to add fields
        def add_field(bib_key: str, fc_key: str):
            val = item.get(fc_key)
            if not val:
                return

            # A TeX engine reads these values; a bare '&' in a journal name
            # silently mangles the compiled bibliography. An item parsed from a
            # .bib file is already LaTeX and is passed through untouched.
            #
            # Brace protection is applied after escaping, never before: its
            # braces are BibTeX syntax rather than content, and escaping them
            # would turn the protection into a literal pair of characters.
            if isinstance(val, list):
                if fc_key in {"authors", "editor", "editors"}:
                    hint = "_cff_authors" if fc_key == "authors" else "_cff_editors"
                    names = cff_names(val, item.get(hint)) or val
                    parts = [
                        _bibtex_name(part, latex_source=latex_source) for part in names
                    ]
                else:
                    parts = [
                        escape(str(part), latex_source=latex_source) for part in val
                    ]
                escaped = " and ".join(parts)
            else:
                escaped = escape(str(val), latex_source=latex_source)

            fields.append(f"  {bib_key} = {{{escaped}}}")

        add_field("title", "title")

        # Name the kind BibTeX cannot express in its entry type — but not when
        # the entry already says what it is, which it does for anything read
        # from a .bib file.
        if not item.get("_bibtex_type") and (kind := kind_map.get(fc_type)):
            fields.append(f"  howpublished = {{{kind}}}")

        for bib_key, fc_key in _ORDERED:
            add_field(bib_key, fc_key)

        # CSL/CFF use plural "editors"; BibTeX styles read singular "editor".
        # Keep the same explicit plural-first choice as the CSL renderer, while
        # original string-valued BibTeX editor syntax passes through unchanged.
        add_field("editor", "editors" if item.get("editors") else "editor")

        # Whatever else the item carries. A fixed list dropped the publisher of
        # a book, the pages of a conference paper and the school of a thesis,
        # although the parser had stored all three. A .bst style ignores a field
        # it does not know, so carrying one costs nothing and dropping one costs
        # the bibliography.
        for fc_key in sorted(item):
            if fc_key in _NOT_A_FIELD or fc_key.startswith("_"):
                continue
            add_field(fc_key, fc_key)

        # With no author or editor, a natbib style labels the entry with its
        # `key` field, and without one with the first three characters of the
        # citation key — so every discovered package printed as "(dis, 2020)".
        # BibTeX defines `key` for exactly this; the label is the work's name.
        # An entry read from a .bib file is left as its author wrote it.
        # Classic misc styles do not use editor for sorting/labels. A retained
        # editor is still metadata, but cannot supply that entry's label.
        named = item.get("authors") or (
            bib_type != "misc" and (item.get("editor") or item.get("editors"))
        )
        if not latex_source and not named and not item.get("key"):
            label = escape(str(item.get("title") or item_id))
            fields.append(f"  key = {{{label}}}")

        entry = f"@{bib_type}{{{key},\n" + ",\n".join(fields) + "\n}"
        entries.append(entry)

    return "\n\n".join(entries)
