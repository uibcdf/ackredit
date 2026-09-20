from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path
from typing import Any, Dict, Literal, TypedDict


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
            raise ValueError("Item must have an 'id'")
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
            raise FileNotFoundError(f"BibTeX file not found: {path}")

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
        safe_doi = doi.replace("/", "_")
        cache_file = cls._get_cache_dir() / f"{safe_doi}.json"

        data = None

        # 1. Try cache
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text())
            except Exception:
                pass

        # 2. Try network (Crossref first, then DataCite)
        if not data:
            # 2a. Try Crossref
            try:
                url = f"https://api.crossref.org/works/{doi}"
                headers = {
                    "User-Agent": "Ackredit/0.4.0 (https://github.com/uibcdf/ackredit)"
                }
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
                        data = {
                            "title": [dc_data.get("title")]
                            if dc_data.get("title")
                            else [
                                t.get("title") for t in dc_data.get("titles", [])[:1]
                            ],
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
                except Exception:
                    pass

            # Save to cache if we found something
            if data:
                try:
                    cache_file.write_text(json.dumps(data))
                except Exception:
                    pass

        # 3. Apply metadata
        if data:
            # Update title if missing
            if "title" not in item or not item["title"]:
                item["title"] = data.get("title", [item_id])[0]

            # Update authors if missing
            if "authors" not in item or not item["authors"]:
                authors = []
                for auth in data.get("author", []):
                    given = auth.get("given", "")
                    family = auth.get("family", "")
                    authors.append(f"{family}, {given}".strip(", "))
                if authors:
                    item["authors"] = authors

            # Update year if missing
            if "year" not in item or not item["year"]:
                issued = data.get("issued", {}).get("date-parts", [[None]])[0][0]
                if issued:
                    item["year"] = int(issued)

            # Update journal if missing
            if "journal" not in item or not item["journal"]:
                container = data.get("container-title", [])
                if container:
                    item["journal"] = container[0]

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
            except Exception:
                # Fail silently to avoid breaking the host application
                pass

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
            else:
                # Direct mapping or standard keys
                fc_key_map = {"journaltitle": "journal", "date": "year"}
                final_key = fc_key_map.get(key, key)
                item[final_key] = value

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
