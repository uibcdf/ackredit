"""Unrecorded scope/origin/gaps must not become reassuring invented evidence."""

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import AttributionError

FIXTURE = Path(__file__).parent / "data" / "attribution_v1_pyunitwizard.json"


def saved(**overrides):
    payload = {
        "schema": "ackredit.attribution@1",
        "name": "result",
        "context": {},
        "items": [],
        "uses": [],
        "usage_tree": {},
    }
    payload.update(overrides)
    return ackredit.Attribution(payload)


def test_empty_capture_explains_unknown_coverage_and_recording_outcome():
    original = saved()
    view = ackredit.explain_attribution(original)
    assert view["schema"] == "ackredit.attribution_explanation@1"
    assert view["source_schema"] == "ackredit.attribution@1"
    assert view["counts"] == {"input_records": 1, "shared_references": 0}
    result = view["results"][0]
    assert result["counts"] == {
        "references": 0,
        "recorded_use_records": 0,
        "distinct_recorded_uses": 0,
        "recorded_graph_targets": 0,
        "unscoped_uses": 0,
    }
    assert result["instrumentation_scope"] == "not_recorded"
    assert result["diagnosed_recording_gaps"] == "not_recorded"
    rendered = original.report("explanation")
    assert "No recorded references does not prove" in rendered
    assert "not evidence that recording was complete or successful" in rendered
    assert "100%" not in rendered and "0%" not in rendered


def test_fields_describe_presence_not_validity_mandatory_citations_or_origin():
    original = saved(
        items=[
            {"id": "identifier-only"},
            {"id": "engine", "type": "software", "title": None, "authors": []},
            {
                "id": "paper",
                "type": "article",
                "title": "Paper",
                "authors": ["A"],
                "doi": "10.test/original",
                "url": "https://example.invalid",
                "origin": "verified",
                "instrumentation_scope": "complete",
            },
        ],
        context={"scope": "complete", "diagnosed_recording_gaps": [], "success": True},
    )
    view = ackredit.explain_attribution(original)
    result = view["results"][0]
    first, engine, paper = result["references"]
    assert first["fields_absent"] == ["type", "title", "authors"]
    assert engine["fields_absent"] == ["version"]
    assert paper["fields_absent"] == []
    assert "doi" in paper["metadata_fields"]
    assert all(r["metadata_origin"] == "not_recorded" for r in result["references"])
    assert result["instrumentation_scope"] == "not_recorded"
    assert result["diagnosed_recording_gaps"] == "not_recorded"
    assert result["context"] == original.to_dict()["context"]
    rendered = original.report("explanation")
    assert "This does not establish that they were unused" in rendered
    assert "not mandatory citation requirements" in rendered


def test_distinct_contextual_evidence_retains_unscoped_and_entry_roles():
    use = {
        "item_id": "engine",
        "used_by": "convert",
        "roles": ["function_entry"],
        "context": {"version": "1.2", "backend": "first"},
    }
    later = deepcopy(use)
    later["context"]["backend"] = "second"
    unscoped = {"item_id": "paper", "used_by": None, "roles": [], "context": {}}
    original = saved(
        items=[{"id": "engine", "type": "software", "version": "1.2"}, {"id": "paper"}],
        uses=[use, deepcopy(use), later, unscoped],
        usage_tree={
            "pipeline": {"items": [], "children": ["convert"]},
            "convert": {"items": ["engine"], "children": []},
        },
    )
    result = ackredit.explain_attribution(original)["results"][0]
    assert result["counts"]["recorded_use_records"] == 4
    assert result["counts"]["distinct_recorded_uses"] == 3
    assert result["counts"]["unscoped_uses"] == 1
    assert result["references"][0]["roles"] == ["function_entry"]
    assert result["references"][0]["version"] == "1.2"
    assert result["references"][0]["used_by"] == ["convert"]
    assert result["references"][1]["used_by"] == []
    assert result["graph_targets_without_direct_references"] == ["pipeline"]
    assert "these are not diagnosed gaps" in original.report("explanation")
    assert "executed_software" not in original.report("explanation")


