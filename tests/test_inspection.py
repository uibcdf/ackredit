"""Static analysis says what a function would cite; only running it says whether.

`auto_track_calls` used to record the credit while reading the source, so
importing a module was enough to cite work it never did — the failure mode
Ackredit exists to prevent.
"""

import warnings

import pytest

import ackredit
from ackredit._private.smonitor.warnings import SourceInspectionWarning
from ackredit.core.collector import Collector
from ackredit.core.inspection import auto_track_calls


def mdtraj_load():
    return "loaded"


@pytest.fixture(autouse=True)
def _isolated():
    Collector.used_items.clear()
    Collector.used_targets.clear()
    Collector.usage_tree.clear()
    yield


def _uses_mdtraj():
    return mdtraj_load()


MAP = {"mdtraj_load": "external:mdtraj"}


def test_nothing_is_credited_until_the_function_runs():
    auto_track_calls(_uses_mdtraj, MAP)

    assert ackredit.get_used_items() == {}


def test_running_it_credits_the_detected_item():
    wrapped = auto_track_calls(_uses_mdtraj, MAP)

    assert ackredit.get_used_items() == {}
    wrapped()

    assert ackredit.get_used_items() == {"external:mdtraj": ["_uses_mdtraj"]}


def test_the_return_value_is_not_swallowed():
    wrapped = auto_track_calls(_uses_mdtraj, MAP)

    assert wrapped() == "loaded"


def test_repeated_calls_credit_the_caller_once():
    wrapped = auto_track_calls(_uses_mdtraj, MAP)

    for _ in range(5):
        wrapped()

    assert ackredit.get_used_items() == {"external:mdtraj": ["_uses_mdtraj"]}


def test_the_provenance_tree_records_where_the_item_came_from():
    """The credit now happens inside a scope, so the tree shows the caller."""
    wrapped = auto_track_calls(_uses_mdtraj, MAP)
    wrapped()

    assert "_uses_mdtraj" in Collector.used_targets
    assert Collector.usage_tree["_uses_mdtraj"]["items"] == {"external:mdtraj"}


def test_identity_is_preserved():
    wrapped = auto_track_calls(_uses_mdtraj, MAP)

    assert wrapped.__name__ == "_uses_mdtraj"
    assert wrapped.__doc__ == _uses_mdtraj.__doc__


def test_a_function_calling_nothing_mapped_is_returned_untouched():
    """No wrapper, so no cost on a function that has nothing to credit."""
    assert auto_track_calls(_uses_mdtraj, {"something_else": "x"}) is _uses_mdtraj


def test_several_items_for_one_call_are_all_credited():
    wrapped = auto_track_calls(_uses_mdtraj, {"mdtraj_load": ["a:one", "a:two"]})
    wrapped()

    assert set(ackredit.get_used_items()) == {"a:one", "a:two"}


def test_unreadable_source_is_reported_and_costs_nothing():
    """A function defined in a REPL or by a C extension has no retrievable
    source. Detection finds nothing, the reason is reported, and the caller
    gets their function back."""
    from_string = eval("lambda: mdtraj_load()")  # noqa: S307 - deliberate

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = auto_track_calls(from_string, MAP)

    assert result is from_string
    assert [
        w.message.code for w in caught if isinstance(w.message, SourceInspectionWarning)
    ] == ["ACKREDIT-W010"]
    assert ackredit.get_used_items() == {}


def test_a_branch_that_is_not_taken_is_still_credited():
    """Pinned deliberately: detection is per function, not per branch.

    This is the same coarseness as `credit_bound=True`, and the documented
    remedy is the same — call track_item() on the branch that needs it. The
    test exists so the limitation is explicit rather than discovered.
    """

    def _conditional(use_it):
        if use_it:
            mdtraj_load()

    wrapped = auto_track_calls(_conditional, MAP)
    wrapped(use_it=False)

    credited = ackredit.get_used_items()
    assert list(credited) == ["external:mdtraj"]
    # Attributed by qualified name, so two methods called `run` stay apart.
    assert credited["external:mdtraj"] == [_conditional.__qualname__]


def test_a_method_is_analysed_like_any_other_function():
    """A method's source arrives carrying its class's indentation, which
    ast.parse rejects. Every method was invisible to detection, which is most
    of what a scientific library has to cite."""

    class Converter:
        def convert(self):
            return mdtraj_load()

    Converter.convert = auto_track_calls(Converter.convert, MAP)
    Converter().convert()

    credited = ackredit.get_used_items()
    assert list(credited) == ["external:mdtraj"]
    assert credited["external:mdtraj"][0].endswith("Converter.convert")


def test_attribution_is_by_qualified_name():
    class First:
        def run(self):
            return mdtraj_load()

    class Second:
        def run(self):
            return mdtraj_load()

    First.run = auto_track_calls(First.run, MAP)
    Second.run = auto_track_calls(Second.run, MAP)
    First().run()
    Second().run()

    callers = ackredit.get_used_items()["external:mdtraj"]
    assert len(callers) == 2, callers
    assert len(set(callers)) == 2
