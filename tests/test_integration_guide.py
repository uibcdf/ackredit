"""The integration guide's template must work, in both of its modes.

`standards/ACKREDIT_GUIDE.md` is the file host libraries copy into `_ackredit.py`.
Its whole purpose is that a host keeps working when Ackredit is absent, and its
`try`/`except ImportError` hides any mistake in it: a broken import looks exactly
like a missing package. These tests execute the template instead of trusting it.
"""

import inspect
import sys
from pathlib import Path

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