def test_cycles_shared_edges_and_software_versions_are_not_interpreted_as_execution():
    original = saved(
        items=[
            {"id": "software:engine:1", "type": "software", "version": "1"},
            {"id": "software:engine:2", "type": "software", "version": "2"},
        ],
        usage_tree={
            "a": {"items": [], "children": ["b", "leaf"]},
            "b": {"items": [], "children": ["a", "leaf"]},
            "leaf": {
                "items": ["software:engine:1", "software:engine:2"],
                "children": [],
            },
        },
    )
    before = original.to_dict()
    result = ackredit.explain_attribution(original)["results"][0]
    assert result["counts"]["recorded_graph_targets"] == 3
    assert result["counts"]["distinct_recorded_uses"] == 0
    assert [r["version"] for r in result["references"]] == ["1", "2"]
    assert result["graph_targets_without_direct_references"] == ["a", "b"]
    assert '"1"' in original.report("explanation")
    assert '"2"' in original.report("explanation")
    assert original.to_dict() == before


def test_result_order_reuse_and_shared_targets_keep_independent_evidence():
    a = saved(
        name="same",
        context={"cell": 1},
        items=[{"id": "same-id"}],
        usage_tree={"shared": {"items": [], "children": []}},
    )
    b = saved(
        name="same",
        context={"cell": 2},
        items=[{"id": "same-id"}],
        uses=[
            {
                "item_id": "same-id",
                "used_by": "shared",
                "roles": ["executed_software"],
                "context": {},
            }
        ],
        usage_tree={"shared": {"items": ["same-id"], "children": []}},
    )
    bundle = ackredit.compose_attributions([a, b, a, saved()])
    view = ackredit.explain_attribution(bundle)
    assert view["source_schema"] == "ackredit.attribution_bundle@1"
    assert view["counts"] == {"input_records": 4, "shared_references": 1}
    assert [r["counts"]["distinct_recorded_uses"] for r in view["results"]] == [
        0,
        1,
        0,
        0,
    ]
    assert view["results"][0] == view["results"][2]
    assert view["results"][0]["context"] != view["results"][1]["context"]
    reversed_view = ackredit.explain_attribution(ackredit.compose_attributions([b, a]))
    assert reversed_view["results"] == [view["results"][1], view["results"][0]]
    rendered = bundle.report("explanation")
    assert "## Result 1: same" in rendered and "## Result 2: same" in rendered
    assert "## Result 4: result" in rendered
    assert "chronology" in rendered and "complete instrumentation" in rendered
    empty = ackredit.explain_attribution(ackredit.compose_attributions([]))
    assert empty["results"] == [] and empty["counts"]["input_records"] == 0


def test_live_snapshot_and_saved_view_ignore_changed_reader_registry(clean_registry):
    ackredit.register_item(id="engine", type="software", title="Original", version="1")
    with ackredit.capture("calculation") as run:
        ackredit.track_item("engine", used_by="calculate", roles=["executed_software"])
    original = run.attribution
    before = original.to_dict()
    live_before = ackredit.get_attribution().to_dict()
    baseline = original.report("explanation")
    clean_registry.items["engine"] = {"id": "engine", "type": "article", "title": "New"}
    assert original.report("explanation") == baseline
    assert original.to_dict() == before
    assert ackredit.get_used_items() == {"engine": ["calculate"]}
    assert ackredit.report("explanation").startswith("# Attribution explanation")
    # Rendering does not credit another calculation or replace the graph.
    assert ackredit.get_attribution().to_dict()["uses"] == live_before["uses"]


