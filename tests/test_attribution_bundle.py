"""Independent saved results must not become an invented combined pipeline."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import (
    AckreditError,
    AttributionBundleError,
    AttributionConflictError,
)

FIXTURE = Path(__file__).parent / "data" / "attribution_v1_pyunitwizard.json"


def original(name="original", branch="first"):
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    data["name"] = name
    data["context"]["result"] = branch
    # Shared target labels across inputs must not create a left-to-second path.
    data["usage_tree"] = {
        branch: {"items": [], "children": ["shared"]},
        "shared": {"items": [], "children": [f"{branch}.leaf"]},
        f"{branch}.leaf": {"items": [data["items"][0]["id"]], "children": []},
    }
    return ackredit.Attribution(data)


def empty():
    return ackredit.Attribution(
        dict(
            schema="ackredit.attribution@1",
            name="empty",
            context={},
            items=[],
            uses=[],
            usage_tree={},
        )
    )


def test_complete_originals_reuse_empty_and_presentation_order_survive_round_trip():
    a, b = original("same name", "left"), original("same name", "right")
    originals = [a.to_dict(), b.to_dict(), a.to_dict(), empty().to_dict()]
    context = {"notebook": {"title": "μ analysis", "cells": [5, 2]}}
    bundle = ackredit.compose_attributions(
        (item for item in [a, b, a, empty()]), name="notebook", context=context
    )
    saved = bundle.to_dict()
    assert saved["attributions"] == originals
    assert saved["context"] == context
    context["notebook"]["cells"].clear()
    saved["attributions"][0]["items"].clear()
    assert bundle.to_dict()["attributions"] == originals
    assert (
        ackredit.AttributionBundle.from_json(bundle.to_json()).to_dict()
        == bundle.to_dict()
    )
    members = bundle.attributions
    assert tuple(item.to_dict() for item in members) == tuple(originals)
    members[0]._payload["usage_tree"].clear()
    assert bundle.to_dict()["attributions"] == originals
    assert a.to_dict() == originals[0] and b.to_dict() == originals[1]
    assert ackredit.get_used_items() == {}


def test_workflow_shares_numbered_references_and_keeps_graphs_independent():
    bundle = ackredit.compose_attributions(
        [original("one", "left"), original("two", "right")]
    )
    report = bundle.report()
    assert report.count("### Reference 1\n") == 1
    assert report.count("### Reference 2\n") == 1
    first, second = report.split("## Result 1: one", 1)[1].split("## Result 2: two", 1)
    assert "left.leaf" in first and "right.leaf" not in first
    assert "right.leaf" in second and "left.leaf" not in second
    assert "shared" in first and "shared" in second
    assert "software_description" in report.replace("\\_", "_")
    assert "0.27.0" in first and "0.27.0" in second
    assert "not execution chronology" in report
    for scope in (first, second):
        assert "Reference 2: unyt" in scope
    tree = bundle.report(format="provenance")
    first, second = tree.split('Result 1: "one"', 1)[1].split('Result 2: "two"', 1)
    assert "right.leaf" not in first and "left.leaf" not in second


def test_reordering_inputs_changes_presentation_but_not_shared_bibliography():
    a, b = original("one", "left"), original("two", "right")
    forward = ackredit.compose_attributions([a, b])
    reverse = ackredit.compose_attributions([b, a])
    for format in ("bibtex", "csl-json", "json", "markdown", "text"):
        assert forward.report(format=format) == reverse.report(format=format)
    assert reverse.attributions[0].to_dict() == b.to_dict()
    assert len(json.loads(forward.report(format="csl"))) == 2


def test_different_software_releases_remain_distinct_and_share_only_the_article():
    first = original()
    data = first.to_dict()
    data["items"][0]["id"] = "software:unyt:3.2.0"
    data["items"][0]["version"] = "3.2.0"
    for use in data["uses"]:
        if use["item_id"] == "software:unyt:3.1.0":
            use["item_id"] = "software:unyt:3.2.0"
        use["context"]["version"] = "3.2.0"
    for node in data["usage_tree"].values():
        node["items"] = [
            "software:unyt:3.2.0" if item == "software:unyt:3.1.0" else item
            for item in node["items"]
        ]
    combined = ackredit.compose_attributions([first, ackredit.Attribution(data)])
    exported = json.loads(combined.report(format="json"))
    assert {item["id"] for item in exported} == {
        "software:unyt:3.1.0",
        "software:unyt:3.2.0",
        "doi:10.21105/joss.00809",
    }
    assert {item["version"] for item in exported if item["type"] == "software"} == {
        "3.1.0",
        "3.2.0",
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "different work"),
        ("version", "new version"),
        ("extra", {"source": "other"}),
    ],
)
def test_conflicting_identity_refuses_entire_composition_and_preserves_originals(
    field, value
):
    first = original()
    conflicting = first.to_dict()
    conflicting["items"][0][field] = value
    second = ackredit.Attribution(conflicting)
    before = [first.to_dict(), second.to_dict()]
    with pytest.raises(AttributionConflictError) as caught:
        ackredit.compose_attributions([first, empty(), second])
    assert caught.value.code == "ACKREDIT-E011"
    assert [first.to_dict(), second.to_dict()] == before
    assert ackredit.get_used_items() == {}
    payload = dict(
        schema="ackredit.attribution_bundle@1",
        name="bad",
        context={},
        attributions=before,
    )
    with pytest.raises(AttributionConflictError):
        ackredit.AttributionBundle.from_dict(payload)


@pytest.mark.parametrize(
    "invalid",
    [None, 1, "file.json", {}, [None], [dict(schema="ackredit.attribution@1")]],
)
def test_composition_requires_explicit_attribution_objects(invalid):
    with pytest.raises(AttributionBundleError):
        ackredit.compose_attributions(invalid)


@pytest.mark.parametrize(
    "mutation",
    [
        "unknown_schema",
        "extra_field",
        "missing_field",
        "wrong_members",
        "invalid_member",
    ],
)
def test_bundle_reader_refuses_unknown_or_invalid_envelopes(mutation):
    data = ackredit.compose_attributions([original()]).to_dict()
    if mutation == "unknown_schema":
        data["schema"] = "ackredit.attribution_bundle@2"
    elif mutation == "extra_field":
        data["future"] = []
    elif mutation == "missing_field":
        del data["context"]
    elif mutation == "wrong_members":
        data["attributions"] = {}
    else:
        data["attributions"][0]["items"] = []
    with pytest.raises(AckreditError):
        ackredit.AttributionBundle.from_json(json.dumps(data))
    with pytest.raises(AckreditError):
        ackredit.AttributionBundle.from_json("{bad")


def test_empty_bundle_empty_member_and_shared_cyclic_graph_remain_distinct():
    assert json.loads(ackredit.compose_attributions([]).report(format="csl")) == []
    assert "No input attributions" in ackredit.compose_attributions([]).report()
    assert "## Result 1: empty" in ackredit.compose_attributions([empty()]).report()
    data = original().to_dict()
    data["usage_tree"]["first.leaf"]["children"] = ["shared"]
    data["usage_tree"]["other"] = {"items": [], "children": ["shared"]}
    result = ackredit.compose_attributions([ackredit.Attribution(data), empty()])
    assert result.attributions[0].to_dict()["usage_tree"] == data["usage_tree"]
    assert "first.leaf" in result.report()
    assert "other" in result.report()


def test_bundle_reports_ignore_conflicting_live_registry(clean_registry):
    bundle = ackredit.compose_attributions([original()])
    expected = bundle.report()
    ackredit.register_item(id="software:unyt:3.1.0", title="Today's unrelated metadata")
    ackredit.track_item("software:unyt:3.1.0", used_by="different workflow")
    before = ackredit.get_attribution().to_dict()
    assert bundle.report() == expected
    assert ackredit.get_attribution().to_dict() == before


def test_format_plugin_cannot_mutate_members_or_shared_bibliography(monkeypatch):
    import importlib

    formats = importlib.import_module("ackredit.core.report")
    monkeypatch.setattr(formats, "_RENDERERS", dict(formats._RENDERERS))

    def destructive(used, items):
        first = next(iter(items.values()))
        first["authors"].clear()
        used.clear()
        return "custom report"

    ackredit.register_format("bundle-detachment-test", destructive, "txt")
    bundle = ackredit.compose_attributions([original()])
    before = bundle.to_dict()
    assert bundle.report(format="bundle-detachment-test") == "custom report"
    assert bundle.to_dict() == before
    assert json.loads(bundle.report(format="json"))[0]["authors"]


def test_workflow_context_and_names_cannot_escape_markdown_fences():
    first = original("one\n# injected")
    data = first.to_dict()
    data["context"]["text"] = "```\n# external"
    composed = ackredit.compose_attributions(
        [ackredit.Attribution(data)], name="book\n# injected", context={"text": "```"}
    )
    report = composed.report()
    assert "\n# injected\n" not in report
    assert "````json" in report


def test_fresh_bundle_cli_reader_has_no_producer_network_or_recording(tmp_path):
    path = tmp_path / "results.json"
    path.write_text(
        ackredit.compose_attributions(
            [original("one", "left"), original("two", "right"), empty()]
        ).to_json(),
        encoding="utf-8",
    )
    before = path.read_bytes()
    script = """
