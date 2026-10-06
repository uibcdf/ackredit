"""Mandatory real-producer receiving gate; run only with the installed bundle.

No import skips are permitted here. Ordinary Ackredit tests do not require
PyUnitWizard or optional scientific engines. See devguide/receiving_validation.md.
"""

import importlib.util
import json
import os
import platform
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "qualification_bundle", TOOLS / "qualification_bundle.py"
)
bundle_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle_tools)


@pytest.fixture(scope="module")
def installed():
    import pint
    import pyunitwizard as puw
    import unyt

    import ackredit

    bundle = Path(os.environ["ACKREDIT_QUALIFICATION_BUNDLE"]).resolve()
    output = Path(os.environ["ACKREDIT_QUALIFICATION_OUTPUT"]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = bundle_tools.verify_bundle(bundle)
    minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert minor == os.environ["EXPECTED_PYTHON"], minor
    assert sys.platform in {"linux", "darwin"}, sys.platform
    if sys.platform == "darwin":
        assert platform.machine() == "arm64", platform.machine()
    candidate = manifest["packages"]["candidate"]
    if manifest["schema"] == "ackredit.receiving-bundle@2":
        proof = json.loads((output / "conda-before.json").read_text())
        candidate_identity = bundle_tools.verify_conda_receiving(
            ackredit, candidate, proof
        )
    else:
        candidate_identity = bundle_tools.verify_installed(ackredit, candidate)
    providers = {
        "ackredit": candidate_identity,
        "pyunitwizard": bundle_tools.verify_installed(
            puw, manifest["packages"]["producer"]
        ),
    }
    for module in (pint, unyt):
        origin = Path(module.__file__).resolve()
        assert "site-packages" in origin.parts, origin
        assert any(
            origin.is_relative_to(Path(prefix).resolve())
            for prefix in (sys.prefix, sys.base_prefix)
        ), origin
        providers[module.__name__] = {
            "version": module.__version__,
            "origin": str(origin),
        }
    receipt = {
        "schema": "ackredit.receiving-cell@1",
        "python": platform.python_version(),
        "platform": sys.platform,
        "architecture": platform.machine(),
        "packages": manifest["packages"],
        "providers": providers,
    }
    (output / "identity.json").write_text(json.dumps(receipt, indent=2) + "\n")
    puw.configure.reset()
    puw.configure.load_library(["pint", "unyt"])
    return ackredit, puw, bundle, output, receipt


def _child(script: str, *arguments: Path):
    result = subprocess.run(
        [sys.executable, "-c", script, *map(str, arguments)],
        cwd=arguments[-1],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_installed_identity_and_bundled_resources(installed):
    ackredit, _, _, _, receipt = installed
    assert receipt["providers"]["ackredit"]["version"] == ackredit.__version__
    assert hasattr(ackredit, "observe_calls") and hasattr(ackredit, "prepare_credit")
    candidate = receipt["packages"]["candidate"]
    if candidate.get("kind") == "conda":
        assert receipt["providers"]["ackredit"]["conda_sha256"] == candidate["sha256"]
    else:
        assert "ackredit/CITATION.cff" in candidate["files"]


def test_real_pipeline_retains_exact_references_roles_and_graph(installed):
    ackredit, puw, _, output, receipt = installed
    q = puw.quantity([1.0, 2.0], "meter", form="pint")
    captures = {}
    with (
        ackredit.session("receiving pipeline"),
        ackredit.scope("pipeline"),
        ackredit.observe_calls(puw),
        puw.attribution(),
    ):
        for name in ("first", "reused"):
            with ackredit.capture(name) as run:
                value = puw.convert(q, to_unit=q._REGISTRY.centimeter)
            assert puw.get_value(value).tolist() == [100.0, 200.0]
            assert value.units == q._REGISTRY.centimeter
            data = run.attribution.to_dict()
            assert {u["context"]["software"] for u in data["uses"]} == {
                "pyunitwizard",
                "pint",
            }
            assert len(data["items"]) == 2
            assert {i["type"] for i in data["items"]} == {"software"}
            assert "pyunitwizard.convert" in data["usage_tree"]["pipeline"]["children"]
            assert "pyunitwizard.quantity" not in data["usage_tree"]
            captures[name] = data
        with ackredit.capture("translated") as run:
            value = puw.convert(q, to_form="unyt")
        assert value.value.tolist() == [1.0, 2.0]
        assert str(value.units) == "m"
        data = run.attribution.to_dict()
        assert {u["context"]["software"] for u in data["uses"]} == {
            "pyunitwizard",
            "pint",
            "unyt",
        }
        assert len(data["items"]) == 4
        article = next(i for i in data["items"] if i["type"] == "article")
        assert article["doi"] == "10.21105/joss.00809"
        descriptions = [u for u in data["uses"] if u["item_id"] == article["id"]]
        assert descriptions and all(
            u["roles"] == ["software_description"] for u in descriptions
        )
        assert (
            "pyunitwizard.forms.pint.quantity_to_unyt"
            in data["usage_tree"]["pyunitwizard.convert"]["children"]
        )
        captures["translated"] = data
        workflow = ackredit.get_attribution().to_dict()
    assert len(workflow["items"]) == 4
    assert captures["first"]["items"] == captures["reused"]["items"]
    versions = {name: p["version"] for name, p in receipt["providers"].items()}
    for data in captures.values():
        for use in data["uses"]:
            assert use["context"]["version"] == versions[use["context"]["software"]]
        own = next(i for i in data["items"] if i.get("doi") == "10.5281/zenodo.8092688")
        assert own["version"] == puw.__version__
        assert "10.5281/zenodo.8092688" in ackredit.Attribution.from_dict(data).report(
            format="bibtex"
        )
    saved = {"captures": captures, "workflow": workflow}
    (output / "pipeline.json").write_text(json.dumps(saved, indent=2) + "\n")
    # A separate reader never loads the producer or either scientific engine.
    _child(
        """
import importlib.abc, json, pathlib, sys
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise ModuleNotFoundError('producer unavailable', name=fullname)
sys.meta_path.insert(0, NoProducer())
import ackredit
saved = json.loads((pathlib.Path(sys.argv[1]) / 'pipeline.json').read_text())
for data in [*saved['captures'].values(), saved['workflow']]:
    result = ackredit.Attribution.from_dict(data)
    assert result.to_dict() == data
    assert '10.5281/zenodo.8092688' in result.report(format='bibtex')
assert '10.21105/joss.00809' in ackredit.Attribution.from_dict(
    saved['captures']['translated']).report(format='bibtex')
assert not {'pyunitwizard', 'pint', 'unyt'} & sys.modules.keys()
assert ackredit.get_used_items() == {}
(pathlib.Path(sys.argv[1]) / 'reader.json').write_text(json.dumps({
    'producer_imports': 0, 'new_credits': 0, 'payload_equality': True}))
""",
        output,
    )


def test_noop_and_failed_calls_distinguish_entry_from_completed_backend(installed):
    ackredit, puw, _, _, _ = installed
    q = puw.quantity(2.0, "meter", form="pint")
    with (
        ackredit.session("entry boundary"),
        ackredit.observe_calls(puw),
        puw.attribution(),
    ):
        with ackredit.capture("noop") as noop:
            assert puw.convert(q) is q
        with ackredit.capture("failed") as failed:
            with pytest.raises(Exception):
                puw.convert(q, to_unit=q._REGISTRY.second)
    for run in (noop, failed):
        data = run.attribution.to_dict()
        assert len(data["items"]) == len(data["uses"]) == 1
        assert data["uses"][0]["context"]["software"] == "pyunitwizard"
        assert data["uses"][0]["roles"] == ["executed_software"]


def test_warmed_backend_plans_retain_credit_and_invalidate_by_value(
    installed, monkeypatch
):
    ackredit, puw, _, output, _ = installed
    from pyunitwizard import _ackredit
    from pyunitwizard._private import backend_references
    from pyunitwizard._private.smonitor.warnings import AckreditTrackingWarning

    evidence = {}
    for library in ("pint", "unyt"):
        module = sys.modules[library]
        q = puw.quantity(2.0, "meter", form=library)
        target = q._REGISTRY.centimeter if library == "pint" else module.Unit("cm")
        _ackredit._PREPARED.clear()
        with (
            ackredit.session(f"warmed {library}"),
            ackredit.scope("prepared.pipeline"),
            ackredit.observe_calls(puw),
            puw.attribution(),
        ):
            with ackredit.capture("original") as original:
                puw.convert(q, to_unit=target, to_form=library)
            saved = original.attribution.to_dict()

            def unnecessary_copy(*args):
                pytest.fail("warmed conversion copied backend declarations again")

            with monkeypatch.context() as warm:
                warm.setattr(backend_references, "records", unnecessary_copy)
                warm.setattr(
                    backend_references._DeclarationPlan, "records", unnecessary_copy
                )
                with ackredit.capture("reused") as reused:
                    result = puw.convert(q, to_unit=target, to_form=library)
                assert puw.get_value(result) == 200.0
                assert result.units == target
                assert reused.attribution.to_dict() == dict(saved, name="reused")
            assert {use["context"]["software"] for use in saved["uses"]} == {
                "pyunitwizard",
                library,
            }
            assert len(saved["items"]) == (2 if library == "pint" else 3)
            assert (
                "pyunitwizard.convert"
                in saved["usage_tree"]["prepared.pipeline"]["children"]
            )
            versions = {"pyunitwizard": puw.__version__, library: module.__version__}
            for use in saved["uses"]:
                assert use["context"]["version"] == versions[use["context"]["software"]]
                assert use["roles"] == [
                    "software_description"
                    if use["item_id"] == "doi:10.21105/joss.00809"
                    else "executed_software"
                ]
            if library == "unyt":
                article = next(
                    item for item in saved["items"] if item["type"] == "article"
                )
                assert article["doi"] == "10.21105/joss.00809"

            with monkeypatch.context() as changed:
                changed.setattr(
                    module, "__version__", module.__version__ + "+qualification99"
                )
                with ackredit.capture("version changed") as updated:
                    result = puw.convert(q, to_unit=target, to_form=library)
                assert puw.get_value(result) == 200.0 and result.units == target
                updated_data = updated.attribution.to_dict()
                backend_uses = [
                    use
                    for use in updated_data["uses"]
                    if use["context"]["software"] == library
                ]
                assert backend_uses
                assert {use["context"]["version"] for use in backend_uses} == {
                    module.__version__
                }
                software = next(
                    item
                    for item in updated_data["items"]
                    if item["id"] == f"software:{library}:{module.__version__}"
                )
                assert software["version"] == module.__version__
                assert original.attribution.to_dict() == saved
                changed.setitem(
                    backend_references._SOFTWARE,
                    library,
                    deepcopy(backend_references._SOFTWARE[library]),
                )
                backend_references._SOFTWARE[library]["authors"].append(
                    "Changed declaration"
                )
                with (
                    ackredit.capture("metadata conflict") as conflict,
                    pytest.warns(AckreditTrackingWarning) as diagnostics,
                ):
                    result = puw.convert(q, to_unit=target, to_form=library)
                assert puw.get_value(result) == 200.0 and result.units == target
                assert diagnostics[0].message.code == "PUW-WARN-ACK-001"
                conflict_data = conflict.attribution.to_dict()
                assert len(conflict_data["items"]) == 1
                assert {
                    use["context"]["software"] for use in conflict_data["uses"]
                } == {"pyunitwizard"}
                assert updated.attribution.to_dict() == updated_data
                assert original.attribution.to_dict() == saved
            evidence[library] = {
                "original": saved,
                "reused": reused.attribution.to_dict(),
                "changed_version": updated_data,
                "metadata_conflict": conflict_data,
                "diagnostic": diagnostics[0].message.code,
            }
    (output / "prepared-reuse.json").write_text(json.dumps(evidence, indent=2) + "\n")


def test_workflow_report_is_faithful_in_a_producer_free_reader(installed):
    ackredit, puw, _, output, _ = installed
    # A host may have registered the same valid bibliography before observation.
    # Tuple/list JSON equivalence must not become a false identity conflict (#92).
    declared = deepcopy(puw.__ackredit__["items"][0])
    declared["authors"] = tuple(declared["authors"])
    ackredit.register_item(**declared)
    q = puw.quantity([1.0, 2.0], "meter", form="pint")
    with (
        ackredit.session("report receiving"),
        ackredit.scope("report.pipeline"),
        ackredit.observe_calls(puw),
        puw.attribution(),
        ackredit.capture("reported result", context={"purpose": "receiving"}) as run,
    ):
        value = puw.convert(q, to_form="unyt")
    assert value.value.tolist() == [1.0, 2.0] and str(value.units) == "m"
    payload = run.attribution.to_dict()
    assert len(payload["items"]) == 4
    own = next(item for item in payload["items"] if item["id"] == declared["id"])
    assert own["authors"] == list(declared["authors"])
    (output / "reported-pipeline.json").write_text(json.dumps(payload, indent=2) + "\n")
    _child(
        """
import importlib.abc, json, pathlib, socket, sys
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise AssertionError('report reader imported producer')
sys.meta_path.insert(0, NoProducer())
socket.create_connection = lambda *a, **kw: (_ for _ in ()).throw(AssertionError('network'))
import ackredit
from ackredit.formats._markdown import escape
output = pathlib.Path(sys.argv[1])
payload = json.loads((output / 'reported-pipeline.json').read_text())
saved = ackredit.Attribution.from_dict(payload)
rendered = saved.report(format='workflow')
assert 'References: 4' in rendered and 'call counts' in rendered
assert '10.21105/joss.00809' in rendered and '10.5281/zenodo.8092688' in rendered
assert 'report.pipeline' in rendered and 'pyunitwizard.convert' in rendered
assert 'pyunitwizard.forms.pint.quantity_to_unyt' in rendered
for use in payload['uses']:
    assert escape(use['context']['version']) in rendered
    assert all(escape(role) in rendered for role in use['roles'])
for number, item in enumerate(payload['items'], 1):
    assert f'Reference {number}: ' in rendered
assert saved.to_dict() == payload and ackredit.get_used_items() == {}
assert not {'pyunitwizard', 'pint', 'unyt'} & sys.modules.keys()
(output / 'workflow-report.md').write_text(rendered)
(output / 'workflow-reader.json').write_text(json.dumps({
    'producer_imports': 0, 'new_credits': 0, 'payload_equality': True,
    'references': len(payload['items']), 'format': 'workflow'}))
""",
        output,
    )


def test_saved_result_composition_retains_original_boundaries(installed):
    ackredit, puw, _, output, _ = installed
    q = puw.quantity([1.0, 2.0], "meter", form="pint")
    with (
        ackredit.session("composition receiving"),
        ackredit.scope("composition.pipeline"),
        ackredit.observe_calls(puw),
        puw.attribution(),
    ):
        with ackredit.capture("pint result", context={"cell": 1}) as pint_run:
            converted = puw.convert(q, to_unit=q._REGISTRY.centimeter)
        assert puw.get_value(converted).tolist() == [100.0, 200.0]
        with ackredit.capture("unyt result", context={"cell": 2}) as unyt_run:
            translated = puw.convert(q, to_form="unyt")
        assert translated.value.tolist() == [1.0, 2.0] and str(translated.units) == "m"
        with ackredit.capture("empty result") as empty_run:
            pass
        results = [
            pint_run.attribution,
            unyt_run.attribution,
            pint_run.attribution,
            empty_run.attribution,
        ]
        originals = [result.to_dict() for result in results]
        before = ackredit.get_attribution().to_dict()
        bundle = ackredit.compose_attributions(
            results, name="notebook", context={"owner": "receiving"}
        )
        assert bundle.to_dict()["attributions"] == originals
        assert bundle.attributions[-1].to_dict()["items"] == []
        assert len(json.loads(bundle.report(format="csl"))) == 4
        reversed_bundle = ackredit.compose_attributions(reversed(results))
        assert reversed_bundle.report(format="bibtex") == bundle.report(format="bibtex")
        conflict = results[1].to_dict()
        conflict["items"][0]["title"] = "conflicting original"
        with pytest.raises(ValueError) as caught:
            ackredit.compose_attributions([results[0], ackredit.Attribution(conflict)])
        assert caught.value.code == "ACKREDIT-E011"
        assert ackredit.get_attribution().to_dict() == before
        assert [result.to_dict() for result in results] == originals
    (output / "composition.json").write_text(bundle.to_json(), encoding="utf-8")
    _child(
        """
import importlib.abc, json, pathlib, socket, sys
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard', 'pint', 'unyt'}:
            raise AssertionError('composition reader imported producer')
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('composition reader queried network')
socket.create_connection = socket.socket.connect = forbidden
import ackredit
from ackredit.cli import main
output = pathlib.Path(sys.argv[1])
path = output / 'composition.json'
payload = json.loads(path.read_text(encoding='utf-8'))
saved = ackredit.AttributionBundle.from_dict(payload)
assert saved.to_dict() == payload
assert [item.to_dict() for item in saved.attributions] == payload['attributions']
rendered = saved.report()
assert 'Shared bibliography: 4' in rendered
assert '## Result 1: pint result' in rendered and '## Result 2: unyt result' in rendered
assert '## Result 3: pint result' in rendered and '## Result 4: empty result' in rendered
assert rendered.count('### Reference ') == 4
assert '10.21105/joss.00809' in rendered and '10.5281/zenodo.8092688' in rendered
assert not {'pyunitwizard', 'pint', 'unyt'} & sys.modules.keys()
sys.argv = ['ackredit', 'report', str(path), '--input-format', 'bundle', '-f', 'workflow',
            '-o', str(output / 'composition-report.md')]
assert main() == 0
assert (output / 'composition-report.md').read_text(encoding='utf-8') == rendered
assert ackredit.get_used_items() == {}
(output / 'composition-reader.json').write_text(json.dumps({
    'producer_imports': 0, 'new_credits': 0, 'payload_equality': True,
    'original_members': 4, 'shared_references': 4, 'independent_graphs': True}))
""",
        output,
    )


def test_absent_optional_provider_preserves_completed_science(installed):
    _, _, _, output, _ = installed
    _child(
        """
import importlib.abc, json, pathlib, sys
class NoAckredit(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] == 'ackredit':
            raise ModuleNotFoundError('optional provider unavailable', name=fullname)
sys.meta_path.insert(0, NoAckredit())
import pyunitwizard as puw
assert 'ackredit' not in sys.modules and 'pint' not in sys.modules
with puw.attribution():
    q = puw.quantity(2., 'meter', form='pint')
    assert puw.get_value(puw.convert(q, to_unit='centimeter')) == 200.
assert 'ackredit' not in sys.modules
(pathlib.Path(sys.argv[1]) / 'absence.json').write_text(json.dumps({
    'ackredit_imports': 0, 'centimeters': 200.}))
""",
        output,
    )


def test_original_090_provider_supports_reused_backend_credit(installed, tmp_path):
    _, _, bundle, output, receipt = installed
    released = receipt["packages"]["released"]
    target = tmp_path / "site-packages"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--no-index",
            "--target",
            str(target),
            str(bundle / released["wheel"]),
        ],
        check=True,
        cwd=output,
        capture_output=True,
        text=True,
    )
    _child(
        """
import hashlib, importlib.metadata, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import ackredit
import pyunitwizard as puw
origin = pathlib.Path(ackredit.__file__).resolve()
assert origin.is_relative_to(pathlib.Path(sys.argv[1]).resolve())
assert ackredit.__version__ == importlib.metadata.version('ackredit') == '0.9.0'
assert not hasattr(ackredit, 'prepare_credit')
bundle = json.loads((pathlib.Path(sys.argv[2]) / 'bundle.json').read_text())
for relative, digest in bundle['packages']['released']['files'].items():
    assert hashlib.sha256((origin.parent.parent / relative).read_bytes()).hexdigest() == digest
q = puw.quantity(2., 'meter', form='pint')
captures = []
with ackredit.session('released fallback'), puw.attribution():
    for name in ('first', 'reused'):
        with ackredit.capture(name) as run:
            result = puw.convert(q, to_unit=q._REGISTRY.centimeter)
        assert puw.get_value(result) == 200.
        captures.append(run.attribution.to_dict())
assert captures[0]['items'] == captures[1]['items']
assert all(len(data['items']) == len(data['uses']) == 1 for data in captures)
assert all(data['uses'][0]['context']['software'] == 'pint' for data in captures)
(pathlib.Path(sys.argv[3]) / 'released-fallback.json').write_text(json.dumps({
    'version': ackredit.__version__, 'source_commit': bundle['packages']['released']['source_commit'],
    'captures': captures}))
""",
        target,
        bundle,
        output,
    )


