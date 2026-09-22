"""Anyone can add an output format.

`devguide/vision.md` listed that as a design pillar and only half of it was
true: injections were extensible through `add_injection` and the
`ackredit.citations` entry-point group, formats were a private module dict. A
group that needs its report in the shape its journal wants had to reach into a
name the stability page says may change without notice.

The rule that matters here is that a name is never replaced. Letting a plugin
take over `bibtex` would make a request succeed and return a report that is not
the one asked for, which is exactly the defect `ACKREDIT-E004` exists to
prevent.
"""

import json
from importlib import import_module, metadata

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import (
    FormatNameTakenError,
    InvalidFormatError,
    UnknownFormatError,
)
from ackredit._private.smonitor.warnings import FormatPluginWarning

# `ackredit.core.report` the attribute is the function, which shadows the
# module of the same name, so the module is fetched from sys.modules.
report_module = import_module("ackredit.core.report")


def render_ids(used, items):
    return "IDS: " + ", ".join(sorted(used))


@pytest.fixture(autouse=True)
def _restore_the_format_table():
    original = dict(report_module._RENDERERS)
    loaded = report_module._PLUGINS_LOADED
    ackredit.register_item(id="a:1", title="A Work")
    ackredit.track_item("a:1")
    yield
    report_module._RENDERERS.clear()
    report_module._RENDERERS.update(original)
    report_module._PLUGINS_LOADED = loaded


class FakeEntryPoint:
    """What `importlib.metadata` hands back, with only what is used."""

    def __init__(self, name, target):
        self.name = name
        self._target = target
        self.loads = 0

    def load(self):
        self.loads += 1
        return self._target


def provide(monkeypatch, *entry_points):
    """Make `ackredit.formats` resolve to *entry_points*, and force a scan."""
    monkeypatch.setattr(
        metadata,
        "entry_points",
        lambda group=None: list(entry_points) if group == "ackredit.formats" else [],
    )
    report_module._PLUGINS_LOADED = False


# --- registering by hand --------------------------------------------------


def test_a_registered_format_renders():
    ackredit.register_format("ids", render_ids, "txt")
    assert ackredit.report(format="ids") == "IDS: a:1"


def test_a_registered_format_is_advertised():
    ackredit.register_format("ids", render_ids, "txt")
    assert "ids" in ackredit.available_formats()


def test_a_registered_format_reaches_dump(tmp_path):
    ackredit.register_format("ids", render_ids, "ids.txt")
    ackredit.dump(tmp_path, formats=["ids"])
    written = list(tmp_path.iterdir())
    assert [path.name for path in written] == ["ackredit_report.ids.txt"]
    assert written[0].read_text() == "IDS: a:1"


def test_an_unknown_format_still_refuses_and_lists_what_exists():
    ackredit.register_format("ids", render_ids, "txt")
    with pytest.raises(UnknownFormatError) as raised:
        ackredit.report(format="idz")
    assert "ids" in str(raised.value)


# --- what a name may not do ----------------------------------------------


@pytest.mark.parametrize("taken", sorted(report_module._RENDERERS))
def test_a_built_in_name_cannot_be_replaced(taken):
    with pytest.raises(FormatNameTakenError):
        ackredit.register_format(taken, render_ids, "txt")


def test_an_alias_cannot_be_taken_either():
    """`csl` resolves to `csl-json`, so taking it would shadow a real format."""
    with pytest.raises(FormatNameTakenError):
        ackredit.register_format("csl", render_ids, "txt")


def test_the_built_in_still_works_after_a_refused_attempt():
    """The refusal must leave the table as it was, not half-written."""
    with pytest.raises(FormatNameTakenError):
        ackredit.register_format("bibtex", render_ids, "txt")
    assert ackredit.report(format="bibtex").startswith("@")


def test_one_plugin_cannot_take_another_plugins_name():
    ackredit.register_format("ids", render_ids, "txt")
    with pytest.raises(FormatNameTakenError):
        ackredit.register_format("ids", render_ids, "txt")


@pytest.mark.parametrize(
    "name,renderer,extension,expected",
    [
        ("BibTeXish", render_ids, "txt", "lower case"),
        ("has space", render_ids, "txt", "lower case"),
        ("-leading", render_ids, "txt", "lower case"),
        ("", render_ids, "txt", "lower case"),
        (None, render_ids, "txt", "lower case"),
        ("ok", "not callable", "txt", "not callable"),
        ("ok", render_ids, "", "file extension"),
        ("ok", render_ids, ".", "file extension"),
    ],
)
def test_a_format_that_cannot_work_is_refused_with_a_reason(
    name, renderer, extension, expected
):
    with pytest.raises(InvalidFormatError) as raised:
        ackredit.register_format(name, renderer, extension)
    assert expected in str(raised.value)


# --- arriving through an entry point --------------------------------------


def test_a_format_from_an_entry_point_renders(monkeypatch):
    provide(
        monkeypatch,
        FakeEntryPoint(
            "mine", lambda: ackredit.register_format("ids", render_ids, "txt")
        ),
    )
    assert ackredit.report(format="ids") == "IDS: a:1"


def test_a_plugin_may_ship_several_formats(monkeypatch):
    def register():
        ackredit.register_format("ids", render_ids, "txt")
        ackredit.register_format("count", lambda used, items: str(len(used)), "txt")

    provide(monkeypatch, FakeEntryPoint("mine", register))
    assert ackredit.report(format="ids") == "IDS: a:1"
    assert ackredit.report(format="count") == "1"


