"""The integration guide's template must work, in both of its modes.

`standards/ACKREDIT_GUIDE.md` is the file host libraries copy into `_ackredit.py`.
Its whole purpose is that a host keeps working when Ackredit is absent, and its
`try`/`except ImportError` hides any mistake in it: a broken import looks exactly
like a missing package. These tests execute the template instead of trusting it.
"""

import inspect
import sys
from pathlib import Path
from types import ModuleType

import pytest

import ackredit

GUIDE = Path(__file__).resolve().parents[1] / "standards" / "ACKREDIT_GUIDE.md"
MARKER = "### Template for `_ackredit.py`:"

# Names the template promises to export, and that a host may therefore rely on.
EXPORTED_CALLABLES = (
    "register_item",
    "bind",
    "bound_items",
    "add_injection",
    "credit_bound",
    "track_item",
    "scoped_usage",
    "report",
)


def test_portable_capture_example_runs_and_reads_without_new_credit(clean_registry):
    text = GUIDE.read_text(encoding="utf-8")
    section = text.split("### Portable calculation capture", 1)[1]
    source = section.split("```python", 1)[1].split("```", 1)[0]
    namespace = {}
    exec(compile(source, "<portable_capture_guide>", "exec"), namespace)
    assert (
        namespace["result_references"]["items"]
        == namespace["workflow_references"]["items"]
    )
    assert "Example" in namespace["bibliography"]
    assert ackredit.get_used_items() == {}


def _section_example(heading):
    text = GUIDE.read_text(encoding="utf-8")
    section = text.split(heading, 1)[1]
    return section.split("```python", 1)[1].split("```", 1)[0]


def test_provider_guide_records_software_and_article_only_on_entry(
    clean_registry, monkeypatch
):
    declaration = _section_example("### Dependency-free provider declaration")
    provider = ModuleType("example_provider")
    # A provider must still work when Ackredit cannot be imported.
    monkeypatch.setitem(sys.modules, "ackredit", None)
    exec(compile(declaration, "<provider_guide>", "exec"), provider.__dict__)
    original = provider.normalize
    assert provider.normalize([1, 3]) == [0.25, 0.75]
    assert ackredit.get_used_items() == {}
    monkeypatch.setitem(sys.modules, "ackredit", ackredit)
    monkeypatch.setitem(sys.modules, "example_provider", provider)

    source = _section_example("### Explicit application observation")
    namespace = {}
    exec(compile(source, "<observer_guide>", "exec"), namespace)
    assert namespace["values"] == [0.25, 0.75]
    assert provider.normalize is original
    saved = ackredit.Attribution.from_json(namespace["saved_references"]).to_dict()
    assert {item["id"] for item in saved["items"]} == {
        "example:software:2.4.0",
        "example:method",
    }
    assert {role for use in saved["uses"] for role in use["roles"]} == {
        "executed_software",
        "software_description",
    }
    assert "Example method" in namespace["bibliography"]
    assert ackredit.get_used_items() == {}


@pytest.mark.parametrize("fails", [False, True])
def test_prepared_guide_preserves_science_and_credits_only_after_completion(
    clean_registry, fails
):
    source = _section_example(
        "### Explicit fixed credit at the host's completion boundary"
    )
    failure = ValueError("scientific failure")

    def backend_convert(values):
        assert ackredit.get_used_items() == {}  # preparation must be inert
        if fails:
            raise failure
        return [value * 2 for value in values]

    namespace = {"backend_convert": backend_convert}
    if fails:
        with pytest.raises(ValueError) as caught:
            exec(compile(source, "<prepared_guide>", "exec"), namespace)
        assert caught.value is failure
        assert namespace["run"].attribution.to_dict()["items"] == []
    else:
        exec(compile(source, "<prepared_guide>", "exec"), namespace)
        assert namespace["converted"] == [2, 6]
        saved = ackredit.Attribution.from_json(namespace["saved_references"])
        assert saved.to_dict()["items"][0]["version"] == "2"
        assert saved.to_dict()["uses"][0]["used_by"] == "host.convert"
    assert ackredit.get_used_items() == {}


def _template_source() -> str:
    text = GUIDE.read_text(encoding="utf-8")
    assert MARKER in text, f"{GUIDE.name} no longer contains the template marker"
    return text.split(MARKER, 1)[1].split("```python", 1)[1].split("```", 1)[0]


