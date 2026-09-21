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


def test_the_two_state_holders_are_exported_alike():
    """Registry and Collector hold the same kind of state; exporting one and
    not the other was an accident of which import line each arrived on."""
    assert "Registry" in ackredit.__all__
    assert "Collector" in ackredit.__all__


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
