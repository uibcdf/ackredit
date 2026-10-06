"""Offline citation use must not initialize network or PDF execution support."""

import subprocess
import sys

import pytest


@pytest.mark.parametrize("operation", ["report", "cached_enrichment", "missing_pdf"])
def test_offline_operations_leave_feature_imports_deferred(tmp_path, operation):
    code = """
import importlib.metadata, json, pathlib, sys, warnings
# Third-party citation/format code has its own import requirements. Exercise
# Ackredit's built-in operations with no installed plugins, in a fresh process.
importlib.metadata.entry_points = lambda **kwargs: ()
import ackredit
ackredit.register_item(id='local', doi='10.1/local',
                      title='' if sys.argv[1] == 'cached_enrichment' else 'Local reference')
ackredit.track_item('local')
if sys.argv[1] == 'cached_enrichment':
    from ackredit.core.registry import Registry, _cache_name
    Registry._get_cache_dir = classmethod(lambda cls: pathlib.Path.cwd())
    pathlib.Path(_cache_name('10.1/local') + '.json').write_text(
        json.dumps({'title': ['Cached title']}))
    ackredit.enrich_all()
    assert Registry.items['local']['title'] == 'Cached title'
elif sys.argv[1] == 'missing_pdf':
    from ackredit._private.smonitor.warnings import PdfCompilationWarning
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        assert ackredit.compile_pdf(pathlib.Path.cwd()) is None
    assert any(issubclass(w.category, PdfCompilationWarning) for w in caught)
else:
    assert 'Local reference' in ackredit.report(format='text')
assert 'argdigest' in sys.modules
assert 'smonitor' in sys.modules
assert not {'urllib.request', 'ssl', 'subprocess'} & sys.modules.keys()
"""
    subprocess.run(
        [sys.executable, "-c", code, operation],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
