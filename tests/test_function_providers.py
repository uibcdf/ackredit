"""Actual calls, not imports or static branches, determine provider references."""

import asyncio
import importlib.util
import inspect
import json
import os
import shutil
import subprocess
import sys
import threading
from copy import deepcopy
from pathlib import Path

import pytest

import ackredit
from ackredit._private.smonitor.warnings import ProviderObservationWarning

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "citation_provider"


def test_declared_lazy_exports_are_resolved_only_on_activation(
    provider, clean_registry
):
    original = provider.normalize
    del provider.normalize
    requested = []

    def resolve(name):
        requested.append(name)
        if name == "normalize":
            provider.normalize = original
            return original
        raise AttributeError(name)

    provider.__getattr__ = resolve
    assert "normalize" not in vars(provider)
    with ackredit.observe_calls(provider), ackredit.capture() as run:
        assert requested == ["normalize"]
        assert ackredit.get_used_items() == {}
        assert provider.normalize([1, 3]) == [0.25, 0.75]
    assert len(run.attribution.to_dict()["items"]) == 2
    assert provider.normalize is original


def test_lazy_resolution_failure_is_diagnosed_before_observation(
    provider, clean_registry
):
    original = provider.normalize
    provider.__ackredit__["functions"]["missing"] = deepcopy(
        provider.__ackredit__["functions"]["normalize"]
    )

    def resolve(name):
        raise RuntimeError("producer resolution failed")

    provider.__getattr__ = resolve
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(provider):
            pass
    assert error.value.code == "ACKREDIT-E012"
    assert "producer resolution failed" in str(error.value)
    assert provider.normalize is original
    assert clean_registry.items == {}


def test_conflicting_function_metadata_on_lazy_export_is_refused(
    provider, clean_registry
):
    original = provider.normalize
    original.__ackredit__ = {
        "uses": [{"item_id": "example:article", "roles": ["other"]}]
    }
    del provider.normalize
    provider.__getattr__ = lambda name: original
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(provider):
            pass
    assert error.value.code == "ACKREDIT-E012"
    assert "conflicting declarations" in str(error.value)
    assert "normalize" not in vars(provider)
    assert clean_registry.items == {}


def test_prepared_provider_credits_use_the_existing_journal_writer(
    provider, clean_registry, tmp_path
):
    path = tmp_path / "journal.json"
    with ackredit.session("writer"):
        ackredit.enable_persistence(path)
        with ackredit.observe_calls(provider):
            provider.normalize([1, 3])
            provider.normalize([1, 3])
    with ackredit.session("reader"):
        ackredit.aggregate([path])
        used = ackredit.get_used_items()
        assert used == {
            "example:software:2.4.0": ["citation_provider.normalize"],
            "example:article": ["citation_provider.normalize"],
        }


def test_active_observation_keeps_detached_original_declaration(
    provider, clean_registry
):
    with ackredit.observe_calls(provider), ackredit.capture() as run:
        provider.__ackredit__["software"]["version"] = "mutated"
        provider.__ackredit__["items"][1]["title"] = "Mutated article"
        provider.__ackredit__["functions"]["normalize"][1]["roles"].append("mutated")
        provider.normalize([1, 3])
    data = run.attribution.to_dict()
    assert data["items"][1]["title"] == "A method for demonstration"
    assert data["uses"][1]["roles"] == ["software_description"]
    assert data["uses"][1]["context"]["version"] == "2.4.0"


def test_custom_module_is_refused_without_changing_exports(provider, clean_registry):
    from types import ModuleType

    class Custom(ModuleType):
        pass

    provider.__class__ = Custom
    original = provider.normalize
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(provider):
            pass
    assert error.value.code == "ACKREDIT-E012"
    assert provider.normalize is original
    assert clean_registry.items == {}


def test_two_concurrent_observers_share_wrapper_without_cross_credit(
    provider, clean_registry
):
    original = provider.normalize

    async def job(name):
        with ackredit.session(name), ackredit.capture(name) as run:
            with ackredit.observe_calls(provider):
                await asyncio.sleep(0)
                provider.normalize([1, 3])
                await asyncio.sleep(0)
        return run.attribution.to_dict()

    async def main():
        return await asyncio.gather(job("a"), job("b"))

    results = asyncio.run(main())
    assert [data["name"] for data in results] == ["a", "b"]
    assert all(len(data["uses"]) == 2 for data in results)
    assert provider.normalize is original


