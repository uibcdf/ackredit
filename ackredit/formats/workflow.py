"""Render recorded bibliography, contextual uses and graph as one offline report."""

from __future__ import annotations

import json
import re

from . import markdown, provenance
from ._links import doi_link
from ._markdown import destination, escape, safe_link


def _fenced(content: str, language: str = "") -> list[str]:
    """External graph/context text cannot terminate its own Markdown code block."""
    longest = max((len(run) for run in re.findall(r"`+", content)), default=0)
    fence = "`" * max(3, longest + 1)
    return [f"{fence}{language}", content, fence, ""]


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _cell(value) -> str:
    return escape(value).replace("|", "\\|")


def _one_line(value) -> str:
    return json.dumps(str(value), ensure_ascii=False)[1:-1]


def render(used, items) -> str:
    """Render a snapshot of the current workflow using the shared public contract."""
    from ..core.attribution import get_attribution

    return render_payload(get_attribution().to_dict())


def _references(
    items: list[dict], numbers: dict[str, int], heading_level: int
) -> list[str]:
    lines = [f"{'#' * heading_level} References", ""]
    if not items:
        lines.extend(["No references were recorded.", ""])
    for item in items:
        item_id = item["id"]
        lines.extend([f"{'#' * (heading_level + 1)} Reference {numbers[item_id]}", ""])
        lines.extend(markdown._reference_lines(item_id, item, []))
        lines.append(f"  - Identifier: {escape(item_id)}")
        lines.append(f"  - Type: {escape(item.get('type', 'Not recorded'))}")
        if "version" in item:
            lines.append(f"  - Version: {escape(item['version'])}")
        for field, label in (
            ("journal", "Journal"),
            ("volume", "Volume"),
            ("number", "Issue"),
            ("pages", "Pages"),
            ("publisher", "Publisher"),
            ("date", "Date"),
        ):
            if field in item:
                lines.append(f"  - {label}: {escape(item[field])}")
        if item.get("doi"):
            doi = str(item["doi"])
            lines.append(f"  - DOI: [{escape(doi)}]({destination(doi_link(doi))})")
        url = safe_link(item.get("url"))
        if url:
            lines.append(f"  - URL: [{escape(url)}]({destination(url)})")
        if set(item) <= {"id", "title"}:
            lines.append("  - Bibliographic metadata: Not recorded")
        lines.append("")
        shown = {
            "id",
            "title",
            "authors",
            "year",
            "note",
            "type",
            "version",
            "doi",
            "url",
            "journal",
            "volume",
            "number",
            "pages",
            "publisher",
            "date",
        }
        remaining = {key: value for key, value in item.items() if key not in shown}
        if remaining:
            lines.extend(["Other recorded metadata:", ""])
            lines.extend(_fenced(_json(remaining), "json"))
    return lines


def render_payload(
    payload: dict,
    *,
    numbers: dict[str, int] | None = None,
    include_references: bool = True,
    heading_level: int = 1,
    evidence: dict | None = None,
) -> str:
    """Render validated original records; do not inspect the reader's registry."""
    items = payload["items"]
    # External payloads may repeat an identical use. Count distinct evidence,
    # without changing the preserved payload or interpreting it as call counts.
    uses = list({_json(use): use for use in payload["uses"]}.values())
    tree = payload["usage_tree"]
    if numbers is None:
        numbers = {item["id"]: number for number, item in enumerate(items, 1)}
    lines = [
        f"{'#' * heading_level} Workflow attribution",
        "",
        f"**Name:** {escape(payload['name'])}",
        "",
        f"References: {len(items)} · Distinct recorded uses: {len(uses)} · Recorded targets: {len(tree)}",
        "",
        "Recorded uses do not imply call counts, chronology, scientific success or complete instrumentation.",
        "",
    ]
    if payload["context"]:
        lines.extend([f"{'#' * (heading_level + 1)} Original capture context", ""])
        lines.extend(_fenced(_json(payload["context"]), "json"))
    if include_references:
        lines.extend(_references(items, numbers, heading_level + 1))
    lines.extend([f"{'#' * (heading_level + 1)} Recorded uses", ""])
    if uses:
        lines.extend(
            [
                "| Target | Reference | Roles | Original use context |",
                "| --- | --- | --- | --- |",
            ]
        )
        for use in uses:
            cells = [
                _cell(use["used_by"]) if use["used_by"] is not None else "Unscoped",
                str(numbers[use["item_id"]]),
                _cell(", ".join(use["roles"])) if use["roles"] else "Not recorded",
                _cell(_json(use["context"])) if use["context"] else "Not recorded",
            ]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
    else:
        lines.extend(["No contextual uses were recorded.", ""])
    if evidence is not None:
        lines.extend(_evidence_lines(evidence, items, numbers, heading_level + 1))
    lines.extend([f"{'#' * (heading_level + 1)} Recorded graph", ""])
    records = {
        item["id"]: {
            "title": f"Reference {numbers[item['id']]}: {_one_line(item.get('title', item['id']))}"
        }
        for item in items
    }
    display_tree = {
        _one_line(target): {
            **node,
            "children": [_one_line(child) for child in node["children"]],
        }
        for target, node in tree.items()
    }
    lines.extend(_fenced(provenance.render_tree(display_tree, records), "text"))
    return "\n".join(lines).rstrip() + "\n"


