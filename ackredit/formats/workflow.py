"""Render recorded bibliography, contextual uses and graph as one offline report."""

from __future__ import annotations

import json
import re

from . import markdown, provenance
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


def render_payload(payload: dict) -> str:
    """Render validated original records; do not inspect the reader's registry."""
    items = payload["items"]
    # External payloads may repeat an identical use. Count distinct evidence,
    # without changing the preserved payload or interpreting it as call counts.
    uses = list({_json(use): use for use in payload["uses"]}.values())
    tree = payload["usage_tree"]
    numbers = {item["id"]: number for number, item in enumerate(items, 1)}
    lines = [
        "# Workflow attribution",
        "",
        f"**Name:** {escape(payload['name'])}",
        "",
        f"References: {len(items)} · Distinct recorded uses: {len(uses)} · Recorded targets: {len(tree)}",
        "",
        "Recorded uses do not imply call counts, chronology, scientific success or complete instrumentation.",
        "",
    ]
    if payload["context"]:
        lines.extend(["## Original capture context", ""])
        lines.extend(_fenced(_json(payload["context"]), "json"))
    lines.extend(["## References", ""])
    if not items:
        lines.extend(["No references were recorded.", ""])
    for item in items:
        item_id = item["id"]
        lines.extend([f"### Reference {numbers[item_id]}", ""])
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
            lines.append(
                f"  - DOI: [{escape(doi)}]({destination('https://doi.org/' + doi)})"
            )
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
    lines.extend(["## Recorded uses", ""])
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
    lines.extend(["## Recorded graph", ""])
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
