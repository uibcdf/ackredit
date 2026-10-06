"""Standalone declaration validation preserves observation semantics and state."""

import json
from copy import deepcopy
from types import ModuleType

import pytest

import ackredit
from ackredit.core import providers
from ackredit.core.registry import Registry


@pytest.fixture
def provider():
    module = ModuleType("validation_provider")
    module.__ackredit__ = {
        "schema": "ackredit.provider@1",
        "software": {"name": "Example", "version": "2.4.0"},
        "items": [
            {"id": "example:software:2.4.0", "title": "Example", "type": "software"},
            {"id": "example:paper", "title": "Method", "doi": "10.1234/offline"},
            {"id": "example:unused", "title": "Untaken method"},
        ],
        "functions": {
            "calculate": [
                {"item_id": "example:software:2.4.0", "roles": ["executed_software"]},
                {"item_id": "example:paper", "roles": ["software_description"]},
            ]
        },
    }

    def calculate():
        raise AssertionError("validation must not call science")

    module.calculate = calculate
    return module


def test_validating_does_not_activate_credit_registry_or_wrappers(
    provider, clean_registry, monkeypatch
):
    ackredit.register_item(id="host", title="Preserved host record")
    ackredit.track_item("host", "host.call")
    Registry.injections["host"] = ["host"]
    before_registry = deepcopy(Registry.items)
    before_injections = deepcopy(Registry.injections)
    before_attribution = ackredit.get_attribution().to_dict()
    before_exports = vars(provider).copy()

    def forbidden(*args, **kwargs):
        raise AssertionError("validation activated observation or enrichment")

    monkeypatch.setattr(providers, "_Patch", forbidden)
    monkeypatch.setattr(providers, "_track_prepared_item", forbidden)
    monkeypatch.setattr("ackredit.core.registry._fetch", forbidden)
    with ackredit.capture("validation", record_evidence=True) as capture:
        before_capture = capture.attribution.to_dict()
        declaration = ackredit.validate_provider(provider)
        assert capture.attribution.to_dict() == before_capture
    assert declaration == provider.__ackredit__
    assert json.loads(json.dumps(declaration)) == declaration
    assert vars(provider) == before_exports
    assert Registry.items == before_registry
    assert Registry.injections == before_injections
    assert ackredit.get_attribution().to_dict() == before_attribution
    assert not providers._patches
    assert not providers._observers.get()


def test_return_is_detached_and_validation_reads_changed_metadata(provider):
    provider.__ackredit__["items"][1]["authors"] = ("Ruiz, Ana",)
    original = deepcopy(provider.__ackredit__)
    declaration = ackredit.validate_provider(provider)
    assert declaration["items"][1]["authors"] == ["Ruiz, Ana"]
    declaration["software"]["version"] = "changed"
    declaration["items"][1]["title"] = "changed"
    declaration["functions"]["calculate"][0]["roles"].append("changed")
    assert provider.__ackredit__ == original
    provider.__ackredit__["software"]["version"] = "2.5.0"
    assert ackredit.validate_provider(provider)["software"]["version"] == "2.5.0"
    provider.__ackredit__["functions"]["calculate"][0]["item_id"] = "missing"
    with pytest.raises(ValueError, match="undeclared") as error:
        ackredit.validate_provider(provider)
    assert error.value.code == "ACKREDIT-E012"


def test_function_only_declaration_is_merged_and_can_be_reused(
    provider, clean_registry
):
    uses = deepcopy(provider.__ackredit__["functions"]["calculate"])
    uses[0]["roles"] = ["z", "a", "z"]
    provider.calculate.__ackredit__ = {"uses": uses}
    provider.__ackredit__["functions"] = {}
    declaration = ackredit.validate_provider(provider)
    assert provider.__ackredit__["functions"] == {}
    assert declaration["functions"]["calculate"] == uses
    declaration["functions"]["calculate"][0]["roles"].append("detached")
    assert provider.calculate.__ackredit__["uses"] == uses
    provider.__ackredit__ = ackredit.validate_provider(provider)
    original = provider.calculate
    with ackredit.observe_calls(provider):
        assert provider.calculate is not original
        assert not ackredit.get_used_items()
    assert provider.calculate is original


def test_empty_exports_keep_original_software_and_all_items(provider):
    provider.__ackredit__["functions"] = {}
    assert ackredit.validate_provider(provider) == provider.__ackredit__


def test_empty_role_list_keeps_unspecified_use_through_validation_and_saved_report(
    provider, clean_registry
):
    provider.__ackredit__["functions"]["calculate"] = [
        {"item_id": "example:paper", "roles": []}
    ]

    def calculate():
        return 7

    provider.calculate = calculate
    declaration = ackredit.validate_provider(provider)
    assert declaration["functions"]["calculate"][0]["roles"] == []
    assert provider.calculate is calculate
    assert not ackredit.get_used_items()
    assert not Registry.items
    declaration["functions"]["calculate"][0]["roles"].append("not-declared")
    assert provider.__ackredit__["functions"]["calculate"][0]["roles"] == []

    with ackredit.observe_calls(provider), ackredit.capture("unspecified-role") as run:
        assert provider.calculate() == 7
    assert provider.calculate is calculate
    original = run.attribution.to_dict()
    assert len(original["uses"]) == 1
    assert original["uses"][0]["item_id"] == "example:paper"
    assert original["uses"][0]["roles"] == []
    before = ackredit.get_attribution().to_dict()
    saved = ackredit.Attribution.from_json(run.attribution.to_json())
    assert saved.to_dict() == original
    assert "| Not recorded |" in saved.report(format="workflow")
    assert ackredit.get_attribution().to_dict() == before


