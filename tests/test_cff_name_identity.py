"""A producer's declared name identity survives reference-manager export."""

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from ackredit.core.cff import parse_cff
from ackredit.core.hooks import InjectionsFinder
from ackredit.formats.csl_json import render


def _export(data):
    item = {"id": "names:reference", **data}
    return json.loads(render({item["id"]: []}, {item["id"]: item}))[0]


@pytest.mark.parametrize(
    "field,csl_field", [("authors", "author"), ("editors", "editor")]
)
@pytest.mark.parametrize(
    "source,expected",
    [
        (
            "name: Research Unit, Example University",
            {"literal": "Research Unit, Example University"},
        ),
        ("name: Plato", {"literal": "Plato"}),
        ("family-names: Plato", {"family": "Plato"}),
        ("given-names: Plato", {"given": "Plato"}),
        (
            "family-names: Smith, Jr.\n    given-names: John",
            {"family": "Smith, Jr.", "given": "John"},
        ),
        (
            "family-names: Humboldt\n    given-names: Alexander\n    name-particle: von",
            {"family": "von Humboldt", "given": "Alexander"},
        ),
        (
            "family-names: Davis\n    given-names: Sammy\n    name-suffix: Jr.",
            {"family": "Davis", "given": "Sammy", "suffix": "Jr."},
        ),
        (
            "given-names: Alexander\n    name-particle: von\n    name-suffix: Jr.",
            {"literal": "Alexander von Jr."},
        ),
    ],
)
def test_declared_cff_name_identity_reaches_csl(field, csl_field, source, expected):
    data = parse_cff(f"title: Work\n{field}:\n  - {source}\n")
    assert _export(data)[csl_field] == [expected]
    assert not any(key.startswith("_") for key in _export(data))


def test_original_human_readable_names_remain_available():
    data = parse_cff(
        "title: Work\nauthors:\n  - name: Research Unit, Example University\n"
        "  - family-names: Smith, Jr.\n    given-names: John\n"
    )
    assert data["authors"] == ["Research Unit, Example University", "Smith, Jr., John"]


@pytest.mark.parametrize(
    "field,csl_field", [("authors", "author"), ("editors", "editor")]
)
def test_explicit_replacement_does_not_reuse_original_name_hints(field, csl_field):
    data = parse_cff(f"title: Work\n{field}:\n  - name: Research Unit, University\n")
    data[field] = ["Ruiz, Ana"]
    assert _export(data)[csl_field] == [{"family": "Ruiz", "given": "Ana"}]
    del data[field]
    assert csl_field not in _export(data)


def test_typed_preferred_work_owns_its_name_identity():
    data = parse_cff(
        "title: Software\nauthors:\n  - name: Root Team, University\n"
        "preferred-citation:\n  type: article\n  title: Article\n"
        "  authors:\n    - family-names: Plato\n"
    )
    assert _export(data)["author"] == [{"family": "Plato"}]
    assert "Root Team" not in json.dumps(data)


def test_untyped_partial_preferred_work_keeps_independent_name_fallbacks():
    data = parse_cff(
        "title: Software\nauthors:\n  - name: Root Team, University\n"
        "editors:\n  - name: Root Editor, University\npreferred-citation:\n"
        "  title: Preferred\n  editors:\n    - family-names: Plato\n"
    )
    assert _export(data)["author"] == [{"literal": "Root Team, University"}]
    assert _export(data)["editor"] == [{"family": "Plato"}]


def test_discovered_names_survive_a_producer_free_saved_reader(
    tmp_path, monkeypatch, clean_registry
):
    import ackredit

    name = "cff_name_producer"
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "CITATION.cff").write_text(
        "title: Original work\nauthors:\n"
        "  - name: Research Unit, Example University\n"
        "  - family-names: Davis\n    given-names: Sammy\n    name-suffix: Jr.\n"
        "    orcid: https://orcid.org/0000-0001-2345-6789\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    with ackredit.capture("result") as result:
        InjectionsFinder().find_spec(name, None)
    payload = result.attribution.to_dict()
    saved = tmp_path / "attribution.json"
    saved.write_text(result.attribution.to_json())
    script = """
import importlib.abc, json, pathlib, socket, sys, urllib.request
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'cff_name_producer':
            raise AssertionError('producer import')
sys.meta_path.insert(0, NoProducer())
def no_network(*a, **kw):
    raise AssertionError('network')
socket.create_connection = no_network
socket.socket.connect = no_network
urllib.request.urlopen = no_network
sys.path.insert(0, sys.argv[2])
import ackredit
saved = ackredit.Attribution.from_json(pathlib.Path(sys.argv[1]).read_text())
data = saved.to_dict()
names = json.loads(saved.report(format='csl-json'))[0]['author']
assert names == [{'literal': 'Research Unit, Example University'},
                 {'family': 'Davis', 'given': 'Sammy', 'suffix': 'Jr.'}]
assert 'https://orcid.org/0000-0001-2345-6789' in json.dumps(data)
assert 'Research Unit, Example University' in saved.report(format='workflow')
assert ackredit.get_used_items() == {}
assert 'cff_name_producer' not in sys.modules
"""
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
            str(saved),
            str(Path(ackredit.__file__).resolve().parent.parent),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    assert result.attribution.to_dict() == payload