def _run_template(*, ackredit_available: bool) -> dict:
    """Execute the template, optionally with the ackredit import made to fail."""
    namespace: dict = {}
    source = compile(_template_source(), "<ackredit_guide_template>", "exec")

    if ackredit_available:
        exec(source, namespace)
        return namespace

    # A None entry in sys.modules makes `import ackredit` raise ImportError,
    # which is exactly what the template must survive.
    saved = {
        name: module
        for name, module in sys.modules.items()
        if name == "ackredit" or name.startswith("ackredit.")
    }
    for name in saved:
        sys.modules[name] = None
    try:
        exec(source, namespace)
    finally:
        sys.modules.update(saved)
    return namespace


def _shape(function) -> list[tuple]:
    """Parameter names, kinds and whether each has a default. Ignores annotations."""
    parameters = list(inspect.signature(function).parameters.values())
    if parameters and parameters[0].name == "self":
        parameters = parameters[1:]
    return [
        (p.name, p.kind, p.default is not inspect.Parameter.empty) for p in parameters
    ]


def test_the_template_imports_names_that_actually_exist():
    """The documented import must not raise; the except clause would hide it."""
    namespace = _run_template(ackredit_available=True)

    assert namespace["ACKREDIT_INSTALLED"] is True
    assert namespace["ackredit"] is ackredit
    for name in (*EXPORTED_CALLABLES, "scope"):
        assert callable(namespace[name]), name


def test_the_template_survives_ackredit_being_absent():
    namespace = _run_template(ackredit_available=False)

    assert namespace["ACKREDIT_INSTALLED"] is False
    assert namespace["ackredit"] is None
    for name in (*EXPORTED_CALLABLES, "scope"):
        assert callable(namespace[name]), name


@pytest.mark.parametrize("name", EXPORTED_CALLABLES)
def test_fallback_signatures_match_the_real_ones(name):
    """A host that calls a keyword the shim lacks breaks exactly when Ackredit is
    missing, which is the case the pattern exists to protect."""
    fallback = _run_template(ackredit_available=False)[name]
    real = getattr(ackredit, name)

    assert _shape(fallback) == _shape(real), (
        f"the {name} fallback in {GUIDE.name} has drifted from the real signature"
    )


def test_the_scope_fallback_matches_and_is_a_context_manager():
    fallback = _run_template(ackredit_available=False)["scope"]

    assert _shape(fallback.__init__) == _shape(ackredit.scope.__init__)
    with fallback("some_block") as entered:
        assert entered is not None
    with fallback("some_block", credit_bound=True):
        pass


def test_fallbacks_return_types_host_code_can_use():
    """Returning None where the real API returns a list would break host loops."""
    namespace = _run_template(ackredit_available=False)

    assert namespace["bound_items"]("anything") == []
    assert namespace["credit_bound"]("anything") == []
    assert isinstance(namespace["report"](), str)

    @namespace["scoped_usage"]("some.target", credit_bound=True)
    def decorated():
        return "host still works"

    assert decorated() == "host still works"


def test_every_diagnostic_the_guide_promises_exists():
    """The guide tells a host which codes it will see. A code that does not
    exist is worse than an undocumented one: the host filters for something
    that never arrives, and believes it is covered."""
    import re

    from ackredit._private.smonitor import CODES

    guide = Path(__file__).resolve().parents[1] / "standards" / "ACKREDIT_GUIDE.md"
    promised = set(
        re.findall(r"`(ACKREDIT-[EW]\d+)`", guide.read_text(encoding="utf-8"))
    )

    assert promised, "the guide documents no diagnostics at all"
    missing = sorted(code for code in promised if code not in CODES)
    assert not missing, f"the guide promises codes that do not exist: {missing}"


def test_the_guide_says_what_ackredit_is_before_how_to_wire_it():
    """It opened at "1. Centralization File", so a maintainer finding that file
    appear in their repository had no way to know what it was for."""
    guide = Path(__file__).resolve().parents[1] / "standards" / "ACKREDIT_GUIDE.md"
    text = guide.read_text(encoding="utf-8")

    for section in (
        "## What is Ackredit",
        "## Why this matters in this library",
        "## Required behavior (non-negotiable)",
    ):
        assert section in text, f"the guide has no {section!r} section"

    assert text.index("## What is Ackredit") < text.index("## 1. Centralization File")
