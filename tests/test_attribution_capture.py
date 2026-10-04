"""Portable calculation references also contribute to the application workflow."""

import asyncio
import json
import subprocess
import sys
from copy import deepcopy

import pytest

import ackredit


def _declare():
    ackredit.register_item(
        id="software:example:2.0", type="software", title="Example", version="2.0"
    )
    ackredit.register_item(
        id="paper:example",
        type="article",
        title="Example paper",
        authors=["Ruiz, Ana"],
        doi="10.1234/example",
        year=2020,
    )


def _credit():
    context = {"software": "example", "version": "2.0"}
    ackredit.track_item(
        "software:example:2.0", roles=["executed_software"], context=context
    )
    ackredit.track_item(
        "paper:example", roles=["software_description"], context=context
    )


def test_reused_references_belong_to_each_capture_and_the_enclosing_workflow(
    clean_registry,
):
    _declare()
    with ackredit.session("workflow"):
        with ackredit.scope("application"):
            for name in ("first", "second"):
                with ackredit.capture(
                    name, context={"producer": "client", "version": "1"}
                ) as run:
                    with ackredit.scope("client.convert"):
                        _credit()
                data = run.attribution.to_dict()
                assert {item["id"] for item in data["items"]} == {
                    "software:example:2.0",
                    "paper:example",
                }
                assert len(data["uses"]) == 2
                assert data["context"] == {"producer": "client", "version": "1"}
                assert data["uses"][1]["roles"] == ["software_description"]
                assert data["uses"][1]["context"] == {
                    "software": "example",
                    "version": "2.0",
                }
        assert ackredit.get_used_items()["paper:example"] == ["client.convert"]
        assert len(ackredit.get_attribution().to_dict()["items"]) == 2
        assert (
            "client.convert"
            in ackredit.current_session().usage_tree["application"]["children"]
        )


def test_nested_captures_include_completed_children_without_replacing_the_session(
    clean_registry,
):
    _declare()
    with ackredit.session() as workflow:
        with ackredit.capture("parent") as parent:
            with ackredit.capture("child") as child:
                _credit()
                assert ackredit.current_session() is workflow
            ackredit.track_item("parent-only")
        assert len(child.attribution.to_dict()["items"]) == 2
        assert len(parent.attribution.to_dict()["items"]) == 3
        assert len(ackredit.get_used_items()) == 3


def test_capture_is_detached_from_registry_context_and_other_results(clean_registry):
    _declare()
    context = {"software": "example", "versions": ["2.0"]}
    with ackredit.capture("first") as run:
        ackredit.track_item(
            "paper:example", roles=["software_description"], context=context
        )
    original = run.attribution.to_dict()
    context["versions"].append("3.0")
    ackredit.register_item(id="paper:example", title="Replacement")
    altered = run.attribution.to_dict()
    altered["items"][0]["authors"][0] = "User edit"
    altered["uses"][0]["context"]["versions"].append("4.0")
    assert run.attribution.to_dict() == original


