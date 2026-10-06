"""Explicit workflow evidence stays readable, positional and inert (#106)."""

import re
import subprocess
import sys
import warnings
from copy import deepcopy

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import AttributionEvidenceError
from ackredit.formats._markdown import escape


def original(*, empty=False):
    items = [
        {
            "id": "software:engine:1",
            "type": "software",
            "title": "Original engine",
            "version": "1",
        },
        {
            "id": "paper:engine",
            "type": "article",
            "title": "Original article",
            "year": 2020,
        },
    ]
    return ackredit.Attribution.from_dict(
        {
            "schema": "ackredit.attribution@1",
            "name": "same name",
            "context": {"step": "conversion"},
            "items": [] if empty else items,
            "uses": []
            if empty
            else [
                {
                    "item_id": item["id"],
                    "used_by": "engine.convert",
                    "roles": [role],
                    "context": {},
                }
                for item, role in zip(
                    items, ("executed_software", "software_description")
                )
            ],
            "usage_tree": {}
            if empty
            else {
                "workflow": {"items": [], "children": ["engine.convert"]},
                "engine.convert": {
                    "items": [item["id"] for item in items],
                    "children": [],
                },
            },
        }
    )


def declarations():
    return {
        "metadata_origins": [
            {
                "item_id": "software:engine:1",
                "fields": ["title"],
                "method": "citation_file",
                "source": "initial/CITATION.cff",
                "recorder": "original:1",
            },
            {
                "item_id": "software:engine:1",
                "fields": ["version"],
                "method": "provider_declaration",
                "source": "engine.__ackredit__.items",
                "recorder": "original:1",
            },
        ],
        "observation_scope": [
            {
                "boundary": boundary,
                "mechanism": "provider_observer",
                "status": status,
                "recorder": "original:1",
            }
            for boundary, status in (
                ("engine.convert", "selected"),
                ("engine.generator", "unsupported"),
                ("saved_alias", "unobserved"),
            )
        ],
        "recording_gaps": [
            {
                "boundary": "engine.convert",
                "diagnostic_owner": "example",
                "diagnostic_code": "EXAMPLE-W001",
                "recorder": "original:1",
            }
        ],
    }


def companion():
    return ackredit.AttributionEvidence.from_attribution(
        original(), results=[declarations()]
    )


def test_single_report_joins_original_bibliography_roles_graph_and_bounded_facts():
    evidence = companion()
    before = evidence.to_dict()
    with warnings.catch_warnings(record=True) as emitted:
        report = evidence.report("workflow", include_evidence=True)
    assert emitted == []
    assert "Original engine" in report and "Original article" in report
    assert "Version: 1" in report and "2020" in report
    assert escape("executed_software") in report
    assert escape("software_description") in report
    assert "engine.convert" in report and "workflow" in report
    assert (
        '| 1 | \\["title"\\] | Citation file | initial/CITATION.cff | original:1 |'
        in report
    )
    assert "Provider declaration" in report
    assert "References with no metadata-source declaration: 2." in report
    assert "selected" in report and "unsupported" in report and "unobserved" in report
    assert "EXAMPLE-W001" in report and "example" in report
    assert "Selected boundaries do not establish that a function ran" in report
    assert "Other field origins remain unknown" in report
    assert "absence of failures" in report and "not emitted again" in report
    assert "call counts" in report and "complete instrumentation" in report
    assert evidence.to_dict() == before
    assert evidence.report("workflow") == original().report("workflow")
    assert evidence.report("workflow", include_evidence=False) == original().report(
        "workflow"
    )


def test_bundle_numbers_shared_references_once_and_keeps_occurrence_declarations():
    source = original()
    bundle = ackredit.compose_attributions([source, source, original(empty=True)])
    second = declarations()
    second["recording_gaps"][0]["diagnostic_code"] = "EXAMPLE-W002"
    evidence = ackredit.AttributionEvidence.from_attribution(
        bundle, results=[declarations(), second, dict.fromkeys(declarations())]
    )
    report = evidence.report("workflow", include_evidence=True)
    assert report.count("### Reference 1\n") == report.count("### Reference 2\n") == 1
    first, second, third = report.split("## Result ")[1:]
    assert "EXAMPLE-W001" in first and "EXAMPLE-W002" not in first
    assert "EXAMPLE-W002" in second and "EXAMPLE-W001" not in second
    assert "EXAMPLE-W001" not in third and "Not recorded." in third
    assert report.count("#### Recorded graph") == 3
    assert first.count("engine.convert") == second.count("engine.convert")
    assert evidence.attribution.to_dict() == bundle.to_dict()
    assert evidence.report("workflow") == bundle.report()
    empty = ackredit.AttributionEvidence.from_attribution(
        ackredit.compose_attributions([])
    )
    assert "No input attributions were supplied." in empty.report(
        "workflow", include_evidence=True
    )


