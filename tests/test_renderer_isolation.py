"""Nested renderer inputs must not corrupt subsequent public bibliography (#90)."""

import json
from importlib import import_module

import pytest

import ackredit


@pytest.fixture
def renderer_registry(clean_registry, monkeypatch):
    reports = import_module("ackredit.core.report")
    monkeypatch.setattr(reports, "_RENDERERS", dict(reports._RENDERERS))
    original = {
        "id": "isolated:paper",
        "title": "Original paper",
        "authors": [{"family": "Original", "given": "Ada"}],
        "identifiers": [{"type": "doi", "value": "10.1/original"}],
    }
    ackredit.register_item(**original)
    ackredit.track_item(original["id"])
    return original


@pytest.mark.parametrize("fails", [False, True])
def test_nested_plugin_mutation_preserves_registered_bibliography(
    renderer_registry, fails
):
    original = renderer_registry

    def mutate(used, items):
        item = items[original["id"]]
        item["authors"][0]["family"] = "Changed"
        item["identifiers"].clear()
        if fails:
            raise RuntimeError("renderer failed after mutation")
        return "rendered"

    ackredit.register_format("nested-mutation", mutate, "txt")
    if fails:
        with pytest.raises(RuntimeError, match="renderer failed"):
            ackredit.report(format="nested-mutation")
    else:
        assert ackredit.report(format="nested-mutation") == "rendered"
    assert json.loads(ackredit.report(format="json"))[0]["authors"] == [
        {"family": "Original", "given": "Ada"}
    ]
    assert original["identifiers"] == [{"type": "doi", "value": "10.1/original"}]
    assert ackredit.get_attribution().to_dict()["items"][0]["authors"] == [
        {"family": "Original", "given": "Ada"}
    ]


def test_nested_plugin_mutation_preserves_saved_attribution(renderer_registry):
    saved = ackredit.get_attribution()
    before = saved.to_dict()

    def mutate(used, items):
        items["isolated:paper"]["authors"].clear()
        return "rendered"

    ackredit.register_format("saved-mutation", mutate, "txt")
    assert saved.report(format="saved-mutation") == "rendered"
    assert saved.to_dict() == before


def test_builtin_bibliography_does_not_copy_unused_metadata(renderer_registry):
    class UnusedMetadata:
        def __deepcopy__(self, memo):
            raise AssertionError("unused record was copied")

    ackredit.register_item(id="unused:metadata", title="Unused", extra=UnusedMetadata())
    assert "Original paper" in ackredit.report(format="markdown")