def test_provider_evidence_retains_actual_origins_and_diagnosed_gaps(
    installed, monkeypatch
):
    ackredit, puw, _, output, _ = installed
    from ackredit._private.smonitor.warnings import ProviderObservationWarning
    from ackredit.core import providers

    q = puw.quantity([1.0, 2.0], "meter", form="pint")
    producer_id = puw.__ackredit__["items"][0]["id"]
    producer_fields = sorted(puw.__ackredit__["items"][0])
    with (
        ackredit.session("evidence receiving"),
        ackredit.scope("evidence.pipeline"),
        ackredit.observe_calls(puw),
        puw.attribution(),
    ):
        with ackredit.capture("first", record_evidence=True) as first:
            converted = puw.convert(q, to_unit=q._REGISTRY.centimeter)
        assert puw.get_value(converted).tolist() == [100.0, 200.0]
        with ackredit.capture("reused", record_evidence=True) as reused:
            translated = puw.convert(q, to_form="unyt")
        assert translated.value.tolist() == [1.0, 2.0] and str(translated.units) == "m"
        for run in (first, reused):
            facts = run.evidence.to_dict()["results"][0]
            assert len(facts["metadata_origins"]) == 1
            origin = facts["metadata_origins"][0]
            assert (
                origin["item_id"] == producer_id and origin["fields"] == producer_fields
            )
            assert origin["method"] == "provider_declaration"
            assert origin["source"] == "pyunitwizard.__ackredit__.items"
            assert ackredit.__version__ in origin["recorder"]
            assert facts["recording_gaps"] is None
            assert len(run.attribution.to_dict()["items"]) > len(
                facts["metadata_origins"]
            )
        with monkeypatch.context() as patch:

            def fail_recording(*args, **kwargs):
                raise RuntimeError("controlled provider-recorder fault")

            patch.setattr(providers, "_track_prepared_item", fail_recording)
            with ackredit.capture("recording fault", record_evidence=True) as failed:
                with pytest.warns(ProviderObservationWarning) as emitted:
                    result = puw.convert(q, to_unit=q._REGISTRY.centimeter)
            assert puw.get_value(result).tolist() == [100.0, 200.0]
            facts = failed.evidence.to_dict()["results"][0]
            assert facts["metadata_origins"] is None
            assert any(
                record["boundary"] == "pyunitwizard.convert"
                and record["diagnostic_code"] == emitted[0].message.code
                for record in facts["recording_gaps"]
            )
            assert all(
                record["diagnostic_owner"] == "ackredit"
                for record in facts["recording_gaps"]
            )
        with ackredit.capture("selected but unused", record_evidence=True) as empty:
            pass
        assert empty.attribution.to_dict()["items"] == []
        assert empty.evidence.to_dict()["results"][0]["observation_scope"]
        runs = [first, reused, failed, empty]
        bundle = ackredit.compose_attributions(
            [run.attribution for run in runs], name="real provider evidence"
        )
        companion = ackredit.AttributionEvidence.from_attribution(
            bundle, results=[run.evidence.to_dict()["results"][0] for run in runs]
        )
        assert companion.attribution.to_dict() == bundle.to_dict()
    (output / "provider-evidence.json").write_text(
        companion.to_json(), encoding="utf-8"
    )
    (output / "provider-evidence-workflow.md").write_text(
        bundle.report(), encoding="utf-8"
    )
    (output / "provider-evidence-integrated-workflow.md").write_text(
        companion.report("workflow", include_evidence=True), encoding="utf-8"
    )
    _child(
        """
import importlib.abc, json, pathlib, socket, sys, warnings
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'pyunitwizard','pint','unyt'}:
            raise AssertionError('provider evidence reader imported a producer')
sys.meta_path.insert(0, NoProducer())
def forbidden(*args, **kwargs):
    raise AssertionError('network or new recording')
socket.create_connection = socket.socket.connect = forbidden
import ackredit
from ackredit.core import registry, collector, session
from ackredit.cli import main
before = ackredit.get_attribution().to_dict()
items = dict(registry.Registry.items)
registry.register_item = collector.track_item = collector.aggregate = session.read = forbidden
output = pathlib.Path(sys.argv[1])
path = output/'provider-evidence.json'
original_bytes = path.read_bytes()
with warnings.catch_warnings(record=True) as emitted:
    saved = ackredit.AttributionEvidence.from_json(original_bytes.decode())
    assert saved.to_dict() == json.loads(original_bytes)
    results = saved.explain()['results']
    assert len(results)==4
    assert results[0]['metadata_origins'][0]['method']=='provider_declaration'
    assert results[1]['metadata_origins'][0]['source']=='pyunitwizard.__ackredit__.items'
    assert results[2]['metadata_origins'] is None and results[2]['recording_gaps']
    assert results[3]['metadata_origins'] is None and results[3]['observation_scope']
    assert saved.attribution.attributions[-1].to_dict()['items']==[]
    assert saved.report('workflow') == (output/'provider-evidence-workflow.md').read_text()
    rendered=saved.report()
    sys.argv=['ackredit','report',str(path),'--input-format','evidence','-f','explanation','-o',str(output/'provider-evidence-report.md')]
    assert main()==0
    assert (output/'provider-evidence-report.md').read_text()==rendered
    integrated=saved.report('workflow',include_evidence=True)
    assert integrated==(output/'provider-evidence-integrated-workflow.md').read_text()
    assert 'Provider declaration' in integrated and 'Metadata sources' in integrated
    assert 'ACKREDIT-W019' in integrated and 'pyunitwizard.convert' in integrated
    assert 'Selected boundaries do not establish that a function ran' in integrated
    assert 'Other field origins remain unknown' in integrated
    assert saved.attribution.to_dict()==saved.to_dict()['attribution']
    sys.argv=['ackredit','report',str(path),'--input-format','evidence','-f','workflow','--include-evidence','-o',str(output/'provider-evidence-integrated-cli.md')]
    assert main()==0
    assert (output/'provider-evidence-integrated-cli.md').read_text()==integrated
assert emitted==[]
assert path.read_bytes()==original_bytes
assert ackredit.get_attribution().to_dict()==before and registry.Registry.items==items
assert not {'pyunitwizard','pint','unyt'} & sys.modules.keys()
(output/'provider-evidence-reader.json').write_text(json.dumps({
    'producer_imports':0,'network_attempts':0,'new_credits':0,'new_diagnostics':0,
    'original_versions_preserved':True,'actual_provider_declaration_origins':True,
    'controlled_recording_fault_retained':True,'unchanged_workflow_report':True,
    'integrated_workflow_matches_cli':True,'original_workflow_default_unchanged':True,
    'scope':'Real Pint/unyt calculation with opt-in provider evidence and controlled recorder fault; broader recorder origins remain unknown.'
}))
""",
        output,
    )
