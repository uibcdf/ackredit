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
    providers = {
        "ackredit": bundle_tools.verify_installed(
            ackredit, manifest["packages"]["candidate"]
        ),
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
    assert "ackredit/CITATION.cff" in receipt["packages"]["candidate"]["files"]


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


def test_workflow_report_is_faithful_in_a_producer_free_reader(installed):
    ackredit, puw, _, output, _ = installed
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
