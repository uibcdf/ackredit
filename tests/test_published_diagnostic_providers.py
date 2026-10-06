"""Receiving contracts for optional new provider capabilities; no default bypass."""

import inspect
import json
import os
import subprocess
import sys

import pytest


@pytest.fixture
def scoped_providers(request):
    import argdigest
    import smonitor
    import smonitor.integrations

    available = (
        hasattr(smonitor, "diagnostic_scope")
        and hasattr(smonitor.integrations, "register_provider")
        and "argument_digestion" in inspect.signature(argdigest.DigestConfig).parameters
    )
    if not available:
        if request.config.getoption("--require-scoped-providers"):
            pytest.fail(
                "This receiving lane requires scoped capture and provider registration"
            )
        pytest.skip("These optional APIs need SMonitor 0.19.0 and ArgDigest 0.15.0")


@pytest.fixture
def receiving_python(request):
    return request.config.getoption("--diagnostic-receiving-python") or sys.executable


def _child(code, tmp_path, receiving_python):
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [receiving_python, "-c", code],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stderr == "", result.stderr
    return json.loads(result.stdout)


def test_ackredit_import_preserves_application_policy_and_registers_catalog(
    scoped_providers, receiving_python, tmp_path
):
    result = _child(
        """
import json, warnings
import smonitor
from smonitor.handlers import MemoryHandler
handler = MemoryHandler()
manager = smonitor.configure(level='WARNING', profile='qa', args_summary=False,
    capture_logging=False, capture_warnings=False, handlers=[handler],
    run_id='receiving-run', session_id='receiving-session')
configured = manager.config
import ackredit
from ackredit._private.smonitor import PACKAGE_ROOT, CODES
from ackredit._private.smonitor.emitter import bundle
from ackredit._private.smonitor.warnings import SessionLoadWarning
from smonitor.integrations import ensure_configured
assert manager.config is configured
assert configured.profile == 'qa' and configured.level == 'WARNING'
assert not configured.args_summary
assert not configured.capture_logging and not configured.capture_warnings
assert set(CODES) <= set(manager.get_codes())
providers = manager.get_providers()
ensure_configured(PACKAGE_ROOT)
ensure_configured(PACKAGE_ROOT)
assert manager.get_providers() == providers
message, hint = smonitor.resolve(code='ACKREDIT-W001', profile='agent', extra={'path': 'fixture.json'})
assert message and manager.config is configured
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    bundle.warn(SessionLoadWarning(extra={'path': 'fixture.json'}))
assert len(caught) == 1 and caught[0].message.code == 'ACKREDIT-W001'
events = [e for e in handler.events if e.get('code') == 'ACKREDIT-W001']
assert events and events[-1]['extra']['path'] == 'fixture.json'
assert manager.config is configured
print(json.dumps({'application_policy_preserved': True, 'catalog_codes': len(CODES)}))
""",
        tmp_path,
        receiving_python,
    )
    assert result["application_policy_preserved"] and result["catalog_codes"] > 0


@pytest.mark.parametrize("selection", ["ambient", "decorator"])
def test_restrictive_capture_keeps_pipeline_native_failure_and_each_result(
    scoped_providers, receiving_python, tmp_path, selection
):
    code = """
import json
from types import ModuleType
from contextlib import nullcontext
import smonitor
from smonitor.handlers import MemoryHandler
handler = MemoryHandler()
smonitor.configure(level='DEBUG', handlers=[handler], args_summary=True,
    capture_logging=False, capture_warnings=False)
import ackredit
from ackredit._private.smonitor.exceptions import ArgumentError
from argdigest import arg_digest
from argdigest.core.errors import UnknownArgumentError
class Payload:
    def __init__(self, failed=False):
        self.failed = failed
        self.repr_calls = self.str_calls = 0
    def __repr__(self):
        self.repr_calls += 1
        return 'RECEIVING_OPAQUE_MARKER'
    def __str__(self):
        self.str_calls += 1
        return 'RECEIVING_OPAQUE_MARKER'
class NativeError(ValueError):
    def __init__(self):
        super().__init__('RECEIVING_NATIVE_MARKER')
        self.str_calls = 0
    def __str__(self):
        self.str_calls += 1
        return 'RECEIVING_NATIVE_MARKER'
native = NativeError()
cause = LookupError('original cause')
native.__cause__ = cause
calls = []
def normalize(value, ctx):
    assert ctx.value is value
    if value.failed:
        raise native
    return 3
selection = SELECTION
@arg_digest.map(capture_policy='metadata_only' if selection == 'decorator' else 'detailed',
    argument_digestion=False, value={'kind': 'receiving', 'rules': [normalize]})
def calculate(value):
    calls.append(value)
    return value * value
provider = ModuleType('diagnostic_receiving_provider')
provider.calculate = original = calculate
provider.__ackredit__ = {
    'schema': 'ackredit.provider@1',
    'software': {'name': provider.__name__, 'version': '1.0'},
    'items': [{'id': 'receiving:method', 'type': 'article', 'title': 'Original method'}],
    'functions': {'calculate': [{'item_id': 'receiving:method', 'roles': ['function_entry']}]},
}
values = [Payload(), Payload(True), Payload()]
scope = smonitor.diagnostic_scope() if selection == 'ambient' else nullcontext()
with scope, ackredit.session('receiving'), ackredit.observe_calls(provider):
    results = []
    for index, value in enumerate(values):
        with ackredit.capture(str(index)) as captured:
            if value.failed:
                try:
                    provider.calculate(value)
                except NativeError as error:
                    assert error is native and error.__cause__ is cause
                else:
                    raise AssertionError('the original failure was swallowed')
            else:
                assert provider.calculate(value) == 9
        results.append(captured.attribution)
    assert calls == [3, 3]
    try:
        ackredit.bind('invalid', 'receiving:method')
    except ArgumentError as error:
        assert error.code and ackredit.bound_items('invalid') == []
    else:
        raise AssertionError('Ackredit argument validation was bypassed')
    try:
        provider.calculate(Payload(), unexpected=True)
    except UnknownArgumentError:
        pass
    else:
        raise AssertionError('provider binding was bypassed')
assert provider.calculate is original
assert all(v.repr_calls == v.str_calls == 0 for v in values)
assert native.str_calls == 0
pipeline_events = [e for e in handler.events if e.get('code') == 'ARG-DBG-PIPELINE-001']
assert pipeline_events and pipeline_events[-1]['extra']['argname'] == 'value'
serialized = json.dumps(pipeline_events)
assert 'RECEIVING_OPAQUE_MARKER' not in serialized and 'RECEIVING_NATIVE_MARKER' not in serialized
for attribution in results:
    data = attribution.to_dict()
    assert {item['id'] for item in data['items']} == {'receiving:method'}
    assert data['items'][0]['title'] == 'Original method'
    with ackredit.session('saved reader'):
        restored = ackredit.Attribution.from_json(attribution.to_json())
        assert restored.to_dict() == data
        assert 'Original method' in restored.report(format='bibtex')
        assert ackredit.get_used_items() == {}
print(json.dumps({'independent_results': len(results), 'native_failure_preserved': True,
    'value_conversions': sum(v.repr_calls + v.str_calls for v in values)}))
""".replace("SELECTION", repr(selection))
    result = _child(code, tmp_path, receiving_python)
    assert result == {
        "independent_results": 3,
        "native_failure_preserved": True,
        "value_conversions": 0,
    }
