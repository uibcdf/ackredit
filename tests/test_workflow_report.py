"""Readable reports retain the saved attribution rather than inventing evidence (#89)."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

import ackredit
from ackredit.formats._markdown import escape

FIXTURE = Path(__file__).parent / "data" / "attribution_v1_pyunitwizard.json"


def test_saved_workflow_report_preserves_reference_roles_and_original_versions():
    saved = ackredit.Attribution.from_json(FIXTURE.read_text())
    rendered = saved.report(format="workflow")
    assert "# Workflow attribution" in rendered
    assert "original result" in rendered
    assert "3.1.0" in rendered and "0.27.0" in rendered
    assert escape("executed_software") in rendered
    assert escape("software_description") in rendered
    assert "2018" in rendered and "Journal of Open Source Software" in rendered
    assert "https://doi.org/10.21105/joss.00809" in rendered
    assert escape("software:unyt:3.1.0") in rendered
    assert "pyunitwizard.forms.unyt.convert" in rendered
    assert "Distinct recorded uses: 2" in rendered
    assert "call counts" in rendered and "scientific success" in rendered


def test_live_workflow_report_uses_original_captured_bibliography(clean_registry):
    ackredit.register_item(
        id="software:original", type="software", title="Original", version="1.0"
    )
    with ackredit.session("live workflow"):
        ackredit.track_item(
            "software:original",
            used_by="producer.convert",
            roles=["executed_software"],
            context={"software": "producer", "version": "1.0"},
        )
        ackredit.register_item(
            id="software:original", type="software", title="Changed", version="99.0"
        )
        rendered = ackredit.report(format="workflow")
    assert "Original" in rendered and "1.0" in rendered
    assert "Changed" not in rendered and "99.0" not in rendered


def test_report_counts_distinct_uses_without_claiming_invocation_counts(clean_registry):
    ackredit.register_item(
        id="paper:shared", type="article", title="Shared description", year=2018
    )
    with ackredit.capture("two versions") as run:
        for version in ("1.0", "2.0", "1.0"):
            ackredit.track_item(
                "paper:shared",
                used_by="library.convert",
                roles=["software_description"],
                context={"software": "library", "version": version},
            )
    rendered = run.attribution.report(format="workflow")
    assert "References: 1" in rendered and "Distinct recorded uses: 2" in rendered
    assert "1.0" in rendered and "2.0" in rendered
    assert "2018" in rendered
    assert rendered.count("Shared description") >= 1


def test_duplicate_saved_uses_do_not_invent_distinct_uses_or_calls():
    payload = json.loads(FIXTURE.read_text())
    payload["uses"].append(dict(payload["uses"][0]))
    saved = ackredit.Attribution(payload)
    assert "Distinct recorded uses: 2" in saved.report(format="workflow")
    assert len(saved.to_dict()["uses"]) == 3


def test_graph_reference_numbers_distinguish_same_title_versions(clean_registry):
    with ackredit.capture("versions") as run:
        for version in ("1.0", "2.0"):
            item_id = f"library:{version}"
            ackredit.register_item(
                id=item_id, title="Same library", type="software", version=version
            )
            ackredit.track_item(
                item_id, used_by="library.run", context={"version": version}
            )
    rendered = run.attribution.report(format="workflow")
    assert "(Cite: Reference 1: Same library)" in rendered
    assert "(Cite: Reference 2: Same library)" in rendered


def test_legacy_unscoped_and_unknown_references_are_explicit(clean_registry):
    ackredit.track_item("unknown:reference")
    rendered = ackredit.report(format="workflow")
    assert "unknown:reference" in rendered
    assert "Unscoped" in rendered and "Not recorded" in rendered
    assert "References: 1" in rendered and "Distinct recorded uses: 1" in rendered
    assert "executed" not in rendered


def test_empty_workflow_keeps_a_recorded_scope(clean_registry):
    with ackredit.session("no references"), ackredit.scope("empty.scope"):
        rendered = ackredit.report(format="workflow")
    assert "References: 0" in rendered and "Distinct recorded uses: 0" in rendered
    assert "empty.scope" in rendered
    assert "No references were recorded" in rendered


def test_recursive_workflow_is_finite_and_does_not_drop_an_isolated_target(
    clean_registry,
):
    ackredit.register_item(id="paper:cycle", title="Cycle paper")
    with ackredit.scope("cycle"):
        with ackredit.scope("cycle"):
            ackredit.track_item("paper:cycle")
    with ackredit.scope("island"):
        pass
    rendered = ackredit.report(format="workflow")
    assert "cycle (above)" in rendered and "island" in rendered
    assert len(rendered.splitlines()) < 100


def test_workflow_metadata_cannot_break_tables_links_or_code_fences(clean_registry):
    name = "producer|step <script> ```"
    ackredit.register_item(
        id="unsafe:item",
        title="Title | <script> ```",
        authors=["A <script>"],
        url="javascript:alert(1)",
        note="Note\n<script>",
    )
    with ackredit.capture(
        "result <script>", context={"input": "| <script> ```"}
    ) as run:
        ackredit.track_item(
            "unsafe:item",
            used_by=name,
            roles=["role|injected"],
            context={"value": "| <script> ```"},
        )
    rendered = run.attribution.report(format="workflow")
    assert "(javascript:" not in rendered
    assert "role\\|injected" in rendered
    assert "result \\<script\\>" in rendered
    # The graph is literal fenced text. Its user-supplied backticks cannot end it.
    assert "````text\n" in rendered
    assert "| Target |" in rendered


def test_graph_control_characters_cannot_invent_a_child(clean_registry):
    target = "library.run\n    └── invented"
    ackredit.register_item(id="paper", title="Title\n(Cite: invented)")
    with ackredit.capture("literal graph") as run:
        ackredit.track_item("paper", used_by=target)
    rendered = run.attribution.report(format="workflow")
    graph = rendered.split("## Recorded graph\n", 1)[1]
    assert "library.run\\n    └── invented" in graph
    assert "Title\\n(Cite: invented)" in graph
    assert "\n    └── invented" not in graph
    assert target in run.attribution.to_dict()["usage_tree"]


def test_saved_workflow_needs_no_producer_or_current_registry(tmp_path):
    script = """