def test_unrelated_thread_calls_remain_unobserved(provider, clean_registry):
    result = []
    with ackredit.observe_calls(provider):
        thread = threading.Thread(
            target=lambda: result.append(provider.normalize([1, 3]))
        )
        thread.start()
        thread.join(timeout=5)
        assert not thread.is_alive()
    assert result == [[0.25, 0.75]]
    assert ackredit.get_used_items() == {}


def test_multi_provider_preflight_is_atomic(provider, clean_registry):
    original = provider.normalize
    from types import ModuleType

    broken = ModuleType("broken")
    with pytest.raises(ValueError):
        with ackredit.observe_calls(provider, broken):
            pass
    assert provider.normalize is original
    assert clean_registry.items == {}


def test_references_from_two_versions_can_share_a_description_article(
    provider, clean_registry
):
    from types import ModuleType

    second = ModuleType("second_provider")
    second.__ackredit__ = deepcopy(provider.__ackredit__)
    second.__ackredit__["software"]["version"] = "3.0"
    second.__ackredit__["items"][0].update(id="example:software:3.0", version="3.0")
    second.__ackredit__["functions"] = {
        "normalize": deepcopy(provider.__ackredit__["functions"]["normalize"])
    }
    second.__ackredit__["functions"]["normalize"][0]["item_id"] = "example:software:3.0"
    second.normalize = provider.normalize
    with ackredit.observe_calls(provider, second), ackredit.capture() as run:
        provider.normalize([1, 3])
        second.normalize([1, 3])
    data = run.attribution.to_dict()
    assert len(data["items"]) == 3
    uses = [use for use in data["uses"] if use["item_id"] == "example:article"]
    assert [use["context"]["version"] for use in uses] == ["2.4.0", "3.0"]


def test_tracking_engine_failure_is_diagnosed_and_original_exception_survives(
    provider, clean_registry, monkeypatch
):
    from ackredit.core import providers

    def failure(*args, **kwargs):
        raise RuntimeError("tracking engine failed")

    monkeypatch.setattr(providers, "_track_prepared_item", failure)
    with ackredit.observe_calls(provider), pytest.warns(ProviderObservationWarning):
        with pytest.raises(ZeroDivisionError):
            provider.normalize([0, 0])
    from ackredit.core.context import get_current_scope

    assert get_current_scope() is None


@pytest.fixture
def provider():
    spec = importlib.util.spec_from_file_location(
        "citation_provider", FIXTURE / "citation_provider.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_actual_calls_credit_software_and_paper_in_each_capture(
    provider, clean_registry
):
    original = provider.normalize
    signature = inspect.signature(original)
    with ackredit.session("workflow"), ackredit.scope("pipeline"):
        with ackredit.observe_calls(provider):
            assert ackredit.get_used_items() == {}
            assert inspect.signature(provider.normalize) == signature
            for name in ("first", "second"):
                with ackredit.capture(name) as result:
                    value = provider.normalize([1, 3], scale=2)
                    if False:
                        provider.unused()
                assert value == [0.5, 1.5]
                data = result.attribution.to_dict()
                assert {item["id"] for item in data["items"]} == {
                    "example:software:2.4.0",
                    "example:article",
                }
                assert [use["roles"] for use in data["uses"]] == [
                    ["executed_software"],
                    ["software_description"],
                ]
                assert all(use["context"]["version"] == "2.4.0" for use in data["uses"])
                assert (
                    "citation_provider.normalize"
                    in data["usage_tree"]["pipeline"]["children"]
                )
        assert provider.normalize is original
        assert len(ackredit.get_attribution().to_dict()["uses"]) == 2
    text = result.attribution.report(format="bibtex")
    assert "10.1234/demo" in text and "Untaken method" not in text
    assert "Ruiz" in text
    assert (
        ackredit.Attribution.from_json(result.attribution.to_json()).to_dict() == data
    )


def test_nested_observers_do_not_double_wrap_and_restore(provider, clean_registry):
    original = provider.normalize
    with ackredit.observe_calls(provider, provider):
        outer = provider.normalize
        with ackredit.observe_calls(provider):
            assert provider.normalize is outer
            provider.normalize([2, 2])
        assert provider.normalize is outer
    assert provider.normalize is original


