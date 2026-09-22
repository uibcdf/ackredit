"""Another package can ship citations, and that is a promise.

`load_plugins` reads the `ackredit.citations` entry-point group, and nothing
exercised it. Reading it found a branch for the dict `entry_points()` returned
before Python 3.10 — unreachable, since the supported range starts at 3.11, and
an `AttributeError` rather than a fallback if it ever had been.

These use a stand-in for the entry points, because a real one needs an
installed distribution. What is under test is which packs are loaded and what
happens when one fails, not how `importlib` finds them.
"""

from importlib import metadata

import pytest

import ackredit
from ackredit._private.smonitor.warnings import PluginLoadWarning
from ackredit.core.registry import Registry


class FakeEntryPoint:
    def __init__(self, name, target):
        self.name = name
        self._target = target
        self.loads = 0

    def load(self):
        self.loads += 1
        return self._target


@pytest.fixture(autouse=True)
def _clean(clean_registry):
    yield


def provide(monkeypatch, *entry_points):
    monkeypatch.setattr(
        metadata,
        "entry_points",
        lambda group=None: list(entry_points) if group == "ackredit.citations" else [],
    )


def a_pack(item_id="plug:1"):
    def register():
        ackredit.register_item(id=item_id, title="From a pack")

    return register


def test_a_pack_that_registers_is_loaded(monkeypatch):
    provide(monkeypatch, FakeEntryPoint("mine", a_pack()))
    ackredit.load_plugins()

    assert Registry.items["plug:1"]["title"] == "From a pack"


def test_several_packs_are_all_loaded(monkeypatch):
    provide(
        monkeypatch,
        FakeEntryPoint("one", a_pack("plug:1")),
        FakeEntryPoint("two", a_pack("plug:2")),
    )
    ackredit.load_plugins()

    assert {"plug:1", "plug:2"} <= set(Registry.items)


def test_a_pack_may_bind_and_inject(monkeypatch):
    """What a pack is expected to call, beyond registering."""

    def register():
        ackredit.register_item(id="plug:1", title="From a pack")
        ackredit.bind("host.target", ["plug:1"])
        ackredit.add_injection("numpy", ["plug:1"])

    provide(monkeypatch, FakeEntryPoint("mine", register))
    ackredit.load_plugins()

    assert ackredit.bound_items("host.target") == ["plug:1"]
    assert Registry.injections["numpy"] == ["plug:1"]


def test_a_broken_pack_is_reported_and_costs_nothing_else(monkeypatch):
    def explode():
        raise RuntimeError("this pack is broken")

    provide(
        monkeypatch,
        FakeEntryPoint("broken", explode),
        FakeEntryPoint("working", a_pack()),
    )

    with pytest.warns(PluginLoadWarning, match="broken"):
        ackredit.load_plugins()

    assert "plug:1" in Registry.items, "the pack beside it still loaded"


def test_a_pack_that_cannot_even_be_loaded_is_reported(monkeypatch):
    class Unloadable(FakeEntryPoint):
        def load(self):
            raise ImportError("no such module")

    provide(monkeypatch, Unloadable("absent", None))
    with pytest.warns(PluginLoadWarning, match="absent"):
        ackredit.load_plugins()


def test_loading_twice_is_safe(monkeypatch):
    """register_item overwrites and add_injection deduplicates, so a pack that
    only declares has no second effect."""

    def register():
        ackredit.register_item(id="plug:1", title="From a pack")
        ackredit.add_injection("numpy", ["plug:1"])

    provide(monkeypatch, FakeEntryPoint("mine", register))
    ackredit.load_plugins()
    ackredit.load_plugins()

    assert Registry.injections["numpy"] == ["plug:1"]
    assert len(Registry.items) == 1


def test_no_group_at_all_does_nothing(monkeypatch):
    provide(monkeypatch)
    assert ackredit.load_plugins() is None
    assert Registry.items == {}


def test_only_the_citation_group_is_read(monkeypatch):
    """`ackredit.formats` is a different promise, loaded elsewhere."""
    asked = []

    def entry_points(group=None):
        asked.append(group)
        return []

    monkeypatch.setattr(metadata, "entry_points", entry_points)
    ackredit.load_plugins()

    assert asked == ["ackredit.citations"]
