from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.request
from pathlib import Path
from typing import Any, Dict, Literal, TypedDict

from .._private.smonitor.emitter import warn
from .._private.smonitor.exceptions import (
    BibtexFileNotFoundError,
    ItemIdMissingError,
)
from .._private.smonitor.warnings import (
    BibtexFieldWarning,
    MetadataCacheWarning,
    MetadataFetchWarning,
    MetadataRecordWarning,
    PluginLoadWarning,
)


def _cache_name(doi: str) -> str:
    """A file name that belongs to exactly one DOI.

    Replacing "/" with "_" was lossy: a DOI suffix may contain either, so
    "10.1234/a/b" and "10.1234/a_b" shared one file and one work's metadata was
    served for the other. The digest is of the DOI itself, so distinct DOIs
    cannot collide, and the readable prefix keeps the directory inspectable.
    """
    digest = hashlib.sha256(doi.encode("utf-8")).hexdigest()[:16]
    readable = re.sub(r"[^A-Za-z0-9._-]+", "-", doi)
    # Collapse runs of dots: a name carrying ".." is confusing to read in a
    # cache directory even where it cannot traverse one.
    readable = re.sub(r"\.{2,}", ".", readable)[:60].strip("-.")
    return f"{readable}.{digest}" if readable else digest


def _first(values: Any) -> Any:
    """The first element of *values*, unescaped, or None if there is none.

    `data.get("title", [item_id])[0]` used the default only when the key was
    absent, and an empty list is not absent: a record carrying `"title": []`
    raised IndexError out of enrichment.
    """
    if not isinstance(values, (list, tuple)) or not values:
        return None
    first = values[0]
    return html.unescape(first) if isinstance(first, str) else first


def _record_authors(creators: Any) -> list[str]:
    """Names from a fetched record, dropping the ones that name nobody.

    DataCite's mapping yields `family=None` for a creator with neither a
    `familyName` nor a `name`, and formatting that produced an author called
    "None"; a Crossref creator with empty fields produced an empty author the
    same way. Either is the invented authorship closed in `uibcdf/ackredit#26`,
    arriving from the network rather than from our own table.
    """
    names = []
    for creator in creators or []:
        if not isinstance(creator, dict):
            continue
        family = html.unescape(str(creator.get("family") or "")).strip()
        given = html.unescape(str(creator.get("given") or "")).strip()
        if name := ", ".join(part for part in (family, given) if part):
            names.append(name)
    return names


def _user_agent() -> str:
    """Announce the version actually running.

    Crossref routes by user agent, so a version that does not exist is worse
    than none. This was pinned at 0.4.0 while the package moved on.
    """
    from .. import __version__

    return f"Ackredit/{__version__} (https://github.com/uibcdf/ackredit)"


class CitationItem(TypedDict, total=False):
    id: str
    type: Literal["article", "software", "repo", "web", "dataset", "other"]
    title: str
    authors: list[str]
    year: int
    doi: str
    url: str
    note: str
    how_to_cite: str
    # and any other bibtex field
    journal: str
    volume: str
    number: str
    pages: str
    publisher: str
    version: str


