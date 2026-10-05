"""Explicit recorder declarations, separate from portable bibliography and use."""

from __future__ import annotations

import json
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from smonitor import signal

from .._private.smonitor.exceptions import AttributionEvidenceError
from .attribution import Attribution, _json_copy
from .composition import AttributionBundle

_SCHEMA = "ackredit.attribution_evidence@1"
_PLANES = {"metadata_origins", "observation_scope", "recording_gaps"}
_METHODS = {
    "explicit_declaration",
    "provider_declaration",
    "citation_file",
    "bibtex_file",
    "plugin",
    "doi_enrichment",
    "fallback",
}
_MECHANISMS = {
    "explicit_credit",
    "provider_observer",
    "import_hook",
    "static_inspection",
    "host_integration",
}


def _invalid(reason: str) -> None:
    raise AttributionEvidenceError(extra={"reason": reason})


def _text(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        _invalid(
            "evidence names and source/diagnostic identities must be non-empty strings"
        )


def _reader(payload):
    if not isinstance(payload, dict):
        _invalid("attribution must contain a complete portable object")
    if payload.get("schema") == "ackredit.attribution@1":
        return Attribution.from_dict(payload)
    if payload.get("schema") == "ackredit.attribution_bundle@1":
        return AttributionBundle.from_dict(payload)
    _invalid("attribution needs the original single-result or bundle schema")


def _originals(attribution):
    return (
        attribution.attributions
        if isinstance(attribution, AttributionBundle)
        else (attribution,)
    )


def _validate_result(result, original):
    if not isinstance(result, dict) or set(result) != _PLANES:
        _invalid(
            "each result needs metadata_origins, observation_scope and recording_gaps"
        )
    items = {item["id"]: item for item in original.to_dict()["items"]}
    for plane, records in result.items():
        if records is None:
            continue
        if not isinstance(records, list):
            _invalid("each evidence plane must be null or a list of declarations")
        for record in records:
            required = {
                "metadata_origins": {
                    "item_id",
                    "fields",
                    "method",
                    "source",
                    "recorder",
                },
                "observation_scope": {"boundary", "mechanism", "status", "recorder"},
                "recording_gaps": {
                    "boundary",
                    "diagnostic_owner",
                    "diagnostic_code",
                    "recorder",
                },
            }[plane]
            if not isinstance(record, dict) or set(record) != required:
                _invalid(
                    f"{plane} declarations need exactly {', '.join(sorted(required))}"
                )
            for key, value in record.items():
                if key != "fields":
                    _text(value)
            if plane == "metadata_origins":
                item = items.get(record["item_id"])
                fields = record["fields"]
                if item is None:
                    _invalid(
                        "metadata origins must refer to an item in this original result"
                    )
                if not isinstance(fields, list) or not fields:
                    _invalid(
                        "metadata origins need a non-empty list of retained field names"
                    )
                for field in fields:
                    _text(field)
                    if field not in item:
                        _invalid(
                            "metadata origins cannot describe absent bibliographic fields"
                        )
                if len(set(fields)) != len(fields):
                    _invalid("metadata-origin field names must be unique")
                if record["method"] not in _METHODS:
                    _invalid("unknown metadata-origin method")
            elif plane == "observation_scope":
                if record["mechanism"] not in _MECHANISMS:
                    _invalid("unknown observation mechanism")
                if record["status"] not in {"selected", "unsupported", "unobserved"}:
                    _invalid("scope status must be selected, unsupported or unobserved")


class AttributionEvidence:
    """Provisional saved companion for explicit, bounded recorder declarations.

    The embedded attribution remains its own complete contract. Evidence is
    positional per original result, never joined by a potentially repeated name.
    Null means unrecorded; an empty list only states that no declarations were
    supplied. Neither certifies complete instrumentation or successful science.
    Source locators and diagnostic identities are retained, never dereferenced.
    """

    def __init__(self, payload: Mapping[str, Any]):
        if not isinstance(payload, Mapping):
            _invalid("the payload must be a JSON object")
        data = _json_copy(dict(payload), "read attribution evidence")
        if (
            set(data) != {"schema", "attribution", "results"}
            or data["schema"] != _SCHEMA
        ):
            _invalid(f"expected the complete {_SCHEMA} envelope")
        attribution = _reader(data["attribution"])
        originals = _originals(attribution)
        if not isinstance(data["results"], list) or len(data["results"]) != len(
            originals
        ):
            _invalid("evidence needs exactly one entry per original result")
        for result, original in zip(data["results"], originals):
            _validate_result(result, original)
        data["attribution"] = attribution.to_dict()
        self._payload = data

    @classmethod
    @signal(tags=["ackredit", "evidence"])
    def from_attribution(cls, attribution, *, results=None) -> AttributionEvidence:
        """Attach explicit declarations to a detached result or bundle.

        Omitted results create three unrecorded planes per original. Collection
        is never automatic: callers must supply actual recorder declarations.
        """
        if not isinstance(attribution, (Attribution, AttributionBundle)):
            _invalid("an Attribution or AttributionBundle is required")
        if results is None:
            results = [dict.fromkeys(sorted(_PLANES)) for _ in _originals(attribution)]
        return cls(
            dict(schema=_SCHEMA, attribution=attribution.to_dict(), results=results)
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AttributionEvidence:
        """Validate and detach explicit saved declarations without replaying them."""
        return cls(payload)

    @classmethod
    def from_json(cls, content: str) -> AttributionEvidence:
        """Read inert UTF-8 JSON content; no file, provider or service is opened."""
        try:
            data = json.loads(content)
        except (TypeError, ValueError, RecursionError) as error:
            _invalid(str(error))
        return cls(data)

    @property
    def attribution(self) -> Attribution | AttributionBundle:
        """Return the separately readable original attribution, freshly detached."""
        return _reader(deepcopy(self._payload["attribution"]))

    def to_dict(self) -> dict[str, Any]:
        """Return a fresh complete envelope, including unknown and empty planes."""
        return deepcopy(self._payload)

    def to_json(self) -> str:
        """Serialize original evidence without network or tracking side effects."""
        return json.dumps(self._payload, ensure_ascii=False, allow_nan=False, indent=2)

    def explain(self) -> dict[str, Any]:
        """Keep declared recorder evidence separate from descriptive use analysis."""
        from .explanation import explain_attribution

        return {
            "schema": "ackredit.attribution_evidence_explanation@1",
            "attribution": explain_attribution(self.attribution),
            "results": deepcopy(self._payload["results"]),
            "limits": [
                "Declarations name their recorder; accepting them does not independently verify their truth.",
                "Metadata origin describes retained fields, not execution evidence or citation correctness.",
                "Selected observation boundaries do not establish that a function ran or instrumentation was complete.",
                "Unrecorded planes and empty declaration lists do not establish absence of citable work or recording failures.",
                "Diagnosed gaps retain owning diagnostic identities; no missing citation or scientific failure is inferred.",
                "Original-result order and repeated declarations do not imply chronology or invocation counts.",
            ],
        }

    def report(self, format: str = "explanation", **options: Any) -> str:
        """Explain explicit declarations, or render the original bibliography/graph.

        Only explanation renders the companion. Other formats delegate to the
        complete original and remain byte-identical; to_json saves both planes.
        """
        from .report import _resolve_format

        if not isinstance(format, str) or not format.strip():
            _invalid("a non-empty report format is required")
        if _resolve_format(format) == "explanation":
            if options:
                _invalid("evidence explanations take no report options")
            from ..formats.explanation import render_evidence

            return render_evidence(self)
        return self.attribution.report(format=format, **options)
