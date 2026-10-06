"""Real wheels must preserve plugin discovery, diagnostics and capture contracts."""

import importlib
import json
import sys
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parents[1] / "devtools"


@pytest.fixture(scope="module")
def plugin_tools():
    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(TOOLS))
        yield importlib.import_module("benchmark_plugins")


@pytest.fixture(scope="module")
def installed_packs(tmp_path_factory, plugin_tools):
    directory = tmp_path_factory.mktemp("installed-plugins")
    sources = []
    for index, refs, failure in (
        (0, 3, None),
        (1, 1, "citations"),
        (2, 1, "formats"),
        (3, 1, "conflict"),
        (4, 1, None),
    ):
        source = directory / "sources" / str(index)
        plugin_tools.write_pack(source, index, refs, failure)
        sources.append(source)
    records = plugin_tools.build_packs(sources, directory / "wheels")
    return directory, records


def test_installed_failures_conflicts_and_reentry_preserve_neighbors(
    installed_packs, plugin_tools
):
    directory, records = installed_packs
    python = plugin_tools.environment(
        directory / "broken-env",
        [
            directory / "wheels" / records[f"ackredit_bench_pack{i}"]["filename"]
            for i in range(4)
        ],
    )
    code = """
import importlib, importlib.metadata, sys, warnings
import smonitor
from smonitor.handlers import MemoryHandler
diagnostics = MemoryHandler()
smonitor.configure(handlers=[diagnostics])
import ackredit
# Observe the catalog incident through the provider's handler contract, without
# assuming default event retention or replacing its initial warning hooks.
assert any(event['code'] == 'ACKREDIT-W008' for event in diagnostics.events)
assert ackredit.get_used_items() == {}
assert not any(name.endswith('.formats') for name in sys.modules if name.startswith('ackredit_bench_pack'))
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    # First demand must load the requested plugin without a preparation call.
    assert ackredit.report(format='pack0') == ''
assert [w.message.code for w in caught] == ['ACKREDIT-W014', 'ACKREDIT-W014']
assert 'pack0' in ackredit.available_formats()
assert 'pack2' not in ackredit.available_formats()
assert 'bibtex' in ackredit.available_formats()
for i in range(4):
    assert importlib.import_module(f'ackredit_bench_pack{i}.formats').registration_calls == 1
import ackredit_bench_pack0 as pack
for label in ('first', 'reused'):
    with ackredit.capture(label) as run:
        assert pack.compute(3) == 9
    assert {item['id'] for item in run.attribution.to_dict()['items']} == {
        'pack0:reference0', 'pack0:reference1', 'pack0:reference2'}
    assert all(item['note'] == 'Fixture version 1.0.0' for item in run.attribution.to_dict()['items'])
    assert run.attribution.report(format='pack0') == 'pack0:reference0|pack0:reference1|pack0:reference2'
    assert 'Pack 0 reference' in run.attribution.report(format='bibtex')
assert importlib.metadata.distribution('ackredit_bench_pack0').version == '1.0.0'
assert pack.__file__.startswith(sys.prefix)
"""
    plugin_tools.lifecycle.child([str(python), "-c", code], cwd=directory)


def test_late_installation_is_visible_to_first_format_demand_and_citation_reload(
    installed_packs, plugin_tools
):
    directory, records = installed_packs
    python = plugin_tools.environment(directory / "late-env", [])
    wheel = directory / "wheels" / records["ackredit_bench_pack4"]["filename"]
    code = """
import subprocess, sys
import ackredit
from ackredit.core.registry import Registry
assert 'pack4:reference0' not in Registry.items
subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps', sys.argv[1]], check=True, capture_output=True)
assert 'pack4:reference0' not in Registry.items
assert ackredit.report(format='pack4') == ''
ackredit.load_plugins()
assert Registry.items['pack4:reference0']['note'] == 'Fixture version 1.0.0'
import ackredit_bench_pack4 as pack
assert pack.registration_calls == 1
ackredit.load_plugins()
assert pack.registration_calls == 2
assert Registry.injections['fixture_host4'] == ['pack4:reference0']
with ackredit.capture('late') as run:
    assert pack.compute(3) == 9
assert run.attribution.report(format='pack4') == 'pack4:reference0'
"""
    plugin_tools.lifecycle.child([str(python), "-c", code, str(wheel)], cwd=directory)


def test_installed_pack_measurements_and_plugin_free_reader(
    installed_packs, plugin_tools
):
    directory, records = installed_packs
    name = "ackredit_bench_pack0"
    python = plugin_tools.environment(
        directory / "healthy-env", [directory / "wheels" / records[name]["filename"]]
    )
    case = directory / "case.json"
    case.write_text(json.dumps({"packs": {name: records[name]}}))
    saved = directory / "detached.json"
    for memory in (False, True):
        response = plugin_tools.lifecycle.child(
            [
                str(python),
                str(TOOLS / "benchmark_plugins.py"),
                "--worker",
                "operations",
                "--case",
                str(case),
                *(["--memory"] if memory else []),
            ],
            cwd=directory,
        )
        result = json.loads(response.stdout)
        assert result["facts"]["references"] == 3
        assert result["facts"]["captures"] == 2
        assert result["facts"]["format_callbacks"] == 1
        assert (
            result["facts"]["plugin_files_verified"][name]["wheel_sha256"]
            == records[name]["sha256"]
        )
        assert all(
            set(m)
            == (
                {"retained_delta_bytes", "peak_extra_bytes"}
                if memory
                else {"elapsed_us"}
            )
            for m in result["measurements"].values()
        )
        assert response.stderr == ""
        saved.write_text(result["detached"])
    response = plugin_tools.lifecycle.child(
        [sys.executable, str(TOOLS / "benchmark_plugins.py"), "--reader", str(saved)],
        cwd=directory,
    )
    reader = json.loads(response.stdout)
    assert reader["references"] == 3
    assert reader["execution_credit"] is False
    assert reader["json_sha256"] == result["facts"]["json_sha256"]


def test_fixture_computation_keeps_working_when_ackredit_is_absent(
    installed_packs, plugin_tools
):
    directory, records = installed_packs
    # Give this case its own environment rather than depending on test order.
    python = plugin_tools.environment(
        directory / "absence-env",
        [directory / "wheels" / records["ackredit_bench_pack0"]["filename"]],
    )
    code = """
import importlib.abc, sys
class NoAckredit(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'ackredit':
            raise ModuleNotFoundError('ackredit', name='ackredit')
sys.meta_path.insert(0, NoAckredit())
import ackredit_bench_pack0 as pack
assert pack.compute(3) == 9
assert pack.registration_calls == 0
assert 'ackredit' not in sys.modules
"""
    plugin_tools.lifecycle.child([str(python), "-c", code], cwd=directory)