def render_bundle(
    payload: dict, items: list[dict], *, evidence: list[dict] | None = None
) -> str:
    """Number shared references once while retaining every original result graph."""
    numbers = {item["id"]: number for number, item in enumerate(items, 1)}
    lines = [
        "# Attribution bundle",
        "",
        f"**Name:** {escape(payload['name'])}",
        "",
        f"Input records: {len(payload['attributions'])} · Shared bibliography: {len(items)}",
        "",
        "Input order is presentation order, not execution chronology. Reused inputs remain separate; graphs are never joined across results.",
        "",
    ]
    if payload["context"]:
        lines.extend(["## Bundle context", ""])
        lines.extend(_fenced(_json(payload["context"]), "json"))
    lines.extend(_references(items, numbers, 2))
    for index, record in enumerate(payload["attributions"], 1):
        lines.extend([f"## Result {index}: {escape(record['name'])}", ""])
        lines.append(
            render_payload(
                record,
                numbers=numbers,
                include_references=False,
                heading_level=3,
                evidence=evidence[index - 1] if evidence is not None else None,
            )
        )
    if not payload["attributions"]:
        lines.extend(["No input attributions were supplied.", ""])
    return "\n".join(lines).rstrip() + "\n"


def _evidence_lines(result, items, numbers, heading_level):
    """Present validated declarations without inferring unrecorded facts."""
    heading = "#" * heading_level
    lines = [
        f"{heading} Recorder evidence",
        "",
        "These are recorder declarations, not certification of bibliographic truth, scientific success or complete instrumentation.",
        "",
        f"{heading} Metadata sources",
        "",
        "Sources describe only the listed retained fields. Other field origins remain unknown; this does not imply a missing or incorrect citation. Source locators are not opened.",
        "",
    ]
    origins = result["metadata_origins"]
    if origins is None:
        lines.extend(["Metadata origins: Not recorded.", ""])
    elif not origins:
        lines.extend(
            [
                "No metadata-source declarations supplied. Field origins remain unknown.",
                "",
            ]
        )
    if origins:
        methods = {
            "explicit_declaration": "Explicit declaration",
            "provider_declaration": "Provider declaration",
            "citation_file": "Citation file",
            "bibtex_file": "BibTeX file",
            "plugin": "Plugin",
            "doi_enrichment": "DOI enrichment",
            "fallback": "Fallback",
        }
        lines.extend(
            [
                "| Reference | Retained fields | Method | Source | Recorder |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for origin in origins:
            cells = [
                str(numbers[origin["item_id"]]),
                _cell(_json(origin["fields"])),
                methods[origin["method"]],
                _cell(origin["source"]),
                _cell(origin["recorder"]),
            ]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")
        supplied = {origin["item_id"] for origin in origins}
        absent = [
            str(numbers[item["id"]]) for item in items if item["id"] not in supplied
        ]
        if absent:
            lines.extend(
                [
                    "References with no metadata-source declaration: "
                    + ", ".join(absent)
                    + ". Their origins remain unknown.",
                    "",
                ]
            )
    for plane, title, headers, keys, limit in (
        (
            "observation_scope",
            "Observation boundaries",
            ("Boundary", "Mechanism", "Declared status", "Recorder"),
            ("boundary", "mechanism", "status", "recorder"),
            "Selected boundaries do not establish that a function ran. Unsupported or unobserved boundaries need not have a recorded graph node.",
        ),
        (
            "recording_gaps",
            "Diagnosed recording gaps",
            ("Boundary", "Diagnostic owner", "Diagnostic code", "Recorder"),
            ("boundary", "diagnostic_owner", "diagnostic_code", "recorder"),
            "Stored diagnostic identities are not emitted again. They do not identify a missing citation or establish scientific failure; absence of declarations does not establish absence of failures.",
        ),
    ):
        lines.extend([f"{heading} {title}", "", limit, ""])
        records = result[plane]
        if records is None:
            lines.extend(["Not recorded.", ""])
        elif not records:
            lines.extend(
                ["No declarations supplied. This does not establish completeness.", ""]
            )
        else:
            lines.extend(
                [
                    "| " + " | ".join(headers) + " |",
                    "| " + " | ".join("---" for _ in keys) + " |",
                ]
            )
            for record in records:
                lines.append(
                    "| " + " | ".join(_cell(record[key]) for key in keys) + " |"
                )
            lines.append("")
    return lines


def render_evidence(evidence) -> str:
    """Join a validated companion with the owning workflow presentation."""
    from ..core.composition import _bibliography

    payload = evidence.to_dict()
    original = payload["attribution"]
    if original["schema"] == "ackredit.attribution_bundle@1":
        return render_bundle(
            original,
            list(_bibliography(original["attributions"]).values()),
            evidence=payload["results"],
        )
    return render_payload(original, evidence=payload["results"][0])