def test_a_broken_plugin_is_reported_and_costs_nothing_else(monkeypatch):
    def explode():
        raise RuntimeError("this plugin is broken")

    provide(
        monkeypatch,
        FakeEntryPoint("broken", explode),
        FakeEntryPoint(
            "working", lambda: ackredit.register_format("ids", render_ids, "txt")
        ),
    )

    with pytest.warns(FormatPluginWarning, match="broken"):
        formats = ackredit.available_formats()

    assert "ids" in formats, "the working plugin still registered"
    assert json.loads(ackredit.report(format="json")), "the built-ins still work"


def test_a_plugin_claiming_a_built_in_is_reported_not_obeyed(monkeypatch):
    provide(
        monkeypatch,
        FakeEntryPoint(
            "greedy", lambda: ackredit.register_format("bibtex", render_ids, "txt")
        ),
    )

    with pytest.warns(FormatPluginWarning, match="greedy"):
        ackredit.available_formats()

    assert ackredit.report(format="bibtex").startswith("@")


def test_the_distributions_are_scanned_once(monkeypatch):
    entry_point = FakeEntryPoint(
        "mine", lambda: ackredit.register_format("ids", render_ids, "txt")
    )
    provide(monkeypatch, entry_point)

    ackredit.available_formats()
    ackredit.available_formats()
    ackredit.report(format="ids")

    assert entry_point.loads == 1


def test_a_plugin_that_asks_what_exists_does_not_recurse(monkeypatch):
    """The flag is set before the work, so a register function may call back in."""

    def register():
        ackredit.register_format("ids", render_ids, "txt")
        assert "ids" in ackredit.available_formats()

    provide(monkeypatch, FakeEntryPoint("curious", register))
    assert ackredit.report(format="ids") == "IDS: a:1"


# --- what a renderer is handed --------------------------------------------


def test_a_renderer_cannot_empty_the_registry():
    """`report` used to pass `Registry.items` itself, and a renderer may come
    from anywhere now."""

    def vandal(used, items):
        items.clear()
        return "gone"

    ackredit.register_format("vandal", vandal, "txt")
    with pytest.raises(AttributeError):
        ackredit.report(format="vandal")

    assert "a:1" in ackredit.Registry.items


def test_a_renderer_cannot_rewrite_an_item():
    """A proxy over the mapping alone still lets an item be written through."""

    def vandal(used, items):
        items["a:1"]["title"] = "hijacked"
        return "gone"

    ackredit.register_format("vandal", vandal, "txt")
    with pytest.raises(TypeError):
        ackredit.report(format="vandal")

    assert ackredit.Registry.items["a:1"]["title"] == "A Work"


def test_what_a_renderer_is_handed():
    seen = {}

    def observer(used, items):
        seen["used"] = dict(used)
        seen["items"] = {key: dict(value) for key, value in items.items()}
        return ""

    # The file's fixture credits without a caller, so this says what it means.
    ackredit.track_item("a:1", used_by="a.caller")
    ackredit.register_format("observer", observer, "txt")
    ackredit.report(format="observer")

    assert seen["used"] == {"a:1": ["a.caller"]}
    assert seen["items"]["a:1"]["title"] == "A Work"


def test_writing_to_the_used_map_changes_nothing():
    """It is a copy, built fresh by get_used_items."""

    def vandal(used, items):
        used.clear()
        return "gone"

    ackredit.track_item("a:1", used_by="a.caller")
    ackredit.register_format("vandal", vandal, "txt")
    ackredit.report(format="vandal")

    assert ackredit.get_used_items() == {"a:1": ["a.caller"]}


def test_an_id_that_was_never_registered_still_reaches_a_renderer():
    seen = {}

    def observer(used, items):
        seen["ids"] = sorted(used)
        seen["known"] = sorted(items)
        return ""

    ackredit.track_item("never:declared", used_by="run")
    ackredit.register_format("observer", observer, "txt")
    ackredit.report(format="observer")

    assert "never:declared" in seen["ids"]
    assert "never:declared" not in seen["known"]


# --- options --------------------------------------------------------------


def test_a_plugin_may_take_options():
    def mine(used, items, upper=False):
        out = ", ".join(sorted(used))
        return out.upper() if upper else out

    ackredit.register_format("mine", mine, "txt")
    assert ackredit.report(format="mine") == "a:1"
    assert ackredit.report(format="mine", upper=True) == "A:1"


def test_an_option_a_format_does_not_take_is_refused():
    """`report(format="bibtex", style="unsrt")` was accepted and the option
    discarded, which is the defect ACKREDIT-E004 exists to prevent."""
    from ackredit._private.smonitor.exceptions import UnknownFormatOptionError

    with pytest.raises(UnknownFormatOptionError) as raised:
        ackredit.report(format="bibtex", style="unsrt")

    assert "bibtex" in str(raised.value)
    assert "style" in str(raised.value)


def test_a_mistyped_option_names_the_format_and_what_it_takes():
    from ackredit._private.smonitor.exceptions import UnknownFormatOptionError

    with pytest.raises(UnknownFormatOptionError) as raised:
        ackredit.report(format="latex", stlye="typo")

    message = str(raised.value)
    assert "latex" in message and "stlye" in message
    assert "style" in message, "it says what the format does take"


def test_the_option_that_already_worked_still_does():
    assert "unsrt" in ackredit.report(format="latex", style="unsrt")