class Registry:
    # item_id -> item
    items: dict[str, CitationItem] = {}
    # target -> [item_id, ...]
    bindings: dict[str, list[str]] = {}
    # external module -> [item_id, ...]
    injections: dict[str, list[str]] = {}

    @classmethod
    def register_item(cls, **item: Any) -> None:
        if "id" not in item:
            raise ItemIdMissingError(extra={"keys": sorted(item)})
        item_id = item["id"]
        cls.items[item_id] = item  # type: ignore

    @classmethod
    def bind(cls, target: str, items: list[str]) -> None:
        cls.bindings.setdefault(target, [])
        for it in items:
            if it not in cls.bindings[target]:
                cls.bindings[target].append(it)

    @classmethod
    def bound_items(cls, target: str) -> list[str]:
        """
        Return the item ids declared for *target* by :func:`bind`.

        These are the *potential* citations of a code entity, not the ones a run
        actually used. Tracking is what records actual use; see
        :func:`ackredit.track_item` and the ``credit_bound`` option of
        :func:`ackredit.scoped_usage`.

        The returned list is a copy, so callers cannot mutate the registry.
        """
        return list(cls.bindings.get(target, []))

    @classmethod
    def add_injection(cls, target_module: str, items: list[str]) -> None:
        cls.injections.setdefault(target_module, [])
        for it in items:
            if it not in cls.injections[target_module]:
                cls.injections[target_module].append(it)

    @classmethod
    def load_bibtex(cls, file_path: str | Path) -> None:
        """
        Load citation items from a BibTeX file.
        Very lightweight parser inspired by bibtexparser but with zero dependencies.
        """
        path = Path(file_path)
        if not path.exists():
            raise BibtexFileNotFoundError(extra={"path": str(path)})

        content = path.read_text()

        pos = 0
        while True:
            match = re.search(r"@(\w+)\s*\{", content[pos:])
            if not match:
                break

            entry_type = match.group(1).lower()
            start_bracket = pos + match.end()

            # Find matching closing bracket
            bracket_count = 1
            end_pos = start_bracket
            while bracket_count > 0 and end_pos < len(content):
                if content[end_pos] == "{":
                    bracket_count += 1
                elif content[end_pos] == "}":
                    bracket_count -= 1
                end_pos += 1

            if bracket_count == 0:
                entry_body = content[start_bracket : end_pos - 1]
                cls._parse_entry(entry_type, entry_body)

            pos = end_pos

    @classmethod
    def _get_cache_dir(cls) -> Path:
        cache_dir = Path.home() / ".cache" / "ackredit"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @classmethod
    def enrich_item(cls, item_id: str) -> None:
        """
        Fetch missing metadata for an item using its DOI from Crossref API.
        Uses a local cache to avoid redundant network calls.
        """
        item = cls.items.get(item_id)
        if not item or "doi" not in item:
            return

        doi = item["doi"]
        cache_file = cls._get_cache_dir() / f"{_cache_name(doi)}.json"

        data = None

        # 1. Try cache
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
            except Exception as error:
                warn(
                    MetadataCacheWarning(
                        extra={
                            "path": str(cache_file),
                            "operation": "read",
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    )
                )

        # 2. Try network (Crossref first, then DataCite)
        if not data:
            # 2a. Try Crossref
            try:
                url = f"https://api.crossref.org/works/{doi}"
                headers = {"User-Agent": _user_agent()}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())["message"]
            except Exception:
                # 2b. Try DataCite
                try:
                    url = f"https://api.datacite.org/dois/{doi}"
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=5) as response:
                        dc_data = json.loads(response.read().decode())["data"][
                            "attributes"
                        ]
                        # Map DataCite to a Crossref-like format for consistency in the rest of the function
                        # DataCite has `titles: [{title: ...}]`; there is no
                        # scalar `title` attribute in its schema.
                        titles = [
                            entry.get("title")
                            for entry in dc_data.get("titles", [])
                            if entry.get("title")
                        ]
                        data = {
                            "title": titles[:1],
                            "author": [
                                {
                                    "family": a.get("familyName", a.get("name")),
                                    "given": a.get("givenName", ""),
                                }
                                for a in dc_data.get("creators", [])
                            ],
                            "issued": {
                                "date-parts": [[dc_data.get("publicationYear")]]
                            },
                            "container-title": [dc_data.get("publisher", "")],
                        }
                except Exception as error:
                    warn(
                        MetadataFetchWarning(
                            extra={
                                "item_id": item_id,
                                "doi": doi,
                                "source": "Crossref and DataCite",
                                "error_type": type(error).__name__,
                                "error": str(error),
                            }
                        )
                    )

            # Save to cache if we found something
            if data:
                try:
                    cache_file.write_text(json.dumps(data))
                except Exception as error:
                    warn(
                        MetadataCacheWarning(
                            extra={
                                "path": str(cache_file),
                                "operation": "write",
                                "error_type": type(error).__name__,
                                "error": str(error),
                            }
                        )
                    )

        # 3. Apply metadata
        if data:
            try:
                cls._apply_record(item, data)
            except Exception as error:
                # A malformed record is data, not a defect here. It used to
                # raise out of this function and end the caller's run, and
                # `enrich_all` stopped on it, leaving every later item alone.
                warn(
                    MetadataRecordWarning(
                        extra={
                            "item_id": item_id,
                            "doi": doi,
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    )
                )

    @staticmethod
    def _apply_record(item: dict, data: dict) -> None:
        """Fill what the item is missing from a fetched record.

        Text arrives HTML-escaped. Crossref returns the Matplotlib paper's
        journal as "Computing in Science &amp; Engineering", and stored as
        written it reached BibTeX as `\&amp;`, which a bibliography prints. It
        is unescaped here rather than on the way into the cache, so the cache
        stays a faithful copy of what the API answered and a file written before
        this is repaired when it is read.
        """
        if not item.get("title"):
            if title := _first(data.get("title")):
                item["title"] = title

        if not item.get("authors"):
            if authors := _record_authors(data.get("author")):
                item["authors"] = authors

        if not item.get("year"):
            parts = _first(data.get("issued", {}).get("date-parts"))
            if year := _first(parts):
                item["year"] = int(year)

        if not item.get("journal"):
            if journal := _first(data.get("container-title")):
                item["journal"] = journal

    @classmethod
    def enrich_all(cls) -> None:
        """Enrich all registered items that have a DOI."""
        for item_id in list(cls.items.keys()):
            cls.enrich_item(item_id)

    @classmethod
    def load_plugins(cls) -> None:
        """
        Discover and load citation plugins using Python entry points.
        External packages can register citations by adding to their pyproject.toml:
        [project.entry-points."ackredit.citations"]
        anything = "my_package.citations:register"
        """
        from importlib import metadata

        eps = metadata.entry_points()

        # In Python 3.10+, entry_points() returns a SelectableGroups object
        if hasattr(eps, "select"):
            plugins = eps.select(group="ackredit.citations")
        else:
            # Fallback for older versions if necessary
            plugins = eps.get("ackredit.citations", [])

        for entry_point in plugins:
            try:
                register_func = entry_point.load()
                # The function is expected to call ackredit.register_item or ackredit.bind
                register_func()
            except Exception as error:
                # Never propagate: a broken third-party pack must not take the
                # host application down. It is reported, not hidden.
                warn(
                    PluginLoadWarning(
                        extra={
                            "plugin": getattr(entry_point, "name", str(entry_point)),
                            "error_type": type(error).__name__,
                            "error": str(error),
                        }
                    )
                )

    @classmethod
    def _parse_entry(cls, entry_type: str, body: str) -> None:
        # First line is usually the ID/Key
        lines = body.split(",", 1)
        if not lines:
            return

        item_id = lines[0].strip()
        fields_str = lines[1] if len(lines) > 1 else ""

        # Normalize type
        fc_type_map = {
            "article": "article",
            "software": "software",
            "misc": "other",
            "webpage": "web",
            "online": "web",
            "dataset": "dataset",
            "repository": "repo",
        }
        fc_type = fc_type_map.get(entry_type, "other")

        item: Dict[str, Any] = {"id": item_id, "type": fc_type}

        # Parse fields
        field_pattern = re.compile(r'(\w+)\s*=\s*(\{.*?\}|".*?"|[^,]+)', re.DOTALL)

        for field_match in field_pattern.finditer(fields_str):
            key = field_match.group(1).lower()
            value = field_match.group(2).strip()

            # Remove enclosing braces or quotes
            if (value.startswith("{") and value.endswith("}")) or (
                value.startswith('"') and value.endswith('"')
            ):
                value = value[1:-1]

            # Special handling for authors
            if key == "author" or key == "authors":
                # Split by ' and '
                authors = [
                    a.strip()
                    for a in re.split(r"\s+and\s+", value, flags=re.IGNORECASE)
                ]
                item["authors"] = authors
            elif key == "year":
                try:
                    item["year"] = int(value)
                except ValueError:
                    item["year"] = value
                    warn(BibtexFieldWarning(extra={"item_id": item_id, "value": value}))
            else:
                # Direct mapping or standard keys
                fc_key_map = {"journaltitle": "journal", "date": "year"}
                final_key = fc_key_map.get(key, key)
                item[final_key] = value

        # Parsed out of a .bib file, so its fields are LaTeX as the author
        # wrote them and must not be escaped again on the way out.
        item["_source"] = "bibtex"
        cls.register_item(**item)


# convenience functions
def register_item(**item: Any) -> None:
    Registry.register_item(**item)


def bind(target: str, items: list[str]) -> None:
    Registry.bind(target, items)


def bound_items(target: str) -> list[str]:
    return Registry.bound_items(target)


def add_injection(target_module: str, items: list[str]) -> None:
    Registry.add_injection(target_module, items)


def load_bibtex(file_path: str | Path) -> None:
    Registry.load_bibtex(file_path)


def enrich_all() -> None:
    Registry.enrich_all()


def load_plugins() -> None:
    Registry.load_plugins()
