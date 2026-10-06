"""Termination and concurrency of providers and provisional recorder evidence."""

import asyncio
import threading
import warnings
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from types import ModuleType

import pytest

import ackredit
from ackredit._private.smonitor.warnings import ProviderObservationWarning
from ackredit.core.context import get_current_scope


@pytest.fixture
def lifecycle_provider(clean_registry):
    module = ModuleType("lifecycle_provider")
    module.__ackredit__ = {
        "schema": "ackredit.provider@1",
        "software": {"name": "Lifecycle Example", "version": "2.4.0"},
        "items": [
            {"id": "lifecycle:method", "type": "article", "title": "The method"},
            {
                "id": "lifecycle:backend:2.4.0",
                "type": "software",
                "title": "Lifecycle Example",
                "version": "2.4.0",
            },
        ],
        "functions": {
            "calculate": [{"item_id": "lifecycle:method", "roles": ["function_entry"]}]
        },
    }
    return module


def _completion_credit(module):
    ackredit.register_item(**module.__ackredit__["items"][1])
    return ackredit.prepare_credit(
        "lifecycle:backend:2.4.0",
        "host.complete",
        roles=["completed_backend"],
        context={"software": "Lifecycle Example", "version": "2.4.0"},
    )


@pytest.mark.parametrize("record_evidence", [False, True])
def test_cancelled_and_failed_tasks_retain_entry_without_completed_backend(
    lifecycle_provider,
    record_evidence,
):
    module = lifecycle_provider
    credit = _completion_credit(module)
    captures = {}
    failure = RuntimeError("scientific failure")

    async def main():
        started = {name: asyncio.Event() for name in ("cancelled", "failed", "done")}
        release = asyncio.Event()

        async def calculate(name):
            started[name].set()
            await release.wait()
            if name == "failed":
                raise failure
            return 200.0

        module.calculate = original = calculate

        async def job(name):
            with (
                ackredit.session(name),
                ackredit.capture(name, record_evidence=record_evidence) as result,
            ):
                captures[name] = result
                with ackredit.scope("host.complete"), ackredit.observe_calls(module):
                    value = await module.calculate(name)
                    credit()
                    return value

        tasks = {name: asyncio.create_task(job(name)) for name in started}
        await asyncio.gather(*(event.wait() for event in started.values()))
        wrapper = module.calculate
        tasks["cancelled"].cancel("application cancellation")
        with pytest.raises(asyncio.CancelledError, match="application cancellation"):
            await tasks["cancelled"]
        # Other activations still own this wrapper after one task is cancelled.
        assert module.calculate is wrapper
        assert ackredit.get_used_items() == {}
        release.set()
        completed, failed = await asyncio.gather(
            tasks["done"], tasks["failed"], return_exceptions=True
        )
        assert completed == 200.0 and failed is failure
        assert module.calculate is original
        assert get_current_scope() is None

    asyncio.run(main())
    for name, captured in captures.items():
        data = captured.attribution.to_dict()
        assert data["name"] == name
        ids = {item["id"] for item in data["items"]}
        expected = {"lifecycle:method"}
        if name == "done":
            expected.add("lifecycle:backend:2.4.0")
        assert ids == expected
        assert data["usage_tree"]["host.complete"]["children"] == [
            "lifecycle_provider.calculate"
        ]
        assert [use["roles"] for use in data["uses"]] == (
            [["function_entry"], ["completed_backend"]]
            if name == "done"
            else [["function_entry"]]
        )
        with ackredit.session("reader"):
            saved = ackredit.Attribution.from_json(captured.attribution.to_json())
            assert saved.to_dict() == data
            assert "References:" in saved.report(format="workflow")
            assert ackredit.get_used_items() == {}
        companion = captured.evidence
        facts = companion.to_dict()["results"][0]
        if record_evidence:
            assert facts["recording_gaps"] is None
            assert [origin["item_id"] for origin in facts["metadata_origins"]] == [
                "lifecycle:method"
            ]
            assert [scope["boundary"] for scope in facts["observation_scope"]] == [
                "lifecycle_provider.calculate"
            ]
        else:
            assert all(value is None for value in facts.values())
        assert companion.attribution.to_dict() == data
        assert (
            ackredit.AttributionEvidence.from_json(companion.to_json()).to_dict()
            == companion.to_dict()
        )


