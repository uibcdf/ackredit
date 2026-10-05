"""Describe saved evidence without guessing unrecorded observation boundaries."""

from __future__ import annotations

import json

from smonitor import signal

from .attribution import Attribution, _invalid
from .composition import AttributionBundle

_LIMITS = (
    "Recorded uses do not imply call counts, chronology, scientific success or complete instrumentation.",
    "No recorded references does not prove that no citable work was used.",
    "Absent fields describe the saved record; they are not mandatory citation requirements or a correctness assessment.",
    "DOIs, URLs and caller-owned context do not establish metadata origin or bibliographic truth.",
    "No diagnosed gap information is not evidence that recording was complete or successful.",
)


def _result(payload: dict) -> dict:
    uses = list(
        {
            json.dumps(use, sort_keys=True, ensure_ascii=False): use
            for use in payload["uses"]
        }.values()
    )
    by_item = {item["id"]: [] for item in payload["items"]}
    for use in uses:
        by_item[use["item_id"]].append(use)
    references = []
    for item in payload["items"]:
        evidence = by_item[item["id"]]
        fields = ["type", "title", "authors"]
        if item.get("type") == "software":
            fields.append("version")
        references.append(
            {
                "item_id": item["id"],
                "distinct_recorded_uses": len(evidence),
                "used_by": sorted(
                    {use["used_by"] for use in evidence if use["used_by"] is not None}
                ),
                "unscoped_uses": sum(use["used_by"] is None for use in evidence),
                "roles": sorted({role for use in evidence for role in use["roles"]}),
                "metadata_fields": sorted(set(item) - {"id"}),
                "fields_absent": [field for field in fields if field not in item],
                "metadata_origin": "not_recorded",
                **({"version": item["version"]} if "version" in item else {}),
            }
        )
    return {
        "name": payload["name"],
        "context": payload["context"],
        "counts": {
            "references": len(references),
            "recorded_use_records": len(payload["uses"]),
            "distinct_recorded_uses": len(uses),
            "recorded_graph_targets": len(payload["usage_tree"]),
            "unscoped_uses": sum(use["used_by"] is None for use in uses),
        },
        "instrumentation_scope": "not_recorded",
        "diagnosed_recording_gaps": "not_recorded",
        "references": references,
        "graph_targets_without_direct_references": sorted(
            target
            for target, node in payload["usage_tree"].items()
            if not node["items"]
        ),
    }


@signal(tags=["ackredit", "explanation"])
def explain_attribution(attribution: Attribution | AttributionBundle) -> dict:
    """Return a detached descriptive view of validated saved attribution.

    Each original result retains its own evidence counts, roles and targets.
    Scope, metadata origin and diagnosed gaps stay ``not_recorded``: current
    portable schemas define no negotiated plane for those facts. Arbitrary
    context or bibliographic fields cannot substitute for that missing contract.

    The version-labelled view is not an attribution payload or a completeness
    score. Reading it never registers references, credits uses, imports a
    producer, queries a service or changes the originals. Field absence is
    reported by key presence, without judging supplied values or citation truth.
    """
    if not isinstance(attribution, (Attribution, AttributionBundle)):
        _invalid(
            "explain attribution", "an Attribution or AttributionBundle is required"
        )
    payload = attribution.to_dict()
    originals = (
        payload["attributions"]
        if isinstance(attribution, AttributionBundle)
        else [payload]
    )
    return {
        "schema": "ackredit.attribution_explanation@1",
        "source_schema": payload["schema"],
        "name": payload["name"],
        "counts": {
            "input_records": len(originals),
            "shared_references": len(
                {item["id"] for original in originals for item in original["items"]}
            ),
        },
        "results": [_result(original) for original in originals],
        "limits": list(_LIMITS),
    }
