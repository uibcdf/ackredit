"""A public class promises its whole surface unless it says otherwise.

`Session` exposed `record_item`, `record_target` and `lock` alongside the three
mappings a caller actually wants. They are the writers the collector uses and
the lock they require, and promising them would promise the rule that a caller
holds the lock before calling them.

Its stated reason for being provisional also said the journal had "no migration
story yet", while the same page had carried one since `uibcdf/ackredit#33`.
"""

import pytest

import ackredit
from ackredit.core.session import Session

PROMISED = {
    "used_items",
    "used_targets",
    "usage_tree",
    "journal_path",
    "name",
    "clear",
}


@pytest.fixture
def run():
    with ackredit.session("a-run") as session:
        ackredit.register_item(id="a:1", title="A Work")
        # Through a scope, because crediting a caller records the caller in the
        # tree and only entering a target records it as one that ran.
        with ackredit.scope("caller"):
            ackredit.track_item("a:1")
        yield session


def test_a_session_promises_these_and_no_more():
    """Asked of an instance, which is what a caller holds: the mappings are
    attributes set in __init__ and do not exist on the class."""
    public = {name for name in dir(Session("probe")) if not name.startswith("_")}
    assert public == PROMISED


@pytest.mark.parametrize("name", ["record_item", "record_target", "lock"])
def test_the_machinery_is_private(name):
    """The writers carry the rule that a caller holds the lock, and promising
    them would promise that rule."""
    instance = Session("probe")
    assert not hasattr(instance, name), f"{name} is public again"
    assert hasattr(instance, f"_{name}"), f"_{name} is missing"


@pytest.mark.parametrize("name", sorted(PROMISED))
def test_each_promised_name_is_there(run, name):
    assert hasattr(run, name)


def test_what_a_caller_reads_from_a_session(run):
    assert run.name == "a-run"
    assert run.used_items == {"a:1": ["caller"]}
    assert "caller" in run.used_targets
    assert run.usage_tree["caller"]["items"] == {"a:1"}
    assert run.journal_path is None


def test_clearing_forgets_what_was_tracked(run):
    run.clear()
    assert run.used_items == {}
    assert run.used_targets == set()
    assert run.usage_tree == {}


def test_the_page_does_not_contradict_itself():
    """Its reason said the journal had no migration story, on a page that
    states one two sections below."""
    from pathlib import Path

    page = (
        Path(__file__).resolve().parents[1] / "docs/content/about/stability.md"
    ).read_text(encoding="utf-8")

    assert "reads every session format it has ever written" in page
    assert "no migration story" not in page