def test_prepared_callable_uses_each_threads_session_and_reused_captures(
    lifecycle_provider,
):
    credit = _completion_credit(lifecycle_provider)
    ready = threading.Barrier(4, timeout=10)

    def job(name):
        with ackredit.session(name), ackredit.scope("host.complete"):
            ready.wait()
            results = []
            for index in range(8):
                with ackredit.capture(f"{name}:{index}") as result:
                    credit()
                    credit()
                results.append(result.attribution.to_dict())
            workflow = ackredit.get_attribution().to_dict()
        assert get_current_scope() is None
        return results, workflow

    with ThreadPoolExecutor(max_workers=4) as executor:
        outputs = list(executor.map(job, [f"worker-{index}" for index in range(4)]))
    for index, (results, workflow) in enumerate(outputs):
        assert workflow["name"] == f"worker-{index}"
        assert len(workflow["items"]) == len(workflow["uses"]) == 1
        for number, result in enumerate(results):
            assert result["name"] == f"worker-{index}:{number}"
            assert result["items"] == workflow["items"]
            assert result["uses"] == workflow["uses"]
            assert result["uses"][0]["context"]["version"] == "2.4.0"
    assert ackredit.get_used_items() == {}


@pytest.mark.parametrize("record_evidence", [False, True])
def test_warning_as_error_restores_observer_and_parent_scope(
    lifecycle_provider,
    clean_registry,
    record_evidence,
):
    module = lifecycle_provider
    calls = []

    def calculate(value):
        calls.append(value)
        return value

    module.calculate = calculate
    declared = deepcopy(module.__ackredit__["items"][0])
    with ackredit.session("strict"), ackredit.scope("parent"):
        with warnings.catch_warnings():
            warnings.simplefilter("error", ProviderObservationWarning)
            with pytest.raises(ProviderObservationWarning) as error:
                with (
                    ackredit.observe_calls(module),
                    ackredit.capture(record_evidence=record_evidence) as result,
                ):
                    clean_registry.items["lifecycle:method"]["title"] = "Changed"
                    module.calculate(3)
        assert error.value.code == "ACKREDIT-W019"
        assert calls == []
        assert result.attribution.to_dict()["items"] == []
        assert get_current_scope() == "parent"
        assert module.calculate is calculate
        facts = result.evidence.to_dict()["results"][0]
        if record_evidence:
            assert facts["metadata_origins"] is None
            assert [gap["diagnostic_code"] for gap in facts["recording_gaps"]] == [
                "ACKREDIT-W019"
            ]
            assert facts["recording_gaps"][0]["boundary"] == (
                "lifecycle_provider.calculate"
            )
        else:
            assert all(value is None for value in facts.values())
        # A refused observation leaves no wrapper lease that prevents reuse.
        clean_registry.items["lifecycle:method"] = declared
        with ackredit.observe_calls(module), ackredit.capture() as recovered:
            assert module.calculate(5) == 5
        assert calls == [5]
        assert len(recovered.attribution.to_dict()["items"]) == 1
        assert module.calculate is calculate


@pytest.mark.parametrize("record_evidence", [False, True])
def test_unawaited_coroutine_cannot_earn_completed_or_entry_credit(
    lifecycle_provider,
    record_evidence,
):
    module = lifecycle_provider
    entered = []

    async def calculate():
        entered.append(True)
        return 200.0

    module.calculate = calculate
    with ackredit.session("unawaited"), ackredit.observe_calls(module):
        with ackredit.capture(record_evidence=record_evidence) as result:
            coroutine = module.calculate()
        coroutine.close()
    assert entered == []
    assert result.attribution.to_dict()["items"] == []
    assert ackredit.get_used_items() == {}
    assert module.calculate is calculate
    facts = result.evidence.to_dict()["results"][0]
    assert facts["metadata_origins"] is facts["recording_gaps"] is None
    assert bool(facts["observation_scope"]) is record_evidence


@pytest.mark.parametrize("record_evidence", [False, True])
def test_delayed_prepared_credit_cannot_change_an_expired_result_capture(
    lifecycle_provider,
    record_evidence,
):
    credit = _completion_credit(lifecycle_provider)

    async def main():
        ready = asyncio.Event()
        release = asyncio.Event()

        async def child():
            ready.set()
            await release.wait()
            with ackredit.capture(
                "later result", record_evidence=record_evidence
            ) as later:
                credit()
            return later

        with ackredit.session("workflow"):
            with ackredit.capture(
                "earlier result", record_evidence=record_evidence
            ) as earlier:
                task = asyncio.create_task(child())
                await ready.wait()
            saved = earlier.attribution.to_dict()
            saved_evidence = earlier.evidence.to_dict()
            release.set()
            later = await task
            assert earlier.attribution.to_dict() == saved
            assert earlier.evidence.to_dict() == saved_evidence
            assert saved["items"] == saved["uses"] == []
            later_data = later.attribution.to_dict()
            assert len(later_data["items"]) == len(later_data["uses"]) == 1
            assert ackredit.get_attribution().to_dict()["uses"] == later_data["uses"]
            assert all(
                value is None
                for value in later.evidence.to_dict()["results"][0].values()
            )
        assert ackredit.get_used_items() == {}

    asyncio.run(main())