import importlib.abc, pathlib, socket, sys
sys.path.insert(0, sys.argv[2])
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pint', 'unyt', 'pyunitwizard'}:
            raise AssertionError('reader imported producer')
sys.meta_path.insert(0, NoProducer())
socket.create_connection = lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network'))
import ackredit
original = pathlib.Path(sys.argv[1]).read_text()
saved = ackredit.Attribution.from_json(original)
before = saved.to_dict()
rendered = saved.report(format='workflow')
assert '3.1.0' in rendered and '0.27.0' in rendered
assert '10.21105/joss.00809' in rendered
assert saved.to_dict() == before and ackredit.get_used_items() == {}
assert not {'pint','unyt','pyunitwizard'} & sys.modules.keys()
"""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(FIXTURE),
            str(Path(ackredit.__file__).parents[1]),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_workflow_dump_cannot_overwrite_the_bibliography_markdown(
    tmp_path, clean_registry
):
    ackredit.track_item("legacy")
    ackredit.dump(tmp_path, formats=["markdown", "workflow"])
    assert (
        (tmp_path / "ackredit_report_workflow.md")
        .read_text()
        .startswith("# Workflow attribution")
    )
    assert (tmp_path / "ackredit_report_markdown.md").is_file()


def test_workflow_unsupported_options_use_existing_catalog_errors():
    with pytest.raises(ValueError) as error:
        ackredit.get_attribution().report(format="workflow", invented=True)
    assert error.value.code == "ACKREDIT-E010"