def test_export_import_and_reporting_in_a_fresh_reader_never_credit(
    tmp_path, clean_registry
):
    _declare()
    with ackredit.capture("result") as run:
        _credit()
    path = tmp_path / "attribution.json"
    path.write_text(run.attribution.to_json())
    script = """
import pathlib, sys
import ackredit
saved = ackredit.Attribution.from_json(pathlib.Path(sys.argv[1]).read_text())
assert saved.to_dict()["schema"] == "ackredit.attribution@1"
assert saved.to_dict()["items"][0]["version"] == "2.0"
assert "Example paper" in saved.report()
assert "10.1234/example" in saved.report(format="bibtex")
assert ackredit.get_used_items() == {}
assert ackredit.get_attribution().to_dict()["items"] == []
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(path)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_each_reference_can_have_several_contextual_roles_without_changing_its_record(
    clean_registry,
):
    _declare()
    with ackredit.capture() as run:
        ackredit.track_item(
            "paper:example", used_by="one", roles=["scientific_criterion"]
        )
        ackredit.track_item(
            "paper:example", used_by="two", roles=["reference_implementation"]
        )
    data = run.attribution.to_dict()
    assert len(data["items"]) == 1
    assert [use["roles"] for use in data["uses"]] == [
        ["scientific_criterion"],
        ["reference_implementation"],
    ]
    assert "roles" not in data["items"][0]


def test_different_dependency_versions_can_share_one_description_article(
    clean_registry,
):
    _declare()
    with ackredit.capture() as run:
        for version in ("2.0", "3.0"):
            ackredit.track_item(
                "paper:example",
                roles=["software_description"],
                context={"software": "example", "version": version},
            )
    assert len(run.attribution.to_dict()["items"]) == 1
    assert len(run.attribution.to_dict()["uses"]) == 2


def test_empty_completed_calculation_keeps_producer_context():
    with ackredit.capture(
        "empty", context={"producer": "client", "version": "1"}
    ) as run:
        pass
    assert run.attribution.to_dict()["items"] == []
    assert run.attribution.to_dict()["context"]["version"] == "1"


def test_scientific_exception_propagates_and_completed_child_credit_survives(
    clean_registry,
):
    _declare()
    with pytest.raises(RuntimeError, match="science failed"):
        with ackredit.capture("failed parent") as run:
            _credit()
            raise RuntimeError("science failed")
    assert len(run.attribution.to_dict()["items"]) == 2
    with ackredit.capture("later") as later:
        pass
    assert later.attribution.to_dict()["items"] == []


def test_changing_metadata_for_one_id_inside_a_capture_is_reported(clean_registry):
    _declare()
    with ackredit.capture():
        ackredit.track_item("paper:example")
        ackredit.register_item(id="paper:example", title="Different work")
        with pytest.raises(ValueError) as error:
            ackredit.track_item("paper:example")
    assert error.value.code == "ACKREDIT-E011"


@pytest.mark.parametrize(
    "roles,context",
    [
        ("software_description", None),
        ([""], None),
        ([1], None),
        ([], {"bad": object()}),
        ([], {"bad": float("nan")}),
        ([], {1: "bad"}),
    ],
)
def test_invalid_contextual_tracking_is_refused_before_any_credit(roles, context):
    with pytest.raises(ValueError) as error:
        ackredit.track_item("paper", roles=roles, context=context)
    assert error.value.code == "ACKREDIT-E010"
    assert ackredit.get_used_items() == {}


def test_import_validates_schema_references_and_json_values():
    with ackredit.capture() as run:
        ackredit.track_item("undeclared")
    valid = run.attribution.to_dict()
    mutations = [
        lambda data: data.update(schema="ackredit.attribution@2"),
        lambda data: data["uses"][0].update(item_id="missing"),
        lambda data: data["uses"][0].update(roles="a string"),
        lambda data: data["items"].append(dict(data["items"][0])),
        lambda data: data.update(context={"number": float("inf")}),
    ]
    for mutate in mutations:
        data = deepcopy(valid)
        mutate(data)
        with pytest.raises(ValueError) as error:
            ackredit.Attribution.from_dict(data)
        assert error.value.code == "ACKREDIT-E010"
    assert ackredit.Attribution.from_json(json.dumps(valid)).to_dict() == valid


def test_capture_does_not_collect_an_explicitly_isolated_session():
    with ackredit.capture() as outer:
        with ackredit.session("independent"):
            ackredit.track_item("independent")
        ackredit.track_item("outer")
    assert [item["id"] for item in outer.attribution.to_dict()["items"]] == ["outer"]


def test_async_sibling_captures_are_isolated():
    async def job(name):
        with ackredit.capture(name) as run:
            await asyncio.sleep(0)
            ackredit.track_item(name)
        return run.attribution.to_dict()

    async def main():
        return await asyncio.gather(job("a"), job("b"))

    results = asyncio.run(main())
    assert [[item["id"] for item in data["items"]] for data in results] == [
        ["a"],
        ["b"],
    ]


def test_detached_provenance_uses_saved_tree_and_plugins_use_saved_records(
    clean_registry,
    monkeypatch,
):
    from importlib import import_module

    reports = import_module("ackredit.core.report")
    monkeypatch.setattr(reports, "_RENDERERS", dict(reports._RENDERERS))
    _declare()
    with ackredit.capture() as run:
        with ackredit.scope("original"):
            _credit()
    saved = run.attribution
    ackredit.current_session().clear()
    with ackredit.scope("reader"):
        ackredit.track_item("reader-only")
    report = saved.report(format="provenance")
    assert "original" in report and "reader" not in report
    ackredit.register_format(
        "capture-test", lambda used, items: items["paper:example"]["title"], "txt"
    )
    assert saved.report(format="capture-test") == "Example paper"


def test_capture_instance_cannot_be_reentered():
    run = ackredit.capture()
    with run:
        pass
    with pytest.raises(ValueError) as error:
        with run:
            pass
    assert error.value.code == "ACKREDIT-E010"


def test_mutable_context_is_revalidated_on_repeated_credits_in_nested_captures(
    clean_registry,
):
    _declare()
    context = {"software": "example", "options": ["first"]}
    with ackredit.capture("outer") as outer:
        with ackredit.capture("inner") as inner:
            ackredit.track_item("paper:example", context=context)
            context["options"].append("second")
            ackredit.track_item("paper:example", context=context)
            context["options"].append(float("nan"))
            with pytest.raises(ValueError) as error:
                ackredit.track_item("paper:example", context=context)
    assert error.value.code == "ACKREDIT-E010"
    for attribution in (
        outer.attribution,
        inner.attribution,
        ackredit.get_attribution(),
    ):
        assert [use["context"]["options"] for use in attribution.to_dict()["uses"]] == [
            ["first"],
            ["first", "second"],
        ]


@pytest.mark.parametrize(
    "payload", [None, [], "text", {"schema": "ackredit.attribution@2"}]
)
def test_direct_reader_refuses_non_objects_and_unknown_schemas_with_catalog_error(
    payload,
):
    with pytest.raises(ValueError) as error:
        ackredit.Attribution(payload)
    assert error.value.code == "ACKREDIT-E010"


@pytest.mark.parametrize(
    "field,value", [("context", None), ("item_id", []), ("use_context", None)]
)
def test_reader_refuses_malformed_context_and_use_identity(
    field, value, clean_registry
):
    _declare()
    with ackredit.capture() as run:
        _credit()
    data = run.attribution.to_dict()
    if field == "context":
        data["context"] = value
    else:
        data["uses"][0]["context" if field == "use_context" else field] = value
    with pytest.raises(ValueError) as error:
        ackredit.Attribution.from_dict(data)
    assert error.value.code == "ACKREDIT-E010"


def test_inherited_workflow_keeps_original_contextual_records_and_clear_removes_them(
    clean_registry,
):
    _declare()
    with ackredit.session("parent"):
        _credit()
        with ackredit.session("child", inherit=True):
            data = ackredit.get_attribution().to_dict()
            assert len(data["items"]) == 2
            assert data["uses"][1]["roles"] == ["software_description"]
            ackredit.current_session().clear()
            assert ackredit.get_attribution().to_dict()["items"] == []
        assert len(ackredit.get_attribution().to_dict()["items"]) == 2


@pytest.mark.parametrize("format", [None, [], 12])
def test_saved_report_refuses_invalid_format_with_catalog_error(format):
    with pytest.raises(ValueError) as error:
        ackredit.get_attribution().report(format=format)
    assert error.value.code == "ACKREDIT-E010"


def test_deeply_nested_json_is_refused_with_catalog_error():
    depth = sys.getrecursionlimit() + 100
    with pytest.raises(ValueError) as error:
        ackredit.Attribution.from_json("[" * depth + "0" + "]" * depth)
    assert error.value.code == "ACKREDIT-E010"