def test_mutating_the_view_cannot_change_originals_or_later_views():
    original = saved(context={"nested": [1]}, items=[{"id": "x"}])
    before = original.to_dict()
    view = ackredit.explain_attribution(original)
    pristine = deepcopy(view)
    view["results"][0]["context"]["nested"].append(2)
    view["results"][0]["references"][0]["fields_absent"].clear()
    view["limits"].clear()
    assert original.to_dict() == before
    assert ackredit.explain_attribution(original) == pristine
    assert ackredit.get_used_items() == {}


@pytest.mark.parametrize("value", [None, {}, [], "saved", 2])
def test_unvalidated_inputs_are_refused_with_the_existing_catalog(value):
    with pytest.raises(AttributionError) as raised:
        ackredit.explain_attribution(value)
    assert raised.value.code == "ACKREDIT-E010"


@pytest.mark.parametrize("bundle", [False, True])
def test_unknown_report_options_are_refused(bundle):
    original = ackredit.compose_attributions([saved()]) if bundle else saved()
    with pytest.raises(ValueError) as raised:
        original.report("explanation", complete=True)
    assert raised.value.code == ("ACKREDIT-E015" if bundle else "ACKREDIT-E010")


def test_hostile_external_text_cannot_break_headings_or_report_tables():
    name = "name\n<script>alert(1)</script>"
    item_id = "id|row\n```"
    original = saved(
        name=name,
        items=[{"id": item_id}],
        uses=[
            {
                "item_id": item_id,
                "used_by": "a|b\nline",
                "roles": ["role|x"],
                "context": {},
            }
        ],
    )
    report = original.report("explanation")
    assert "<script>" not in report and "\n<script>" not in report
    assert "id\\|row" in report and "a\\|b line" in report
    assert "\n```" not in report
    assert original.to_dict()["name"] == name


@pytest.mark.parametrize("bundle", [False, True])
def test_fresh_saved_cli_explanation_has_no_producer_network_or_new_credit(
    tmp_path, bundle
):
    original = ackredit.Attribution.from_json(FIXTURE.read_text())
    if bundle:
        original = ackredit.compose_attributions([original, original, saved()])
    path = tmp_path / "saved.json"
    path.write_text(original.to_json())
    before = path.read_bytes()
    script = """
import importlib.abc, socket, sys
sys.path.insert(0, sys.argv[3])
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise AssertionError('producer import')
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('network or observation')
socket.create_connection = socket.socket.connect = forbidden
import ackredit
from ackredit.core import registry, collector, session
before = ackredit.get_attribution().to_dict()
items = dict(registry.Registry.items)
registry.register_item = collector.track_item = collector.aggregate = session.read = forbidden
from ackredit.cli import main
sys.argv = ['ackredit', 'report', sys.argv[1], '--input-format', sys.argv[2], '-f', 'explanation']
assert main() == 0
assert ackredit.get_attribution().to_dict() == before
assert registry.Registry.items == items
assert not {'pyunitwizard', 'pint', 'unyt'} & sys.modules.keys()
"""
    run = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(path),
            "bundle" if bundle else "attribution",
            str(Path(ackredit.__file__).parents[1]),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout == original.report("explanation") + "\n"
    assert "software\\_description" in run.stdout
    assert path.read_bytes() == before


def test_descriptive_view_is_not_a_replacement_attribution_payload():
    view = ackredit.explain_attribution(saved())
    with pytest.raises(AttributionError):
        ackredit.Attribution.from_json(json.dumps(view))


def test_explanation_dump_keeps_existing_workflow_and_bibliography(
    tmp_path, clean_registry
):
    ackredit.track_item("legacy")
    ackredit.dump(tmp_path, formats=["markdown", "workflow", "explanation"])
    assert (
        (tmp_path / "ackredit_report_explanation.md")
        .read_text()
        .startswith("# Attribution explanation")
    )
    assert (
        (tmp_path / "ackredit_report_workflow.md")
        .read_text()
        .startswith("# Workflow attribution")
    )
    assert (tmp_path / "ackredit_report_markdown.md").is_file()
