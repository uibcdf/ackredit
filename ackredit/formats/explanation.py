"""Render the owning offline evidence explanation without duplicating analysis."""

from __future__ import annotations

import json

from ._markdown import escape
from .workflow import _cell


def render(used, items) -> str:
    """Explain a detached current snapshot through the public tool."""
    from ..core.attribution import get_attribution

    return render_attribution(get_attribution())


def render_attribution(attribution) -> str:
    """Render validated original results; no producer or registry lookup."""
    from ..core.explanation import explain_attribution

    view = explain_attribution(attribution)
    lines = [
        "# Attribution explanation",
        "",
        f"**Name:** {escape(view['name'])}",
        "",
        f"Input records: {view['counts']['input_records']} · Shared bibliography: {view['counts']['shared_references']}",
        "",
        "## Interpretation limits",
        "",
        *[f"- {limit}" for limit in view["limits"]],
        "",
        "Instrumentation scope, metadata origin and diagnosed recording gaps: **Not recorded** by the current portable schemas.",
        "",
    ]
    for index, result in enumerate(view["results"], 1):
        counts = result["counts"]
        lines.extend(
            [
                f"## Result {index}: {escape(result['name'])}",
                "",
                f"References: {counts['references']} · Recorded use records: {counts['recorded_use_records']} · Distinct recorded uses: {counts['distinct_recorded_uses']} · Graph targets: {counts['recorded_graph_targets']} · Unscoped uses: {counts['unscoped_uses']}",
                "",
            ]
        )
        if not result["references"]:
            lines.extend(["No references were recorded for this result.", ""])
        else:
            lines.extend(
                [
                    "| Reference identifier | Recorded version | Contextual uses | Targets | Roles | Fields absent (presence only) |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for reference in result["references"]:
                cells = [
                    _cell(reference["item_id"]),
                    _cell(json.dumps(reference["version"], ensure_ascii=False))
                    if "version" in reference
                    else "Not recorded",
                    str(reference["distinct_recorded_uses"]),
                    _cell(", ".join(reference["used_by"])) or "Not recorded",
                    _cell(", ".join(reference["roles"])) or "Not recorded",
                    _cell(", ".join(reference["fields_absent"]))
                    or "None of the checked fields",
                ]
                lines.append("| " + " | ".join(cells) + " |")
            lines.append("")
        uncontextualized = [
            reference["item_id"]
            for reference in result["references"]
            if not reference["distinct_recorded_uses"]
        ]
        if uncontextualized:
            lines.extend(
                [
                    "References with no contextual use recorded: "
                    + ", ".join(escape(item_id) for item_id in uncontextualized)
                    + ". This does not establish that they were unused.",
                    "",
                ]
            )
        structural = result["graph_targets_without_direct_references"]
        if structural:
            lines.extend(
                [
                    "Graph targets without direct references: "
                    + ", ".join(escape(target) for target in structural)
                    + ". Enclosing workflow nodes can legitimately have no direct references; these are not diagnosed gaps.",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