def test_preexisting_alias_is_explicitly_unobserved_and_expired_wrapper_is_inactive(
    provider, clean_registry
):
    alias = provider.normalize
    with ackredit.observe_calls(provider):
        wrapped = provider.normalize
        assert alias([1, 1]) == [0.5, 0.5]
        assert ackredit.get_used_items() == {}
    wrapped([1, 1])
    assert ackredit.get_used_items() == {}


def test_scientific_failure_is_preserved_and_scope_is_restored(
    provider, clean_registry
):
    original = provider.normalize
    with ackredit.scope("parent"), ackredit.capture() as run:
        with pytest.raises(ZeroDivisionError):
            with ackredit.observe_calls(provider):
                provider.normalize([0, 0])
        ackredit.track_item("after")
    assert provider.normalize is original
    assert run.attribution.to_dict()["uses"][-1]["used_by"] == "parent"
    assert len(run.attribution.to_dict()["items"]) == 3


def test_coroutine_only_credits_when_awaited_and_tasks_are_context_local(
    provider, clean_registry
):
    async def main():
        ready = asyncio.Event()
        release = asyncio.Event()

        async def tracked():
            with ackredit.session("tracked"), ackredit.capture() as run:
                with ackredit.observe_calls(provider):
                    coroutine = provider.async_normalize([1, 3])
                    assert ackredit.get_used_items() == {}
                    ready.set()
                    await release.wait()
                    assert await coroutine == [0.25, 0.75]
            return run.attribution.to_dict()

        async def untracked():
            await ready.wait()
            with ackredit.session("untracked"), ackredit.capture() as run:
                assert await provider.async_normalize([1, 3]) == [0.25, 0.75]
            release.set()
            return run.attribution.to_dict()

        return await asyncio.gather(tracked(), untracked())

    tracked, untracked = asyncio.run(main())
    assert len(tracked["items"]) == 2
    assert untracked["items"] == []
    assert (
        "citation_provider.normalize"
        in tracked["usage_tree"]["citation_provider.async_normalize"]["children"]
    )


def test_child_task_cannot_credit_after_observer_lease_expires(
    provider, clean_registry
):
    async def main():
        gate = asyncio.Event()

        async def child():
            await gate.wait()
            provider.normalize([1, 1])

        with ackredit.observe_calls(provider):
            task = asyncio.create_task(child())
        gate.set()
        await task

    asyncio.run(main())
    assert ackredit.get_used_items() == {}


@pytest.mark.parametrize(
    "mutation",
    [
        lambda p: p.__ackredit__.update(schema="ackredit.provider@2"),
        lambda p: p.__ackredit__["functions"].update(missing=[]),
        lambda p: p.__ackredit__["functions"]["normalize"][0].update(item_id="missing"),
        lambda p: p.__ackredit__["functions"]["normalize"][0].update(roles="software"),
        lambda p: p.__ackredit__["items"].append(deepcopy(p.__ackredit__["items"][0])),
        lambda p: p.__ackredit__["software"].update(version=""),
        lambda p: p.__ackredit__["items"][0].update(bad=float("nan")),
        lambda p: setattr(p.normalize, "__ackredit__", {"uses": []}),
    ],
)
def test_invalid_declarations_are_atomic(provider, mutation, clean_registry):
    original = provider.normalize
    mutation(provider)
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(provider):
            pass
    assert error.value.code == "ACKREDIT-E012"
    assert provider.normalize is original
    assert clean_registry.items == {}
    assert ackredit.get_used_items() == {}


@pytest.mark.parametrize("module", [None, "citation_provider", [], {}])
def test_non_module_inputs_get_catalog_diagnostic(module):
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(module):
            pass
    assert error.value.code == "ACKREDIT-E012"


def test_generator_is_refused_before_patching(provider, clean_registry):
    def yielding():
        yield 1

    provider.yielding = yielding
    provider.__ackredit__["functions"]["yielding"] = provider.__ackredit__["functions"][
        "unused"
    ]
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(provider):
            pass
    assert error.value.code == "ACKREDIT-E012"
    assert clean_registry.items == {}