@pytest.mark.parametrize("empty_result", [False, True])
def test_unknown_empty_and_gap_only_planes_remain_distinct(empty_result):
    source = original(empty=empty_result)
    unknown = ackredit.AttributionEvidence.from_attribution(source)
    empty = ackredit.AttributionEvidence.from_attribution(
        source, results=[{p: [] for p in declarations()}]
    )
    partial = dict.fromkeys(declarations())
    partial["recording_gaps"] = declarations()["recording_gaps"]
    gap_only = ackredit.AttributionEvidence.from_attribution(source, results=[partial])
    unknown_report = unknown.report("workflow", include_evidence=True)
    empty_report = empty.report("workflow", include_evidence=True)
    partial_report = gap_only.report("workflow", include_evidence=True)
    assert "Metadata origins: Not recorded." in unknown_report
    assert "No metadata-source declarations supplied" in empty_report
    assert unknown_report != empty_report
    assert "EXAMPLE-W001" in partial_report
    assert "Metadata origins: Not recorded." in partial_report
    assert "absence of failures" in empty_report
    if empty_result:
        assert "No references were recorded." in partial_report
    assert gap_only.attribution.to_dict() == source.to_dict()


def test_repeated_sources_are_retained_without_winners_or_chronology():
    facts = declarations()
    facts["metadata_origins"].append(deepcopy(facts["metadata_origins"][0]))
    report = ackredit.AttributionEvidence.from_attribution(
        original(), results=[facts]
    ).report("workflow", include_evidence=True)
    assert report.count("initial/CITATION.cff") == 2
    assert "engine." in report
    assert "chronology" in report


def test_untrusted_declarations_cannot_break_tables_links_or_html():
    facts = declarations()
    hostile = "<script>|[click](javascript:bad)\n```\n# injected"
    facts["metadata_origins"][0]["source"] = hostile
    facts["observation_scope"][0]["boundary"] = hostile
    facts["recording_gaps"][0]["diagnostic_owner"] = hostile
    report = ackredit.AttributionEvidence.from_attribution(
        original(), results=[facts]
    ).report("workflow", include_evidence=True)
    assert "<script>" not in report and "[click](javascript:bad)" not in report
    assert "\n# injected" not in report
    assert "\\|" in report and "\\`\\`\\`" in report
    assert all(
        len(re.findall(r"(?<!\\)\|", line)) == 6
        for line in report.splitlines()
        if line.startswith("| 1 |")
    )


@pytest.mark.parametrize("value", [None, 1, "yes", [], {}])
def test_include_evidence_requires_boolean(value):
    with pytest.raises(AttributionEvidenceError) as raised:
        companion().report("workflow", include_evidence=value)
    assert raised.value.code == "ACKREDIT-E016"


@pytest.mark.parametrize(
    "format", ["explanation", "markdown", "bibtex", "json", "provenance"]
)
def test_only_workflow_can_request_integrated_evidence(format):
    with pytest.raises(AttributionEvidenceError):
        companion().report(format, include_evidence=True)


def test_integrated_report_rejects_other_options():
    with pytest.raises(AttributionEvidenceError):
        companion().report("workflow", include_evidence=True, invented=True)


@pytest.mark.parametrize(
    "input_format,format",
    [
        ("session", "workflow"),
        ("attribution", "workflow"),
        ("bundle", "workflow"),
        ("evidence", "text"),
    ],
)
def test_cli_refuses_invalid_combination_before_loading_input(
    monkeypatch, tmp_path, input_format, format
):
    from ackredit import cli

    def forbidden(*args, **kwargs):
        raise AssertionError("invalid options read or aggregate input")

    monkeypatch.setattr(cli, "_load", forbidden)
    monkeypatch.setattr(cli, "_attribution_report", forbidden)
    path = tmp_path / "does-not-exist.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ackredit",
            "report",
            str(path),
            "--input-format",
            input_format,
            "-f",
            format,
            "--include-evidence",
        ],
    )
    assert cli.main() == 1
    assert not path.exists()


def test_fresh_cli_and_library_keep_offline_inert_original_input(tmp_path):
    evidence = companion()
    path = tmp_path / "saved.json"
    path.write_text(evidence.to_json())
    baseline = path.read_bytes()
    output = tmp_path / "report.md"
    program = """
import importlib.abc, pathlib, socket, sys, warnings
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'engine','pyunitwizard','pint','unyt'}:
            raise AssertionError('producer import')
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('network or recording')
socket.socket.connect = socket.create_connection = forbidden
import ackredit
from ackredit.core import registry, collector, session
from ackredit.cli import main
before = ackredit.get_attribution().to_dict()
items = dict(registry.Registry.items)
registry.register_item = collector.track_item = collector.aggregate = session.read = forbidden
path, output = map(pathlib.Path, sys.argv[1:])
payload = path.read_bytes()
with warnings.catch_warnings(record=True) as emitted:
    saved = ackredit.AttributionEvidence.from_json(payload.decode())
    expected = saved.report('workflow', include_evidence=True)
    sys.argv = ['ackredit','report',str(path),'--input-format','evidence','-f','workflow','--include-evidence','-o',str(output)]
    assert main() == 0
    assert output.read_text() == expected
    sys.argv[-1] = str(path)
    assert main() == 1
assert emitted == []
assert path.read_bytes() == payload
assert ackredit.get_attribution().to_dict() == before and registry.Registry.items == items
assert not {'engine','pyunitwizard','pint','unyt'} & sys.modules.keys()
"""
    run = subprocess.run(
        [sys.executable, "-c", program, str(path), str(output)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert path.read_bytes() == baseline
    assert output.read_text() == evidence.report("workflow", include_evidence=True)
