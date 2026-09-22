"""`__all__` is the statement of what the library promises to keep.

Anything public beside it is something a user can come to depend on and a
maintainer can remove without noticing they broke it. It accumulates silently:
an import added for the module's own setup joins the namespace, and
`ackredit.version` — `importlib.metadata.version`, one tab-completion from
`__version__` — answered plausibly and wrongly what Ackredit's own version is.
"""

import types

import pytest

import ackredit


def _public_names():
    return [name for name in dir(ackredit) if not name.startswith("_")]


def test_nothing_public_is_undeclared():
    """Submodules are reachable by convention and are not part of the promise."""
    undeclared = [
        name
        for name in _public_names()
        if name not in ackredit.__all__
        and not isinstance(getattr(ackredit, name), types.ModuleType)
    ]

    assert not undeclared, (
        f"public but not in __all__: {undeclared}. Either declare them or bind "
        "them privately; an accidental export is still an export."
    )


def test_nothing_declared_is_missing():
    missing = [name for name in ackredit.__all__ if not hasattr(ackredit, name)]

    assert not missing, f"declared in __all__ but absent: {missing}"


@pytest.mark.parametrize("name", sorted(ackredit.__all__))
def test_every_declared_name_belongs_to_ackredit(name):
    """A re-exported third-party name is a promise about someone else's code."""
    obj = getattr(ackredit, name)
    module = getattr(obj, "__module__", None)
    if module is None:  # __version__ and other plain values
        return

    assert module.split(".")[0] == "ackredit", (
        f"{name} comes from {module}; exporting it promises to keep another "
        "project's API stable"
    )


def test_the_version_is_not_shadowed_by_a_lookup_function():
    """The specific trap this file exists for."""
    assert not hasattr(ackredit, "version")
    assert isinstance(ackredit.__version__, str)


@pytest.mark.parametrize("name", ["Registry", "Collector"])
def test_the_state_holders_are_not_public(name):
    """They hold the same kind of state and were exported alike, and nothing
    Ackredit teaches used either: no mention in the integration guide, none in
    the example libraries, and in the documentation only under the developer
    guide. The supported surface is the functions in front of them.

    Leaving them out of `__all__` while still reachable would contradict the
    rule above: an accidental export is still an export.
    """
    assert name not in ackredit.__all__
    assert not hasattr(ackredit, name), f"ackredit.{name} is still reachable"


@pytest.mark.parametrize(
    "module,name",
    [("ackredit.core.registry", "Registry"), ("ackredit.core.collector", "Collector")],
)
def test_the_state_holders_are_where_they_always_were(module, name):
    from importlib import import_module

    assert hasattr(import_module(module), name)


def test_the_supported_readers_answer_what_the_classes_would():
    """Removing a name is only safe if what it was used for is still asked."""
    ackredit.register_item(id="x:1", title="A Work")
    ackredit.bind("a.target", ["x:1"])
    ackredit.track_item("x:1", used_by="a.caller")

    assert ackredit.bound_items("a.target") == ["x:1"]
    assert ackredit.get_used_items() == {"x:1": ["a.caller"]}


@pytest.mark.parametrize("name", sorted(ackredit.__all__))
def test_no_public_name_is_a_bound_method(name):
    """`ackredit.enable_persistence` *was* `Collector.enable_persistence`.

    Its sibling `close_persistence` was a function, so `help()` described one as
    a method of a class and the other as a function, for two calls used
    together. Worse, an alias binds a public name to the identity of `Collector`,
    a class the stability page calls provisional and whose state is now only a
    view onto the current session.

    A public name is a function or a class. If it is a method, the class it
    belongs to is part of the promise whether that was intended or not.
    """
    obj = getattr(ackredit, name)
    assert not isinstance(obj, types.MethodType), (
        f"ackredit.{name} is {obj.__qualname__}, a bound method. Give it a "
        f"delegating function beside the others in ackredit/core/collector.py"
    )


def test_the_removed_server_is_gone_from_everywhere():
    """`serve_ui` was removed in `uibcdf/ackredit#57`: an HTTP server inside a
    citation library is surface with an indefinite cost, for something
    `summary()` answers in a notebook and `report()` answers anywhere.

    Removing a name is not removing a feature unless what it rested on goes
    too, so this checks the declaration as well as the export.
    """
    from pathlib import Path

    from ackredit._depdigest import LIBRARIES

    assert "serve_ui" not in ackredit.__all__
    assert not hasattr(ackredit, "serve_ui")
    assert "flask" not in LIBRARIES, "it would still be reported as a feature"

    root = Path(ackredit.__file__).parent
    assert not (root / "contrib/web_ui.py").exists()
    assert not [
        path
        for path in root.rglob("*.py")
        if "flask" in path.read_text(encoding="utf-8")
    ]