def test_registry_and_active_declaration_conflicts_do_not_overwrite(
    provider, clean_registry
):
    ackredit.register_item(id="example:article", title="Other work")
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(provider):
            pass
    assert error.value.code == "ACKREDIT-E012"
    assert clean_registry.items["example:article"]["title"] == "Other work"
    clean_registry.items.clear()
    with ackredit.observe_calls(provider):
        wrapped = provider.normalize
        provider.__ackredit__["software"]["version"] = "9"
        with pytest.raises(ValueError):
            with ackredit.observe_calls(provider):
                pass
        assert provider.normalize is wrapped


def test_registered_tuple_metadata_matches_public_observation(provider, clean_registry):
    declared = provider.__ackredit__["items"][1]
    ackredit.register_item(**dict(declared, authors=tuple(declared["authors"])))
    registered = clean_registry.items[declared["id"]]
    context = {"software": "Citation Example", "version": "2.4.0"}
    with ackredit.session("public"), ackredit.capture("result") as public:
        with ackredit.scope("citation_provider.normalize"):
            for use in provider.__ackredit__["functions"]["normalize"]:
                if use["item_id"] != declared["id"]:
                    record = next(
                        i
                        for i in provider.__ackredit__["items"]
                        if i["id"] == use["item_id"]
                    )
                    ackredit.register_item(**record)
                ackredit.track_item(
                    use["item_id"],
                    used_by="citation_provider.normalize",
                    roles=use["roles"],
                    context=context,
                )
    original = provider.normalize
    for name in ("first", "reused"):
        with ackredit.session(name), ackredit.capture("result") as observed:
            with ackredit.observe_calls(provider):
                with ackredit.observe_calls(provider):
                    assert ackredit.get_used_items() == {}
                    assert provider.normalize([1, 3]) == [0.25, 0.75]
        assert observed.attribution.to_dict() == public.attribution.to_dict()
        assert clean_registry.items[declared["id"]] is registered
        assert registered["authors"] == ("Ruiz, Ana",)
        assert provider.normalize is original


@pytest.mark.parametrize("change", ["replace", "delete"])
def test_changed_tuple_registration_reports_a_gap(provider, clean_registry, change):
    declared = provider.__ackredit__["items"][1]
    ackredit.register_item(**dict(declared, authors=tuple(declared["authors"])))
    with ackredit.observe_calls(provider), ackredit.capture() as run:
        if change == "replace":
            clean_registry.items[declared["id"]]["authors"] = ("Changed, Author",)
        else:
            del clean_registry.items[declared["id"]]
        with pytest.warns(ProviderObservationWarning) as warnings:
            assert provider.normalize([1, 3]) == [0.25, 0.75]
        assert warnings[0].message.code == "ACKREDIT-W019"
    assert run.attribution.to_dict()["items"] == []


def test_nonportable_existing_registry_is_refused_before_activation(
    provider, clean_registry
):
    declared = provider.__ackredit__["items"][1]
    ackredit.register_item(**dict(declared, extra=object()))
    registered = clean_registry.items[declared["id"]]
    original = provider.normalize
    with pytest.raises(ValueError) as error:
        with ackredit.observe_calls(provider):
            pass
    assert error.value.code == "ACKREDIT-E012"
    assert provider.normalize is original
    assert clean_registry.items == {declared["id"]: registered}
    assert ackredit.get_used_items() == {}


def test_registered_provider_normalization_stays_in_activation(
    provider, clean_registry, monkeypatch
):
    providers = sys.modules["ackredit.core.providers"]
    normalize = providers._json_copy
    normalizations = []

    def counted(*args):
        normalizations.append(args[1])
        return normalize(*args)

    monkeypatch.setattr(providers, "_json_copy", counted)
    declared = provider.__ackredit__["items"][1]
    declared["authors"] = [{"family": "Ruiz", "given": "Ana"}]
    ackredit.register_item(**dict(declared, authors=tuple(declared["authors"])))
    with ackredit.observe_calls(provider):
        at_activation = len(normalizations)
        assert at_activation > 0
        for name in ("first", "reused"):
            with ackredit.capture(name) as run:
                assert provider.normalize([1, 3]) == [0.25, 0.75]
            assert len(run.attribution.to_dict()["items"]) == 2
        # The runtime comparison must own nested author data independently.
        clean_registry.items[declared["id"]]["authors"][0]["family"] = "Changed"
        with ackredit.capture("gap") as run, pytest.warns(ProviderObservationWarning):
            assert provider.normalize([1, 3]) == [0.25, 0.75]
        assert run.attribution.to_dict()["items"] == []
        assert len(normalizations) == at_activation


