"""Real recorder events stay bounded to opted-in, overlapping captures."""

import asyncio
import importlib.util
import warnings
from copy import deepcopy
from pathlib import Path

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import (
    AttributionError,
    ProviderDeclarationError,
)
from ackredit._private.smonitor.warnings import ProviderObservationWarning


@pytest.fixture
def provider():
    spec = importlib.util.spec_from_file_location(
        "citation_provider",
        Path(__file__).parent / "fixtures/citation_provider/citation_provider.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def planes(run):
    return run.evidence.to_dict()["results"][0]


@pytest.mark.parametrize("capture_first", [False, True])
def test_selected_boundaries_do_not_imply_calls_or_citations(
    provider, clean_registry, capture_first
):
    from contextlib import ExitStack

    run = ackredit.capture(record_evidence=True)
    with ExitStack() as stack:
        contexts = [run, ackredit.observe_calls(provider)]
        for context in contexts if capture_first else reversed(contexts):
            stack.enter_context(context)
        assert run.attribution.to_dict()["items"] == []
    evidence = planes(run)
    assert {record["boundary"] for record in evidence["observation_scope"]} == {
        "citation_provider.normalize",
        "citation_provider.unused",
        "citation_provider.async_normalize",
    }
    assert {record["status"] for record in evidence["observation_scope"]} == {
        "selected"
    }
    assert evidence["metadata_origins"] is evidence["recording_gaps"] is None
    assert "function ran" in run.evidence.report()
    assert ackredit.get_used_items() == {}


def test_actual_credits_retain_activation_metadata_sources_and_original_fields(
    provider, clean_registry
):
    declared = deepcopy(provider.__ackredit__["items"])
    with (
        ackredit.observe_calls(provider),
        ackredit.capture(record_evidence=True) as run,
    ):
        # The observer credits its original detached activation declaration.
        provider.__ackredit__["items"][0]["title"] = "Changed after activation"
        provider.__name__ = "renamed_after_activation"
        assert provider.normalize([1, 3]) == [0.25, 0.75]
    saved = run.attribution.to_dict()
    assert saved["items"] == declared[:2]
    origins = planes(run)["metadata_origins"]
    assert [record["item_id"] for record in origins] == [
        item["id"] for item in declared[:2]
    ]
    assert all(
        record["source"] == "citation_provider.__ackredit__.items" for record in origins
    )
    assert all(record["method"] == "provider_declaration" for record in origins)
    assert [record["fields"] for record in origins] == [
        sorted(item) for item in declared[:2]
    ]
    assert all(ackredit.__version__ in record["recorder"] for record in origins)
    assert planes(run)["recording_gaps"] is None
    assert run.evidence.attribution.to_dict() == saved


def test_reused_calls_and_nested_captures_keep_bounded_origins_without_call_counts(
    provider, clean_registry
):
    with (
        ackredit.capture(record_evidence=True) as outer,
        ackredit.observe_calls(provider),
    ):
        runs = []
        for _ in range(3):
            with ackredit.capture("same", record_evidence=True) as inner:
                for _ in range(20):
                    assert provider.normalize([1, 3]) == [0.25, 0.75]
            runs.append(inner)
    assert len(outer.attribution.to_dict()["uses"]) == 2
    assert len(planes(outer)["metadata_origins"]) == 2
    assert len(planes(outer)["observation_scope"]) == 3
    for inner in runs:
        assert len(inner.attribution.to_dict()["items"]) == 2
        assert planes(inner) == planes(outer)
    assert "invocation counts" in outer.evidence.report()


def test_default_and_unobserved_captures_keep_unknown_planes_and_no_builder(
    provider, clean_registry, monkeypatch
):
    from ackredit.core import evidence

    def forbidden():
        raise AssertionError("default capture allocated an evidence collector")

    monkeypatch.setattr(evidence, "_ProviderEvidenceBuilder", forbidden)
    with ackredit.observe_calls(provider), ackredit.capture() as run:
        assert provider.normalize([1, 3]) == [0.25, 0.75]
    assert run._evidence_builder is None
    assert all(value is None for value in planes(run).values())
    assert len(run.attribution.to_dict()["items"]) == 2


def test_plain_credits_and_pre_activation_aliases_are_not_given_guessed_origins(
    provider, clean_registry
):
    alias = provider.normalize
    with ackredit.capture(record_evidence=True) as run:
        assert alias([1, 3]) == [0.25, 0.75]
        ackredit.register_item(id="explicit", title="Host declaration")
        ackredit.track_item("explicit")
    assert all(value is None for value in planes(run).values())
    with (
        ackredit.observe_calls(provider),
        ackredit.capture(record_evidence=True) as alias_run,
    ):
        assert alias([1, 3]) == [0.25, 0.75]
    assert planes(alias_run)["observation_scope"] is not None
    assert planes(alias_run)["metadata_origins"] is None
    assert alias_run.attribution.to_dict()["items"] == []


def test_replaced_registry_metadata_records_diagnosed_gap_and_preserves_science(
    provider, clean_registry
):
    with (
        ackredit.observe_calls(provider),
        ackredit.capture(record_evidence=True) as run,
    ):
        ackredit.register_item(id="example:article", title="Replaced")
        with pytest.warns(ProviderObservationWarning) as emitted:
            assert provider.normalize([1, 3]) == [0.25, 0.75]
    assert run.attribution.to_dict()["items"] == []
    gap = planes(run)["recording_gaps"][0]
    assert gap["boundary"] == "citation_provider.normalize"
    assert gap["diagnostic_owner"] == "ackredit"
    assert gap["diagnostic_code"] == emitted[0].message.code == "ACKREDIT-W019"
    assert planes(run)["metadata_origins"] is None
    # A saved explanation retains the gap without re-emitting its warning.
    with warnings.catch_warnings(record=True) as caught:
        restored = ackredit.AttributionEvidence.from_json(run.evidence.to_json())
        assert "ACKREDIT-W019" in restored.report()
    assert caught == []


def test_partial_tracking_failure_retains_only_successfully_credited_field_origins(
    provider, clean_registry, monkeypatch
):
    from ackredit.core import providers

    track = providers._track_prepared_item

    def partial(record, *args):
        if record["id"] == "example:article":
            raise RuntimeError("second reference cannot be recorded")
        return track(record, *args)

    monkeypatch.setattr(providers, "_track_prepared_item", partial)
    with (
        ackredit.capture(record_evidence=True) as run,
        ackredit.observe_calls(provider),
    ):
        with pytest.warns(ProviderObservationWarning):
            assert provider.normalize([1, 3]) == [0.25, 0.75]
    assert [record["id"] for record in run.attribution.to_dict()["items"]] == [
        "example:software:2.4.0"
    ]
    assert [origin["item_id"] for origin in planes(run)["metadata_origins"]] == [
        "example:software:2.4.0"
    ]
    assert planes(run)["recording_gaps"][0]["diagnostic_code"] == "ACKREDIT-W019"


def test_scientific_failure_does_not_become_a_recording_gap(provider, clean_registry):
    with (
        ackredit.capture(record_evidence=True) as run,
        ackredit.observe_calls(provider),
    ):
        with pytest.raises(ZeroDivisionError):
            provider.normalize([0, 0])
    assert len(planes(run)["metadata_origins"]) == 2
    assert planes(run)["recording_gaps"] is None
    assert len(run.attribution.to_dict()["uses"]) == 2


def test_export_rebinding_gap_is_retained_only_during_capture_overlap(
    provider, clean_registry
):
    def replacement():
        return "replacement"

    with ackredit.capture(record_evidence=True) as run:
        with pytest.warns(ProviderObservationWarning):
            with ackredit.observe_calls(provider):
                provider.normalize = replacement
    assert provider.normalize is replacement
    assert planes(run)["recording_gaps"][0]["boundary"] == "citation_provider.normalize"


def test_other_sessions_and_closed_captures_do_not_receive_new_evidence(
    provider, clean_registry
):
    with ackredit.session("outer"), ackredit.capture(record_evidence=True) as outer:
        with (
            ackredit.session("inner"),
            ackredit.observe_calls(provider),
            ackredit.capture(record_evidence=True) as inner,
        ):
            assert provider.normalize([1, 3]) == [0.25, 0.75]
    assert all(value is None for value in planes(outer).values())
    before = inner.evidence.to_dict()
    with ackredit.observe_calls(provider):
        provider.normalize([1, 3])
    assert inner.evidence.to_dict() == before
    assert len(planes(inner)["metadata_origins"]) == 2


def test_async_tasks_preserve_awaited_evidence_and_context_local_selection(
    provider, clean_registry
):
    async def selected():
        with (
            ackredit.session("selected"),
            ackredit.capture(record_evidence=True) as run,
            ackredit.observe_calls(provider),
        ):
            coroutine = provider.async_normalize([1, 3])
            assert planes(run)["metadata_origins"] is None
            await asyncio.sleep(0)
            assert await coroutine == [0.25, 0.75]
            return run.evidence

    async def unselected():
        with (
            ackredit.session("unselected"),
            ackredit.capture(record_evidence=True) as run,
        ):
            await asyncio.sleep(0)
            assert await provider.async_normalize([1, 3]) == [0.25, 0.75]
            return run.evidence

    async def both():
        return await asyncio.gather(selected(), unselected())

    first, second = asyncio.run(both())
    assert len(first.to_dict()["results"][0]["metadata_origins"]) == 2
    assert all(value is None for value in second.to_dict()["results"][0].values())


def test_invalid_generator_activation_does_not_invent_selected_boundaries(
    provider, clean_registry
):
    def generator():
        yield 1

    provider.normalize = generator
    with ackredit.capture(record_evidence=True) as run:
        with pytest.raises(ProviderDeclarationError):
            with ackredit.observe_calls(provider):
                pass
    assert all(value is None for value in planes(run).values())
    assert list(provider.normalize()) == [1]


@pytest.mark.parametrize("value", [None, 0, 1, "yes", []])
def test_capture_evidence_opt_in_requires_a_boolean(value):
    with pytest.raises(AttributionError) as error:
        ackredit.capture(record_evidence=value)
    assert error.value.code == "ACKREDIT-E010"


def test_detached_companion_and_original_reports_survive_later_registry_changes(
    provider, clean_registry
):
    with (
        ackredit.capture(record_evidence=True) as run,
        ackredit.observe_calls(provider),
    ):
        provider.normalize([1, 3])
    saved = run.evidence.to_json()
    workflow = run.attribution.report("workflow")
    clean_registry.items.clear()
    restored = ackredit.AttributionEvidence.from_json(saved)
    restored.to_dict()["results"][0]["metadata_origins"].clear()
    assert restored.to_json() == saved
    assert restored.report("workflow") == workflow
    assert run.evidence.to_json() == saved
