"""Explicit declarations retain bounds without rewriting original use evidence."""

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import (
    AttributionError,
    AttributionEvidenceError,
)

FIXTURE = Path(__file__).parent / "data" / "attribution_v1_pyunitwizard.json"
HOSTED_FIXTURE = (
    Path(__file__).parent / "data" / "attribution_evidence_v1_pyunitwizard.json"
)


def test_original_hosted_companion_keeps_versions_occurrences_and_report_defaults():
    """Read original #106 bytes, rather than regenerating input with this reader."""
    content = HOSTED_FIXTURE.read_bytes()
    assert hashlib.sha256(content).hexdigest() == (
        "25c2807ba903d3136d8a4469012837a9b3b74bd9d09b9702e9ab27641fee7b67"
    )
    payload = json.loads(content)
    saved = ackredit.AttributionEvidence.from_json(content.decode())
    assert saved.to_dict() == payload
    originals = saved.attribution.attributions
    assert [item.to_dict()["name"] for item in originals] == [
        "first",
        "reused",
        "recording fault",
        "selected but unused",
    ]
    facts = saved.to_dict()["results"]
    assert facts[0]["metadata_origins"] == facts[1]["metadata_origins"]
    assert facts[2]["metadata_origins"] is None
    assert facts[2]["recording_gaps"][0]["diagnostic_code"] == "ACKREDIT-W019"
    assert originals[3].to_dict()["items"] == []
    assert facts[3]["observation_scope"] and facts[3]["recording_gaps"] is None
    assert all(
        record["recorder"] == "ackredit:0.10.1+20.g9ca7157:observe_calls"
        for result in facts
        for records in result.values()
        for record in records or []
    )
    assert saved.report("workflow") == saved.attribution.report("workflow")
    assert hashlib.sha256(saved.report("workflow").encode()).hexdigest() == (
        "0c845c63908c05e8bbe1e9539c7146fd7fe050489a3bf6f3a8b4d3f9eaf559bb"
    )
    assert hashlib.sha256(
        saved.report("workflow", include_evidence=True).encode()
    ).hexdigest() == (
        "4d27d18ea4754fe4c942832ab36de6ce7bad95caa41b9ab5e794151b48155352"
    )