def test_tracking_failure_reports_gap_without_changing_scientific_result(
    provider, clean_registry
):
    with ackredit.observe_calls(provider):
        ackredit.register_item(id="example:article", title="Replaced")
        with pytest.warns(ProviderObservationWarning) as warnings:
            assert provider.normalize([1, 3]) == [0.25, 0.75]
        assert warnings[0].message.code == "ACKREDIT-W019"
        assert ackredit.get_used_items() == {}


def test_export_rebinding_is_preserved_and_diagnosed(provider, clean_registry):
    def replacement():
        return "new export"

    with pytest.warns(ProviderObservationWarning) as warnings:
        with ackredit.observe_calls(provider):
            provider.normalize = replacement
    assert provider.normalize is replacement
    assert warnings[0].message.extra["operation"] == "restore export"


def test_observer_can_only_be_entered_once(provider, clean_registry):
    run = ackredit.observe_calls(provider)
    with run:
        pass
    with pytest.raises(ValueError):
        with run:
            pass


def test_normally_installed_provider_and_reader_outside_checkout(tmp_path):
    """Install the producer as a wheel; a separate reader cannot import it."""
    target = tmp_path / "installed"
    build_environment = tmp_path / "minimal-build-interpreter"
    created = subprocess.run(
        [sys.executable, "-m", "venv", str(build_environment)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert created.returncode == 0, created.stderr
    build_python = build_environment / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python"
    )
    checked = subprocess.run(
        [
            str(build_python),
            "-c",
            "import importlib.util; assert importlib.util.find_spec('versioningit') is None",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 0, checked.stderr
    source = tmp_path / "producer"
    shutil.copytree(
        FIXTURE,
        source,
        ignore=shutil.ignore_patterns("build", "*.egg-info", "__pycache__"),
    )
    result = subprocess.run(
        [
            str(build_python),
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(target),
            str(source),
            str(Path(__file__).resolve().parents[1]),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    script = """
import importlib.abc, importlib.metadata, pathlib, sys
sys.path.insert(0, sys.argv[1])
class NoAckredit(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "ackredit" or fullname.startswith("ackredit."):
            raise ModuleNotFoundError(fullname)
blocked = NoAckredit()
sys.meta_path.insert(0, blocked)
import citation_provider as provider
assert provider.normalize([1, 3]) == [0.25, 0.75]
assert "ackredit" not in sys.modules
distribution = importlib.metadata.distribution("ackredit-example-provider")
assert distribution.version == "2.4.0"
assert not distribution.requires
sys.meta_path.remove(blocked)
import ackredit
from ackredit.core.registry import Registry
original = provider.normalize
declaration = ackredit.validate_provider(provider)
assert provider.normalize is original
assert ackredit.get_used_items() == {}
assert Registry.items == {}
assert declaration["software"] == {"name": "Citation Example", "version": "2.4.0"}
assert "async_normalize" in declaration["functions"]
with ackredit.observe_calls(provider), ackredit.capture("installed") as run:
    assert run.attribution.to_dict()["items"] == []
    provider.normalize([1, 3])
assert provider.normalize is original
assert {item["id"] for item in run.attribution.to_dict()["items"]} == {
    "example:software:2.4.0", "example:article"
}
pathlib.Path(sys.argv[2]).write_text(run.attribution.to_json())
assert provider.__file__.startswith(sys.argv[1])
assert ackredit.__file__.startswith(sys.argv[1])
"""
    saved = tmp_path / "saved.json"
    result = subprocess.run(
        [sys.executable, "-c", script, str(target), str(saved)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    reader = """
import importlib.abc, pathlib, sys
sys.path.insert(0, sys.argv[2])
import ackredit
class NoProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "citation_provider":
            raise ModuleNotFoundError(fullname)
sys.meta_path.insert(0, NoProducer())
data = ackredit.Attribution.from_json(pathlib.Path(sys.argv[1]).read_text())
assert all(use["context"]["version"] == "2.4.0" for use in data.to_dict()["uses"])
assert "10.1234/demo" in data.report(format="bibtex")
assert "Untaken method" not in data.report()
assert ackredit.get_used_items() == {}
"""
    result = subprocess.run(
        [sys.executable, "-c", reader, str(saved), str(target)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(saved.read_text())["name"] == "installed"