import importlib.abc, socket, sys
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise AssertionError('producer imported: ' + fullname)
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('network or live observation')
socket.create_connection = socket.socket.connect = forbidden
import ackredit
from ackredit.core import registry, collector, session
original = ackredit.get_attribution().to_dict()
items = dict(registry.Registry.items)
registry.register_item = collector.aggregate = collector.track_item = session.read = forbidden
from ackredit.cli import main
sys.argv = ['ackredit', 'report', sys.argv[1], '--input-format', 'bundle', '-f', 'workflow']
assert main() == 0
assert ackredit.get_attribution().to_dict() == original
assert registry.Registry.items == items
"""
    run = subprocess.run(
        [sys.executable, "-c", script, str(path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 0, run.stderr
    assert "## Result 1: one" in run.stdout and "## Result 2: two" in run.stdout
    assert "3.1.0" in run.stdout and "0.27.0" in run.stdout
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "failure", ["conflict", "unknown_schema", "wrong_input", "unknown_format"]
)
def test_bundle_cli_failures_preserve_original_and_export(tmp_path, failure):
    data = ackredit.compose_attributions([original(), original()]).to_dict()
    if failure == "conflict":
        data["attributions"][1]["items"][0]["title"] = "conflict"
    elif failure == "unknown_schema":
        data["schema"] = "ackredit.attribution_bundle@2"
    elif failure == "wrong_input":
        data = original().to_dict()
    path = tmp_path / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    before = path.read_bytes()
    output = tmp_path / "output.bib"
    output.write_bytes(b"previous report")
    format = "unknown" if failure == "unknown_format" else "bibtex"
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "ackredit.cli",
            "report",
            str(path),
            "--input-format",
            "bundle",
            "-f",
            format,
            "-o",
            str(output),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 1
    assert run.stderr and run.stdout == ""
    assert output.read_bytes() == b"previous report" and path.read_bytes() == before
