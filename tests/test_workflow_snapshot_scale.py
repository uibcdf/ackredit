"""Enclosing snapshots preserve uses without repeatedly scanning them (#133)."""

from __future__ import annotations

from copy import deepcopy

import pytest

import ackredit


class CountedName(str):
    """Count public-name comparisons without a wall-clock threshold."""

    comparisons = 0
    __hash__ = str.__hash__

    def __eq__(self, other: object) -> bool:
        type(self).comparisons += 1
        return str.__eq__(self, other)


@pytest.mark.parametrize("layout", ["references", "callers"])
@pytest.mark.parametrize("mode", ["plain", "contextual", "mixed"])
def test_snapshot_name_comparisons_are_bounded_by_workflow_size(
    clean_registry: object, layout: str, mode: str
) -> None:
    size = 256
    with ackredit.session("large-workflow"):
        for index in range(size):
            item_id = CountedName(
                f"paper:{index}" if layout == "references" else "shared"
            )
            caller = CountedName(f"caller:{index}")
            options = (
                {"roles": ["method"], "context": {"version": "original"}}
                if mode == "contextual" or (mode == "mixed" and index >= size // 2)
                else {}
            )
            ackredit.track_item(item_id, used_by=caller, **options)
        CountedName.comparisons = 0

        snapshot = ackredit.get_attribution()

        comparisons = CountedName.comparisons
        assert comparisons <= 16 * size, (
            f"{size} uses required {comparisons} name comparisons; "
            "snapshot reconciliation must not rescan every earlier use"
        )
        data = snapshot.to_dict()
        assert len(data["uses"]) == size
        assert len(data["items"]) == (size if layout == "references" else 1)
        assert {use["used_by"] for use in data["uses"]} == {
            f"caller:{index}" for index in range(size)
        }


def test_mixed_snapshot_preserves_context_variants_original_records_and_legacy_order(
    clean_registry: object,
) -> None:
    ackredit.register_item(id="observed", title="Original observed", version="1")
    ackredit.register_item(id="legacy", title="Initial legacy", version="0")
    with ackredit.session("workflow"):
        ackredit.track_item("legacy", used_by="old-step")
        ackredit.track_item("unknown")
        context = {"version": "1", "options": ["first"]}
        for role in ("executed_software", "software_description"):
            ackredit.track_item(
                "observed", used_by="method", roles=[role], context=context
            )
        ackredit.track_target("method", parent="root")
        ackredit.register_item(id="observed", title="Replaced observed", version="2")
        ackredit.register_item(id="legacy", title="Current legacy", version="3")
        used_before = deepcopy(ackredit.get_used_items())
        tree_before = deepcopy(ackredit.current_session().usage_tree)

        result = ackredit.get_attribution()
        repeated = ackredit.get_attribution()

        assert result.to_dict() == repeated.to_dict()
        data = result.to_dict()
        assert [(use["item_id"], use["used_by"]) for use in data["uses"]] == [
            ("observed", "method"),
            ("observed", "method"),
            ("legacy", "old-step"),
            ("unknown", None),
        ]
        assert [use["roles"] for use in data["uses"]] == [
            ["executed_software"],
            ["software_description"],
            [],
            [],
        ]
        records = {item["id"]: item for item in data["items"]}
        assert records["observed"]["title"] == "Original observed"
        assert records["observed"]["version"] == "1"
        assert records["legacy"]["title"] == "Current legacy"
        assert records["legacy"]["version"] == "3"
        assert records["unknown"] == {"id": "unknown", "title": "unknown"}
        assert data["usage_tree"] == {
            name: {field: sorted(values) for field, values in node.items()}
            for name, node in tree_before.items()
        }
        context["options"].append("later")
        assert result.to_dict() == data
        assert ackredit.get_used_items() == used_before
        assert ackredit.current_session().usage_tree == tree_before
        with ackredit.session("independent"):
            assert ackredit.get_attribution().to_dict()["items"] == []
        assert ackredit.get_attribution().to_dict() == data
