from __future__ import annotations

import hashlib
import html
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterator, Literal, TypedDict

from .._private.argdigest import arg_digest
from .._private.smonitor.emitter import warn
from .._private.smonitor.exceptions import (
    BibtexFileNotFoundError,
    ItemIdMissingError,
)
from .._private.smonitor.warnings import (
    BibtexEntryWarning,
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


# A field name and its `=`, from which a value follows. What the value *is*
# cannot be matched: `\{.*?\}` stops at the first closing brace, so
# `title = {The {DNA} helix}` yielded `The {DNA`, and brace protection is the
# ordinary way to stop a style lowercasing an acronym.
_FIELD_START = re.compile(r"\s*,?\s*(\w+)\s*=\s*")


def _collapse(value: str) -> str:
    """One line, the way a TeX engine reads a braced value."""
    return re.sub(r"\s+", " ", value).strip()


def _read_braced(text: str, start: int) -> tuple[str, int]:
    """The contents of the group at *start*, and where it ends.

    The inner braces are kept: they are what protects `{DNA}` from a style that
    would otherwise lowercase it, and dropping them changes the citation.
    """
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return _collapse(text[start + 1 : index]), index + 1
    # Unbalanced. Take what there is rather than lose the field.
    return _collapse(text[start + 1 :]), len(text)


def _read_quoted(text: str, start: int) -> tuple[str, int]:
    """A quoted value, which ends at a quote outside any braces."""
    depth = 0
    for index in range(start + 1, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == '"' and depth == 0:
            return _collapse(text[start + 1 : index]), index + 1
    return _collapse(text[start + 1 :]), len(text)


def _bibtex_fields(body: str) -> Iterator[tuple[str, str]]:
    """Each `key = value` in an entry body, values read by scanning."""
    position = 0
    while position < len(body):
        match = _FIELD_START.match(body, position)
        if not match:
            # Not a field here. Skip to the next one rather than abandon the
            # entry, so one malformed field costs only itself.
            comma = body.find(",", position)
            if comma == -1:
                return
            position = comma + 1
            continue

        key = match.group(1)
        position = match.end()
        if position >= len(body):
            return

        if body[position] == "{":
            value, position = _read_braced(body, position)
        elif body[position] == '"':
            value, position = _read_quoted(body, position)
        else:
            comma = body.find(",", position)
            end = len(body) if comma == -1 else comma
            value, position = body[position:end].strip(), end

        yield key, value


def _split_bibtex_authors(value: str) -> list[str]:
    """Split on BibTeX's `and`, which separates names only outside braces.

    `{Smith and Sons}` is one corporate author, and braces are exactly what say
    so, which splitting anywhere ignored.
    """
    names, depth, start, index = [], 0, 0, 0
    while index < len(value):
        char = value[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif (
            depth == 0
            and index > 0
            and value[index - 1].isspace()
            and value[index : index + 3].lower() == "and"
            and value[index + 3 : index + 4].isspace()
        ):
            names.append(value[start:index].strip())
            index += 3
            start = index
            continue
        index += 1

    names.append(value[start:].strip())
    return [name for name in names if name]


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


# What Crossref allows a client that does not identify itself. Its responses
# carry the real numbers and the throttle adopts them; these are what to assume
# until one has been seen.
_DEFAULT_RATE_LIMIT = 5
_DEFAULT_RATE_INTERVAL = 1.0

# How long a cached answer keeps. A published record's metadata rarely changes,
# and one cached while it was "in press" is wrong until it is asked again, so
# this is long enough to spare the services and short enough that a year arrives.
_CACHE_MAX_AGE = 30 * 24 * 60 * 60

# The environment variable a user sets to be identified to the metadata
# services. Deliberately not defaulted: see `_contact`.
CONTACT_VARIABLE = "ACKREDIT_CONTACT_EMAIL"

# Entry-point group for citation packs, beside `ackredit.formats` in
# `ackredit/core/report.py`. Both are asked for the same way.
_CITATION_GROUP = "ackredit.citations"

_throttle_lock = threading.Lock()
_throttle = {
    "limit": _DEFAULT_RATE_LIMIT,
    "interval": _DEFAULT_RATE_INTERVAL,
    "last": 0.0,
}


def _contact() -> str | None:
    """The address a user chose to be identified by, if any.

    Crossref's polite pool doubles the allowance for a client that gives a
    contact, and Ackredit does not take it by default. Baking in a maintainer's
    address would attribute every user's requests to one person and misuse the
    pool, and sending a user's address to a third party is theirs to decide, so
    it is opt-in through the environment and off until then.
    """
    value = os.environ.get(CONTACT_VARIABLE, "").strip()
    return value or None


def _user_agent() -> str:
    """Announce the version actually running.

    Crossref routes by user agent, so a version that does not exist is worse
    than none. This was pinned at 0.4.0 while the package moved on.
    """
    from .. import __version__

    agent = f"Ackredit/{__version__} (https://github.com/uibcdf/ackredit)"
    if contact := _contact():
        agent += f" mailto:{contact}"
    return agent


def _wait_turn() -> None:
    """Hold until the next request is within the advertised rate.

    `enrich_all` used to issue one request per item with nothing between them —
    measured at 5 326 per second against an advertised 5 — and network latency
    is not a policy.
    """
    with _throttle_lock:
        limit = max(_throttle["limit"], 1)
        gap = _throttle["interval"] / limit
        wait = _throttle["last"] + gap - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _throttle["last"] = time.monotonic()


def _adopt_rate(headers) -> None:
    """Take the rate the service just stated, in place of what we assumed."""
    try:
        limit = int(headers.get("x-rate-limit-limit", ""))
        interval = headers.get("x-rate-limit-interval", "").strip()
        seconds = float(interval.removesuffix("s")) if interval.endswith("s") else None
    except (TypeError, ValueError):
        return

    with _throttle_lock:
        if limit > 0:
            _throttle["limit"] = limit
        if seconds and seconds > 0:
            _throttle["interval"] = seconds


def _fetch(url: str, headers: dict) -> dict:
    """One request, within the rate, retried once if we are asked to slow down.

    A 429 used to be caught with everything else and reported as
    `ACKREDIT-W006`, whose user message says to check network access. The
    network was fine; we asked too fast.
    """
    for attempt in (1, 2):
        _wait_turn()
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                _adopt_rate(response.headers)
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 2:
                raise
            _adopt_rate(error.headers)
            time.sleep(_throttle["interval"])
    raise RuntimeError("unreachable")


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
            else:
                # A truncated download or a hand-edited file. The entry is lost
                # either way; it used to be lost without saying so.
                warn(
                    BibtexEntryWarning(
                        extra={
                            "path": str(path),
                            "entry_type": entry_type,
                            "offset": start_bracket,
                        }
                    )
                )

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

        # 1. Try cache. An answer has an age, taken from the file's own
        # modification time so the stored format is still what the API replied
        # and an entry written before this has a freshness rather than being
        # thrown away.
        cached = None
        fresh = False
        if cache_file.exists():
            try:
                cached = json.loads(cache_file.read_text())
                fresh = (time.time() - cache_file.stat().st_mtime) < _CACHE_MAX_AGE
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

        data = cached if fresh else None

        # 2. Try network (Crossref first, then DataCite)
        if not data:
            # 2a. Try Crossref
            headers = {"User-Agent": _user_agent()}
            failure = None
            try:
                data = _fetch(f"https://api.crossref.org/works/{doi}", headers)[
                    "message"
                ]
            except Exception:
                # 2b. Try DataCite
                try:
                    dc_data = _fetch(f"https://api.datacite.org/dois/{doi}", headers)[
                        "data"
                    ]["attributes"]
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
                        "issued": {"date-parts": [[dc_data.get("publicationYear")]]},
                        "container-title": [dc_data.get("publisher", "")],
                    }
                except Exception as error:
                    failure = error

            if not data and cached:
                # The refresh did not come back and the stale answer still is
                # one. A cache exists so a run without a network keeps its
                # metadata, and expiring into nothing would take from the user
                # a citation they already had. Nothing is reported, because
                # nothing was lost.
                data = cached
            elif failure is not None:
                warn(
                    MetadataFetchWarning(
                        extra={
                            "item_id": item_id,
                            "doi": doi,
                            "source": "Crossref and DataCite",
                            "error_type": type(failure).__name__,
                            "error": str(failure),
                        }
                    )
                )

            # Save to cache if we found something newer than what it held
            if data is not cached:
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
        r"""Fill what the item is missing from a fetched record.

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
        """Load the citation packs other packages provide.

        A package ships one by declaring an entry point that registers::

            [project.entry-points."ackredit.citations"]
            anything = "my_package.citations:register"

        The entry point loads a callable, which is called with no arguments and
        is expected to call `register_item`, `bind` or `add_injection`. Calling
        this twice is safe: `register_item` overwrites and `add_injection`
        deduplicates, so a pack that only declares has no second effect.

        A pack that fails raises `ACKREDIT-W008` and never propagates, so a
        broken third party cannot take the host down, and the packs beside it
        still load.

        This used to ask for the group in two ways, the second for the dict
        `entry_points()` returned before Python 3.10 — unreachable here, since
        the supported range starts at 3.11, and an `AttributeError` rather than
        a fallback if it ever had been.
        """
        from importlib import metadata

        for entry_point in metadata.entry_points(group=_CITATION_GROUP):
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

        for raw_key, value in _bibtex_fields(fields_str):
            key = raw_key.lower()

            if key == "author" or key == "authors":
                item["authors"] = _split_bibtex_authors(value)
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

        # Ackredit's vocabulary has six types and BibTeX has fourteen, so
        # `@book` and `@phdthesis` both flatten to `other` and were written back
        # as `@misc`. The original is kept so the round trip is exact; it is
        # bookkeeping, not a field, hence the underscore.
        item["_bibtex_type"] = entry_type
        cls.register_item(**item)


# convenience functions
@arg_digest()
def register_item(**item: Any) -> None:
    Registry.register_item(**item)


@arg_digest()
def bind(target: str, items: list[str]) -> None:
    Registry.bind(target, items)


def bound_items(target: str) -> list[str]:
    return Registry.bound_items(target)


@arg_digest()
def add_injection(target_module: str, items: list[str]) -> None:
    Registry.add_injection(target_module, items)


@arg_digest()
def load_bibtex(file_path: str | Path) -> None:
    Registry.load_bibtex(file_path)


def enrich_all() -> None:
    Registry.enrich_all()


def load_plugins() -> None:
    Registry.load_plugins()
