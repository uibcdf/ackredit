"""What `dependency_info` promises is DepDigest's shape, relayed on purpose.

It is `return get_info("ackredit", format=format)`, so the keys a caller reads
are DepDigest's. That was the reason it was the last provisional name, and the
decision was to promise it rather than remove it: the guide every host library
copies tells them to call it, and DepDigest does not have one shape but two.

The machine shape states its own version in the payload; the table is
capitalised keys with prose in the values, for a person. So the machine shape is
the promise, the table is a rendering, and the version relayed is verified —
a change on DepDigest's side is never handed over in silence.
"""

import json
from importlib import import_module

import pytest

import ackredit
from ackredit._private.smonitor.warnings import DependencySchemaWarning
from ackredit.core.report import _DEPENDENCY_SCHEMA

# `ackredit.core.report` the attribute is the function, which shadows the
# module of the same name, so the module is fetched from sys.modules.
report_module = import_module("ackredit.core.report")


# --- the promised shape ---------------------------------------------------


@pytest.mark.parametrize("fmt", ["dict", "json"])
def test_the_machine_shape_states_its_schema(fmt):
    info = ackredit.dependency_info(format=fmt)
    if isinstance(info, str):
        info = json.loads(info)

    assert info["schema"] == {"name": "depdigest.get_info", "version": "1.0"}


@pytest.mark.parametrize("fmt", ["dict", "json"])
def test_the_machine_shape_lists_each_library(fmt):
    info = ackredit.dependency_info(format=fmt)
    if isinstance(info, str):
        info = json.loads(info)

    from ackredit._depdigest import LIBRARIES

    assert {entry["library"] for entry in info["dependencies"]} == set(LIBRARIES)
    for entry in info["dependencies"]:
        assert "installed" in entry
        assert entry["install"]["conda"]


def test_the_version_promised_is_the_one_documented():
    """The docstring names it, and so does the stability page."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    for relative in ("ackredit/core/report.py", "docs/content/about/stability.md"):
        text = (root / relative).read_text(encoding="utf-8")
        assert f"get_info@{_DEPENDENCY_SCHEMA}" in text


# --- the rendering --------------------------------------------------------


def test_the_table_still_answers():
    """Not promised, and still what the guide's advice returns by default."""
    entry = ackredit.dependency_info()[0]
    assert entry["Library"]
    assert entry["Status"]


def test_the_guides_advice_works():
    """`standards/ACKREDIT_GUIDE.md` tells a host to call this."""
    assert ackredit.dependency_info()


# --- a schema that is not the one promised --------------------------------


def _relay(monkeypatch, payload):
    monkeypatch.setattr(
        report_module, "get_info", lambda module_path, format="table": payload
    )
    return ackredit.dependency_info(format="dict")


def test_another_version_is_reported(monkeypatch):
    payload = {"schema": {"name": "depdigest.get_info", "version": "2.0"}}
    with pytest.warns(DependencySchemaWarning, match="2.0"):
        _relay(monkeypatch, payload)


def test_the_payload_is_still_returned(monkeypatch):
    """It states its own schema, so a caller who can read 2.0 still may."""
    payload = {"schema": {"name": "depdigest.get_info", "version": "2.0"}}
    with pytest.warns(DependencySchemaWarning):
        assert _relay(monkeypatch, payload) is payload


def test_a_json_string_is_checked_too(monkeypatch):
    payload = json.dumps({"schema": {"version": "3.1"}})
    with pytest.warns(DependencySchemaWarning, match="3.1"):
        _relay(monkeypatch, payload)


@pytest.mark.parametrize(
    "payload",
    [
        [{"Library": "x"}],
        {"no": "schema"},
        {"schema": {}},
        "not json at all",
        None,
    ],
    ids=["table", "no-schema", "empty-schema", "unparseable", "none"],
)
def test_a_payload_with_no_version_is_not_reported(monkeypatch, payload, recwarn):
    """The table carries none, and nothing else should be guessed at."""
    _relay(monkeypatch, payload)
    assert not [w for w in recwarn if isinstance(w.message, DependencySchemaWarning)]


def test_the_version_that_is_promised_is_not_reported(monkeypatch, recwarn):
    _relay(monkeypatch, {"schema": {"version": _DEPENDENCY_SCHEMA}})
    assert not [w for w in recwarn if isinstance(w.message, DependencySchemaWarning)]
