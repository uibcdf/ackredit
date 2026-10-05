"""Detached result composition with shared references and independent graphs."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from copy import deepcopy
from typing import Any

from smonitor import signal

from .._private.smonitor.exceptions import (
    AttributionBundleError,
    AttributionConflictError,
)
from .attribution import Attribution, _context, _json_copy, _name

_SCHEMA = "ackredit.attribution_bundle@1"


def _invalid(reason: str) -> None:
    raise AttributionBundleError(extra={"reason": reason})


def _bibliography(attributions: list[dict]) -> dict[str, dict]:
    records = {}
    for attribution in attributions:
        for record in attribution["items"]:
            item_id = record["id"]
            if item_id in records and records[item_id] != record:
                raise AttributionConflictError(extra={"item_id": item_id})
            records[item_id] = record
    return dict(sorted(records.items()))


class AttributionBundle:
    """Original result attributions with one conflict-checked bibliography.

    Members retain their names, contexts, uses and graphs. Their order is
    presentation order, not chronology. Reading and rendering never credit
    uses, import a producer or consult the current registry.
    """

    def __init__(self, payload: Mapping[str, Any]):
        if not isinstance(payload, Mapping):
            _invalid("the payload must be a JSON object")
        data = _json_copy(dict(payload), "read attribution bundle")
        if (
            set(data) != {"schema", "name", "context", "attributions"}
            or data["schema"] != _SCHEMA
        ):
            _invalid(f"expected the complete {_SCHEMA} payload")
        _name(data["name"], "read attribution bundle name")
        if not isinstance(data["context"], dict):
            _invalid("context must be a JSON object")
        if not isinstance(data["attributions"], list):
            _invalid("attributions must be a list of complete original records")
        data["attributions"] = [
            Attribution.from_dict(record).to_dict() for record in data["attributions"]
        ]
        self._records = _bibliography(data["attributions"])
        self._payload = data

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> AttributionBundle:
        """Validate every member and bibliography before returning a bundle."""
        return cls(payload)

    @classmethod
    def from_json(cls, content: str) -> AttributionBundle:
        """Read the versioned envelope without a producer or live session."""
        try:
            data = json.loads(content)
        except (TypeError, ValueError, RecursionError) as error:
            _invalid(str(error))
        return cls(data)

    @property
    def attributions(self) -> tuple[Attribution, ...]:
        """Return newly detached original members, including reused/empty inputs."""
        return tuple(Attribution(record) for record in self._payload["attributions"])

    def to_dict(self) -> dict[str, Any]:
        """Return a fresh complete envelope; no graph or original context is merged."""
        return deepcopy(self._payload)

    def to_json(self) -> str:
        """Serialize the complete bundle without filesystem/network side effects."""
        return json.dumps(self._payload, ensure_ascii=False, allow_nan=False, indent=2)

    def report(self, format: str = "workflow", **options: Any) -> str:
        """Export shared bibliography or report original uses/graphs per result.

        Workflow references have one shared numbering. Provenance stays scoped
        per input. Other registered formats receive shared bibliography and
        caller labels without a fabricated combined graph. JSON is bibliography,
        distinct from the complete envelope returned by :meth:`to_json`.
        """
        from ..formats import workflow
        from .report import _render_records, _resolve_format

        _name(format, "render attribution bundle format")
        canonical = _resolve_format(format)
        if canonical in {"workflow", "provenance"}:
            if options:
                _invalid("workflow and provenance bundle reports take no options")
            if canonical == "workflow":
                return workflow.render_bundle(
                    self._payload, list(self._records.values())
                )
            return "\n\n".join(
                f"Result {index}: {json.dumps(record['name'], ensure_ascii=False)}\n"
                + Attribution(record).report(format="provenance")
                for index, record in enumerate(self._payload["attributions"], 1)
            )

        used = {item_id: [] for item_id in self._records}
        for record in self._payload["attributions"]:
            for use in record["uses"]:
                caller = use["used_by"]
                if caller is not None and caller not in used[use["item_id"]]:
                    used[use["item_id"]].append(caller)
        return _render_records(canonical, used, self._records, {}, options)


@signal(tags=["ackredit", "composition"])
def compose_attributions(
    attributions: Iterable[Attribution],
    *,
    name: str = "composition",
    context: Mapping[str, Any] | None = None,
) -> AttributionBundle:
    """Compose original results offline, refusing any conflicting reference ID.

    Input records, current registry and session remain unchanged. Repeated
    records and names remain independent members; bibliography shares only
    identical records with identical IDs. Software releases need distinct IDs.
    """
    name = _name(name, "compose attribution name")
    context = _context(context, "compose attribution context")
    if not isinstance(attributions, Iterable) or isinstance(
        attributions, (str, bytes, Mapping)
    ):
        _invalid("composition needs an iterable of Attribution records")
    originals = []
    for attribution in attributions:
        if not isinstance(attribution, Attribution):
            _invalid("each composition input must be an Attribution record")
        originals.append(attribution.to_dict())
    return AttributionBundle(
        dict(schema=_SCHEMA, name=name, context=context, attributions=originals)
    )