def test_active_observer_and_capture_are_unchanged(provider, clean_registry):
    original = provider.calculate
    with ackredit.observe_calls(provider), ackredit.capture("existing") as capture:
        wrapped = provider.calculate
        bindings = dict(providers._patches)
        leases = {key: binding.leases for key, binding in bindings.items()}
        observers = providers._observers.get()
        registry = deepcopy(Registry.items)
        ackredit.validate_provider(provider)
        assert provider.calculate is wrapped
        assert providers._patches == bindings
        assert providers._observers.get() == observers
        assert {key: binding.leases for key, binding in bindings.items()} == leases
        assert Registry.items == registry
        assert not capture.attribution.to_dict()["uses"]
        provider.__ackredit__["functions"]["calculate"][0]["item_id"] = "missing"
        with pytest.raises(ValueError, match="undeclared"):
            ackredit.validate_provider(provider)
        assert provider.calculate is wrapped
        assert providers._patches == bindings
        assert providers._observers.get() == observers
        assert {key: binding.leases for key, binding in bindings.items()} == leases
        assert Registry.items == registry
        assert not capture.attribution.to_dict()["uses"]
    assert provider.calculate is original


def test_registry_conflict_is_separate_from_declaration_validation(
    provider, clean_registry
):
    ackredit.register_item(id="example:paper", title="Another paper")
    assert ackredit.validate_provider(provider) == provider.__ackredit__
    with pytest.raises(ValueError, match="conflicting registered reference"):
        with ackredit.observe_calls(provider):
            pytest.fail("registry-conflicting observation was activated")


def test_only_explicit_lazy_exports_are_resolved(provider, clean_registry):
    original = provider.calculate
    del provider.calculate
    requested = []

    def resolve(name):
        requested.append(name)
        assert name == "calculate"
        return original

    provider.__getattr__ = resolve
    provider.__dir__ = lambda: pytest.fail("validation swept exports")
    assert ackredit.validate_provider(provider) == provider.__ackredit__
    assert requested == ["calculate"]
    assert "calculate" not in vars(provider)
    assert not Registry.items
    assert not providers._patches


def test_lazy_resolution_failure_is_diagnosed(provider):
    del provider.calculate

    def resolve(name):
        if name == "calculate":
            raise RuntimeError("loader rejected")
        raise AttributeError(name)

    provider.__getattr__ = resolve
    with pytest.raises(ValueError, match="loader rejected") as error:
        ackredit.validate_provider(provider)
    assert error.value.code == "ACKREDIT-E012"
    assert "calculate" not in vars(provider)


def _generator():
    yield None


async def _async_generator():
    yield None


@pytest.mark.parametrize(
    "change",
    [
        lambda p: p.__ackredit__.update(schema="ackredit.provider@2"),
        lambda p: p.__ackredit__["software"].update(version=""),
        lambda p: p.__ackredit__["items"].append(p.__ackredit__["items"][0]),
        lambda p: p.__ackredit__["functions"]["calculate"][0].update(item_id="missing"),
        lambda p: p.__ackredit__["functions"]["calculate"][0].update(roles=[""]),
        lambda p: p.__ackredit__["functions"].update(calculate=[]),
        lambda p: p.__ackredit__["items"][0].update(version=float("nan")),
        lambda p: setattr(p, "calculate", object()),
        lambda p: setattr(p.calculate, "__ackredit__", {"uses": []}),
        lambda p: setattr(p, "calculate", _generator),
        lambda p: setattr(p, "calculate", _async_generator),
    ],
    ids=[
        "unknown-schema",
        "original-version",
        "duplicate-reference",
        "missing-reference",
        "empty-role",
        "empty-uses",
        "non-json",
        "not-function",
        "conflicting-function",
        "generator",
        "async-generator",
    ],
)
def test_validator_and_observer_refuse_the_same_input_without_mutating_state(
    provider, clean_registry, change
):
    change(provider)
    original = vars(provider).copy()
    ackredit.register_item(id="host", title="Preserved host record")
    ackredit.track_item("host", "host.call")
    registry = deepcopy(Registry.items)
    attribution = ackredit.get_attribution().to_dict()
    with ackredit.capture("refusal") as capture:
        with pytest.raises(ValueError) as validation:
            ackredit.validate_provider(provider)
        with pytest.raises(ValueError) as observation:
            with ackredit.observe_calls(provider):
                pytest.fail("invalid observation was activated")
        assert validation.value.code == observation.value.code == "ACKREDIT-E012"
        assert validation.value.extra == observation.value.extra
        assert not capture.attribution.to_dict()["uses"]
    assert vars(provider) == original
    assert Registry.items == registry
    assert ackredit.get_attribution().to_dict() == attribution
    assert not providers._patches


@pytest.mark.parametrize("value", [None, "validation_provider", {}, []])
def test_module_names_and_non_modules_are_refused(value):
    with pytest.raises(ValueError) as error:
        ackredit.validate_provider(value)
    assert error.value.code == "ACKREDIT-E012"


def test_custom_module_is_refused(provider):
    class CustomModule(ModuleType):
        pass

    provider.__class__ = CustomModule
    with pytest.raises(ValueError) as error:
        ackredit.validate_provider(provider)
    assert error.value.code == "ACKREDIT-E012"
