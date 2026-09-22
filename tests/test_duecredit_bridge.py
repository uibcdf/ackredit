"""Handing citations over to DueCredit must hand over all of them.

`export_to_duecredit` skipped a tracked item that was not in the registry.
Every other renderer reports one: `bibtex` emits a minimal `@misc`, `markdown`,
`json` and `csl-json` use the id as the title. This was the one path in the
library that dropped a tracked citation and said nothing, which the diagnostics
policy does not allow.

DueCredit is an optional dependency and is not installed here, so these run
against a stand-in that records what it is given. That is enough: what is under
test is which citations Ackredit hands over and in what shape, not what
DueCredit does with them.
"""

import sys
import types
from importlib.machinery import ModuleSpec

import pytest

import ackredit


class Recorder:
    def __init__(self):
        self.calls = []

    def cite(self, entry, description=None, path=None):
        self.calls.append({"entry": entry, "description": description, "path": path})


@pytest.fixture
def duecredit(monkeypatch, clean_registry):
    """A stand-in for DueCredit, visible to `importlib.util.find_spec`."""

    class Doi:
        def __init__(self, value):
            self.value = value

    class BibTeX:
        def __init__(self, value):
            self.value = value

    entries = types.ModuleType("duecredit.entries")
    entries.__spec__ = ModuleSpec("duecredit.entries", None)
    entries.Doi, entries.BibTeX = Doi, BibTeX

    module = types.ModuleType("duecredit")
    # DepDigest resolves the dependency with find_spec, which refuses a module
    # in sys.modules whose __spec__ is None.
    module.__spec__ = ModuleSpec("duecredit", None)
    module.due = Recorder()
    module.entries = entries

    monkeypatch.setitem(sys.modules, "duecredit", module)
    monkeypatch.setitem(sys.modules, "duecredit.entries", entries)

    # DepDigest memoises `is_installed` for the life of the process, which is
    # right for a library — a package does not appear mid-run — and wrong for a
    # test that makes one appear. Without clearing it on the way out, every
    # later test is told duecredit is installed and meets the real ImportError
    # instead of the diagnostic.
    from depdigest.core.checker import is_installed

    is_installed.cache_clear()
    yield module
    is_installed.cache_clear()


def test_an_item_that_was_never_registered_is_still_handed_over(duecredit):
    """The defect: it was skipped, and nothing said so."""
    ackredit.track_item("never:registered", used_by="run")
    ackredit.export_to_duecredit()

    (call,) = duecredit.due.calls
    assert call["path"].endswith("never:registered")
    assert call["description"] == "never:registered"


def test_every_tracked_item_is_handed_over(duecredit):
    ackredit.register_item(id="a:1", type="article", title="A Paper", doi="10.1/x")
    ackredit.register_item(id="b:1", type="software", title="A Tool")
    for item_id in ("a:1", "b:1", "c:1"):
        ackredit.track_item(item_id, used_by="run")

    ackredit.export_to_duecredit()

    assert len(duecredit.due.calls) == 3


def test_an_item_with_a_doi_is_handed_over_as_a_doi(duecredit):
    ackredit.register_item(id="a:1", type="article", title="A Paper", doi="10.1/x")
    ackredit.track_item("a:1", used_by="run")
    ackredit.export_to_duecredit()

    (call,) = duecredit.due.calls
    assert type(call["entry"]).__name__ == "Doi"
    assert call["entry"].value == "10.1/x"


def test_an_item_without_a_doi_is_handed_over_as_bibtex(duecredit):
    ackredit.register_item(id="b:1", type="software", title="A Tool")
    ackredit.track_item("b:1", used_by="run")
    ackredit.export_to_duecredit()

    (call,) = duecredit.due.calls
    assert type(call["entry"]).__name__ == "BibTeX"
    assert "A Tool" in call["entry"].value


def test_the_description_is_the_title(duecredit):
    ackredit.register_item(id="a:1", type="article", title="A Paper", doi="10.1/x")
    ackredit.track_item("a:1", used_by="run")
    ackredit.export_to_duecredit()

    assert duecredit.due.calls[0]["description"] == "A Paper"


def test_one_item_failing_does_not_cost_the_others(duecredit):
    """Export continues with the remaining items, which ACKREDIT-W013 says."""
    from ackredit._private.smonitor.warnings import DueCreditExportWarning

    original = duecredit.due.cite

    def cite(entry, description=None, path=None):
        if description == "Explodes":
            raise RuntimeError("duecredit said no")
        original(entry, description=description, path=path)

    duecredit.due.cite = cite

    ackredit.register_item(id="bad:1", type="article", title="Explodes", doi="10.1/x")
    ackredit.register_item(id="good:1", type="article", title="Fine", doi="10.1/y")
    for item_id in ("bad:1", "good:1"):
        ackredit.track_item(item_id, used_by="run")

    with pytest.warns(DueCreditExportWarning):
        ackredit.export_to_duecredit()

    assert [call["description"] for call in duecredit.due.calls] == ["Fine"]


# --- what the bridge promises ---------------------------------------------


def test_duecredits_api_does_not_reach_our_contract():
    """It was provisional for being "a bridge to another project's API, which
    we do not control". DueCredit appears nowhere in what we promise: a change
    there is adapted inside the function."""
    import inspect

    signature = inspect.signature(ackredit.export_to_duecredit)
    assert not signature.parameters
    assert signature.return_annotation in (None, inspect.Signature.empty)


def test_it_returns_nothing(duecredit):
    ackredit.register_item(id="a:1", type="article", title="A Paper", doi="10.1/x")
    ackredit.track_item("a:1", used_by="run")
    assert ackredit.export_to_duecredit() is None


def test_the_only_error_it_raises_is_ours(monkeypatch, clean_registry):
    """With duecredit absent, `@dep_digest` raises Ackredit's own exception
    rather than letting an ImportError out."""
    import sys

    from ackredit._private.smonitor.exceptions import AckreditError

    monkeypatch.setitem(sys.modules, "duecredit", None)
    from depdigest.core.checker import is_installed

    is_installed.cache_clear()
    monkeypatch.delitem(sys.modules, "duecredit")
    is_installed.cache_clear()

    with pytest.raises(AckreditError):
        ackredit.export_to_duecredit()


def test_a_failure_inside_duecredit_stays_a_warning(duecredit, clean_registry):
    """Whatever DueCredit raises reaches the caller as ACKREDIT-W013."""
    from ackredit._private.smonitor.warnings import DueCreditExportWarning

    class TheirError(Exception):
        pass

    def cite(entry, description=None, path=None):
        raise TheirError("something changed on their side")

    duecredit.due.cite = cite
    ackredit.register_item(id="a:1", type="article", title="A Paper", doi="10.1/x")
    ackredit.track_item("a:1", used_by="run")

    with pytest.warns(DueCreditExportWarning):
        ackredit.export_to_duecredit()