def test_original_hosted_companion_fresh_reader_is_offline_and_does_not_replay(
    tmp_path,
):
    source = tmp_path / "original.json"
    source.write_bytes(HOSTED_FIXTURE.read_bytes())
    program = """
import importlib.abc, json, pathlib, socket, sys, warnings
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise AssertionError('producer import during original saved reading')
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('network or new recording during saved reading')
socket.socket.connect = socket.create_connection = forbidden
import ackredit
from ackredit.core import registry, collector, session
from ackredit.cli import main
before = ackredit.get_attribution().to_dict()
items = dict(registry.Registry.items)
registry.register_item = collector.track_item = collector.aggregate = session.read = forbidden
source = pathlib.Path(sys.argv[1])
content = source.read_bytes()
with warnings.catch_warnings(record=True) as emitted:
    saved = ackredit.AttributionEvidence.from_json(content.decode())
    assert saved.to_dict() == json.loads(content)
    expected = saved.report('workflow', include_evidence=True)
    assert saved.report('workflow') == saved.attribution.report('workflow')
    sys.argv = ['ackredit', 'report', str(source), '--input-format', 'evidence',
                '-f', 'workflow', '--include-evidence']
    assert main() == 0
assert emitted == []
assert source.read_bytes() == content
assert ackredit.get_attribution().to_dict() == before
assert registry.Registry.items == items
assert not {'pyunitwizard', 'pint', 'unyt'} & sys.modules.keys()
"""
    run = subprocess.run(
        [sys.executable, "-c", program, str(source)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    saved = ackredit.AttributionEvidence.from_json(HOSTED_FIXTURE.read_text())
    assert run.stdout == saved.report("workflow", include_evidence=True) + "\n"
    assert source.read_bytes() == HOSTED_FIXTURE.read_bytes()


def original():
    return ackredit.Attribution.from_json(FIXTURE.read_text())


def declarations():
    item = original().to_dict()["items"][0]
    return {
        "metadata_origins": [
            {
                "item_id": item["id"],
                "fields": ["title"],
                "method": "citation_file",
                "source": "producer/CITATION.cff",
                "recorder": "producer:1.2",
            },
            {
                "item_id": item["id"],
                "fields": ["id"],
                "method": "fallback",
                "source": "host:identifier fallback",
                "recorder": "host:1",
            },
        ],
        "observation_scope": [
            {
                "boundary": "producer.convert",
                "mechanism": "provider_observer",
                "status": "selected",
                "recorder": "host:1",
            },
            {
                "boundary": "producer.generator",
                "mechanism": "provider_observer",
                "status": "unsupported",
                "recorder": "host:1",
            },
            {
                "boundary": "saved_alias",
                "mechanism": "host_integration",
                "status": "unobserved",
                "recorder": "host:1",
            },
        ],
        "recording_gaps": [
            {
                "boundary": "producer.convert",
                "diagnostic_owner": "producer",
                "diagnostic_code": "PRODUCER-W001",
                "recorder": "host:1",
            }
        ],
    }


def test_round_trip_preserves_sources_scope_and_failure_without_new_uses():
    source = original()
    baseline = source.to_dict()
    declared = declarations()
    evidence = ackredit.AttributionEvidence.from_attribution(source, results=[declared])
    restored = ackredit.AttributionEvidence.from_json(evidence.to_json())
    assert restored.to_dict() == evidence.to_dict()
    assert restored.attribution.to_dict() == baseline == source.to_dict()
    assert restored.to_dict()["schema"] == "ackredit.attribution_evidence@1"
    view = restored.explain()
    assert view["schema"] == "ackredit.attribution_evidence_explanation@1"
    assert view["attribution"] == ackredit.explain_attribution(source)
    assert view["results"] == [declared]
    assert view["attribution"]["results"][0]["instrumentation_scope"] == "not_recorded"
    assert ackredit.get_used_items() == {}
    assert "citation correctness" in " ".join(view["limits"])
    assert "function ran" in " ".join(view["limits"])
    assert "PRODUCER-W001" in restored.report()
    assert "unsupported" in restored.report() and "unobserved" in restored.report()


def test_unknown_empty_and_partial_planes_never_establish_completeness():
    source = original()
    unknown = ackredit.AttributionEvidence.from_attribution(source)
    assert unknown.to_dict()["results"] == [dict.fromkeys(declarations())]
    empty = {plane: [] for plane in declarations()}
    empty_evidence = ackredit.AttributionEvidence.from_attribution(
        source, results=[empty]
    )
    partial = deepcopy(empty)
    partial["observation_scope"] = None
    partial["recording_gaps"] = declarations()["recording_gaps"]
    partial_evidence = ackredit.AttributionEvidence.from_attribution(
        source, results=[partial]
    )
    assert unknown.to_dict() != empty_evidence.to_dict() != partial_evidence.to_dict()
    assert "Not recorded." in unknown.report()
    assert "No declarations supplied" in empty_evidence.report()
    assert "PRODUCER-W001" in partial_evidence.report()
    assert "absence of failures" in empty_evidence.report()
    assert partial_evidence.attribution.to_dict() == source.to_dict()


def test_reused_names_empty_members_and_order_keep_separate_declarations():
    source = original()
    empty = ackredit.Attribution(
        {
            "schema": "ackredit.attribution@1",
            "name": source.to_dict()["name"],
            "context": {},
            "items": [],
            "uses": [],
            "usage_tree": {},
        }
    )
    bundle = ackredit.compose_attributions([source, source, empty])
    first = declarations()
    second = dict.fromkeys(first)
    third = {plane: [] for plane in first}
    evidence = ackredit.AttributionEvidence.from_attribution(
        bundle, results=[first, second, third]
    )
    assert evidence.to_dict()["results"] == [first, second, third]
    assert evidence.attribution.to_dict() == bundle.to_dict()
    assert evidence.explain()["attribution"]["counts"]["input_records"] == 3
    assert "Evidence for result 3" in evidence.report()
    reordered = ackredit.AttributionEvidence.from_attribution(
        ackredit.compose_attributions([empty, source, source]),
        results=[third, second, first],
    )
    assert reordered.explain()["results"] == [third, second, first]
    empty_bundle = ackredit.AttributionEvidence.from_attribution(
        ackredit.compose_attributions([])
    )
    assert empty_bundle.to_dict()["results"] == []


def test_multiple_field_sources_do_not_credit_a_reference_or_invent_chronology():
    source = original()
    declaration = declarations()
    declaration["metadata_origins"].append(deepcopy(declaration["metadata_origins"][0]))
    evidence = ackredit.AttributionEvidence.from_attribution(
        source, results=[declaration]
    )
    assert len(evidence.explain()["results"][0]["metadata_origins"]) == 3
    assert evidence.explain()["attribution"] == ackredit.explain_attribution(source)
    assert ackredit.get_used_items() == {}


def test_payload_properties_and_explanation_are_deeply_detached():
    source = original()
    declaration = declarations()
    evidence = ackredit.AttributionEvidence.from_attribution(
        source, results=[declaration]
    )
    baseline = evidence.to_dict()
    declaration["metadata_origins"][0]["fields"].clear()
    evidence.to_dict()["attribution"]["items"].clear()
    evidence.explain()["results"][0]["observation_scope"].clear()
    evidence.attribution._payload["context"]["new"] = True
    assert evidence.to_dict() == baseline
    assert source.to_dict() == baseline["attribution"]


@pytest.mark.parametrize(
    "format", ["workflow", "markdown", "bibtex", "json", "provenance"]
)
@pytest.mark.parametrize("bundle", [False, True])
def test_existing_report_formats_are_identical_to_originals(format, bundle):
    source = original()
    if bundle:
        source = ackredit.compose_attributions([source, source])
    evidence = ackredit.AttributionEvidence.from_attribution(source)
    assert evidence.report(format) == source.report(format)


def test_existing_readers_do_not_silently_accept_new_contract():
    evidence = ackredit.AttributionEvidence.from_attribution(original())
    with pytest.raises(AttributionError):
        ackredit.Attribution.from_dict(evidence.to_dict())
    with pytest.raises(AttributionError):
        ackredit.explain_attribution(evidence)


@pytest.mark.parametrize(
    "case",
    [
        "schema",
        "extra",
        "missing_plane",
        "short",
        "long",
        "plane_scalar",
        "record_extra",
        "item_missing",
        "field_missing",
        "field_duplicate",
        "field_empty",
        "field_scalar",
        "field_nonstring",
        "method",
        "mechanism",
        "status",
        "recorder",
        "code",
        "boundary",
    ],
)
def test_invalid_or_dangling_declarations_are_catalog_refused(case):
    payload = ackredit.AttributionEvidence.from_attribution(
        original(), results=[declarations()]
    ).to_dict()
    result = payload["results"][0]
    origin = result["metadata_origins"][0]
    scope = result["observation_scope"][0]
    gap = result["recording_gaps"][0]
    if case == "schema":
        payload["schema"] = "ackredit.attribution_evidence@2"
    elif case == "extra":
        payload["verified"] = True
    elif case == "missing_plane":
        del result["recording_gaps"]
    elif case == "short":
        payload["results"] = []
    elif case == "long":
        payload["results"].append(deepcopy(result))
    elif case == "plane_scalar":
        result["metadata_origins"] = "not_recorded"
    elif case == "record_extra":
        gap["science_success"] = True
    elif case == "item_missing":
        origin["item_id"] = "absent"
    elif case.startswith("field_"):
        origin["fields"] = {
            "field_missing": ["absent"],
            "field_duplicate": ["title", "title"],
            "field_empty": [],
            "field_scalar": "title",
            "field_nonstring": [None],
        }[case]
    elif case == "method":
        origin["method"] = "verified"
    elif case == "mechanism":
        scope["mechanism"] = "all_calls"
    elif case == "status":
        scope["status"] = "complete"
    elif case == "recorder":
        origin["recorder"] = " "
    elif case == "code":
        gap["diagnostic_code"] = None
    elif case == "boundary":
        gap["boundary"] = ""
    with pytest.raises(AttributionEvidenceError) as raised:
        ackredit.AttributionEvidence.from_dict(payload)
    assert raised.value.code == "ACKREDIT-E016"


@pytest.mark.parametrize("value", [None, [], "saved", 2, {}, {"schema": "unknown"}])
def test_unvalidated_inputs_are_refused(value):
    with pytest.raises(AttributionEvidenceError):
        ackredit.AttributionEvidence.from_attribution(value)
    with pytest.raises(AttributionEvidenceError):
        ackredit.AttributionEvidence.from_dict(value)


@pytest.mark.parametrize("content", ["{", "null", "[]"])
def test_invalid_json_is_refused(content):
    with pytest.raises(AttributionEvidenceError):
        ackredit.AttributionEvidence.from_json(content)


def test_explanation_options_and_hostile_external_strings():
    declared = declarations()
    declared["metadata_origins"][0]["source"] = (
        "https://host.invalid/<script>|line\n```"
    )
    declared["recording_gaps"][0]["diagnostic_owner"] = "owner|row\n<script>"
    evidence = ackredit.AttributionEvidence.from_attribution(
        original(), results=[declared]
    )
    with pytest.raises(AttributionEvidenceError):
        evidence.report(complete=True)
    report = evidence.report()
    assert "<script>" not in report and "\n```" not in report
    assert "owner\\|row" in report
    assert evidence.to_dict()["results"] == [declared]


@pytest.mark.parametrize("bundle", [False, True])
def test_fresh_saved_cli_is_offline_and_inert_with_diagnosed_gaps(tmp_path, bundle):
    source = original()
    if bundle:
        source = ackredit.compose_attributions([source, source])
    evidence = ackredit.AttributionEvidence.from_attribution(
        source, results=[declarations()] * (2 if bundle else 1)
    )
    path = tmp_path / "evidence.json"
    path.write_text(evidence.to_json())
    before = path.read_bytes()
    script = """
import importlib.abc, socket, sys
sys.path.insert(0, sys.argv[2])
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise AssertionError('producer imported')
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('network or new recording')
socket.create_connection = socket.socket.connect = forbidden
import ackredit
from ackredit.core import registry, collector, session
before = ackredit.get_attribution().to_dict()
items = dict(registry.Registry.items)
registry.register_item = collector.track_item = collector.aggregate = session.read = forbidden
from ackredit.cli import main
sys.argv = ['ackredit', 'report', sys.argv[1], '--input-format', 'evidence', '-f', 'explanation']
assert main() == 0
assert ackredit.get_attribution().to_dict() == before
assert registry.Registry.items == items
"""
    run = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(path),
            str(Path(ackredit.__file__).parents[1]),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    assert run.stdout == evidence.report() + "\n"
    assert path.read_bytes() == before


def test_cli_cannot_overwrite_the_evidence_input(tmp_path, monkeypatch):
    from ackredit.cli import main

    path = tmp_path / "evidence.json"
    path.write_text(ackredit.AttributionEvidence.from_attribution(original()).to_json())
    before = path.read_bytes()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "ackredit",
            "report",
            str(path),
            "--input-format",
            "evidence",
            "-o",
            str(path),
        ],
    )
    assert main() == 1
    assert path.read_bytes() == before
