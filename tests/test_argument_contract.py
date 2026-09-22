"""What a public function may be told, and what it refuses.

Six functions accepted arguments that could not be right and said nothing. The
two that did damage were `bind("t", "paper:2024")`, which bound eight citations
one per character, and `aggregate("session.json")`, which merged nothing while
warning about the paths `/` and `.` — a string is a sequence, so a forgotten
pair of brackets is iterated rather than refused.

ArgDigest is the suite's answer and Ackredit adopts it in `uibcdf/ackredit#62`,
where it fits. The decorator costs 11.71 µs against the 1.02 µs `track_item`
takes, so the tracking path is not decorated and checks inline instead; that
boundary is asserted here too, because it is the reason the adoption is partial.
"""

import inspect

import pytest
from argdigest.core.errors import UnknownArgumentError

import ackredit
from ackredit._private.smonitor.exceptions import ArgumentError
from ackredit.core.registry import Registry


@pytest.fixture(autouse=True)
def _clean(clean_registry):
    yield


# --- a string where a sequence is expected --------------------------------


@pytest.mark.parametrize(
    "call,argument",
    [
        (lambda: ackredit.bind("t", "paper:2024"), "items"),
        (lambda: ackredit.add_injection("numpy", "paper:2024"), "items"),
        (lambda: ackredit.aggregate("session.json"), "paths"),
        (lambda: ackredit.dump("out", formats="bibtex"), "formats"),
    ],
    ids=["bind", "add_injection", "aggregate", "dump"],
)
def test_a_string_is_refused_where_a_sequence_is_expected(call, argument):
    with pytest.raises(ArgumentError) as raised:
        call()
    assert argument in str(raised.value)


def test_the_measured_case(clean_registry):
    """`bind` bound eight citations, one per character."""
    with pytest.raises(ArgumentError):
        ackredit.bind("mylib.convert", "paper:2024")
    assert ackredit.bound_items("mylib.convert") == []


def test_a_real_sequence_is_accepted():
    ackredit.bind("mylib.convert", ["mylib:paper:2024"])
    assert ackredit.bound_items("mylib.convert") == ["mylib:paper:2024"]


# --- names that are not names ---------------------------------------------


@pytest.mark.parametrize(
    "call",
    [
        lambda: ackredit.bind(None, []),
        lambda: ackredit.bind("", []),
        lambda: ackredit.add_injection(None, []),
        lambda: ackredit.track_item(None),
        lambda: ackredit.track_item(""),
        lambda: ackredit.track_target(None),
    ],
    ids=[
        "bind-none",
        "bind-empty",
        "injection-none",
        "item-none",
        "item-empty",
        "target-none",
    ],
)
def test_a_name_that_is_not_one_is_refused(call):
    with pytest.raises(ArgumentError):
        call()


def test_tracking_nothing_does_not_reach_the_report():
    """`track_item(None)` put `{None: []}` in the report."""
    with pytest.raises(ArgumentError):
        ackredit.track_item(None)
    assert ackredit.get_used_items() == {}


# --- paths ----------------------------------------------------------------


@pytest.mark.parametrize(
    "call",
    [
        lambda: ackredit.load_bibtex(None),
        lambda: ackredit.enable_persistence(None),
        lambda: ackredit.dump(None),
        lambda: ackredit.compile_pdf(None),
    ],
    ids=["load_bibtex", "enable_persistence", "dump", "compile_pdf"],
)
def test_a_path_that_is_not_one_is_refused(call):
    """These used to raise a bare TypeError from inside pathlib, naming
    `__fspath__` rather than the argument."""
    with pytest.raises(ArgumentError):
        call()


# --- what a citation may be told ------------------------------------------


def test_a_reserved_key_is_refused(clean_registry):
    """`_source` tells the LaTeX escaper a field is already LaTeX, so setting it
    reaches straight past the escaping closed in #7 and #9."""
    with pytest.raises(UnknownArgumentError):
        ackredit.register_item(id="x:1", title="T", _source="bibtex")

    assert "x:1" not in Registry.items


def test_an_ordinary_field_is_accepted(clean_registry):
    ackredit.register_item(id="x:1", title="T", publisher="A Press", isbn="1-2-3")
    assert Registry.items["x:1"]["publisher"] == "A Press"


# --- options, which depend on the format ----------------------------------


def test_an_option_reaches_the_format_that_takes_it(clean_registry):
    ackredit.register_item(id="x:1", title="T")
    ackredit.track_item("x:1", used_by="run")
    assert "unsrt" in ackredit.report(format="latex", style="unsrt")


def test_an_option_a_format_does_not_take_is_refused(clean_registry):
    ackredit.register_item(id="x:1", title="T")
    ackredit.track_item("x:1", used_by="run")
    with pytest.raises(UnknownArgumentError):
        ackredit.report(format="bibtex", style="unsrt")


# --- where the decorator may not go ---------------------------------------


DECORATED = [
    "register_item",
    "bind",
    "add_injection",
    "load_bibtex",
    "aggregate",
    "enable_persistence",
    "scoped_usage",
    "register_format",
    "report",
    "dump",
    "compile_pdf",
    "dependency_info",
]
NOT_DECORATED = [
    "track_item",
    "track_target",
    "credit_bound",
    "bound_items",
    "get_used_items",
]


@pytest.mark.parametrize("name", DECORATED)
def test_declaration_and_reporting_are_digested(name):
    assert hasattr(getattr(ackredit, name), "__wrapped__"), f"{name} is not decorated"


@pytest.mark.parametrize("name", NOT_DECORATED)
def test_the_tracking_path_is_not_digested(name):
    """It runs once per credited citation, and the decorator costs 11.71 µs
    against the 1.02 µs `track_item` takes — the number
    `docs/content/about/performance.md` publishes."""
    function = getattr(ackredit, name)
    source = inspect.getsource(function)
    assert "arg_digest" not in source, f"{name} would pay the decorator per call"
