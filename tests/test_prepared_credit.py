"""Prepared immutable credits still observe every current result and session."""

import json

import pytest

import ackredit


def _declare():
    ackredit.register_item(
        id="prepared:software:2", title="Example", type="software", version="2"
    )


def test_prepared_credit_is_detached_and_reused_in_independent_captures(clean_registry):
    _declare()
    context = {"software": "example", "version": "2", "options": {"mode": "exact"}}
    roles = ["executed_software"]
    credit = ackredit.prepare_credit(
        "prepared:software:2", "example.convert", roles=roles, context=context
    )
    context["options"]["mode"] = "changed"
    roles.append("changed")
    assert ackredit.get_used_items() == {}
    for name in ("first", "second"):
        with (
            ackredit.session(name),
            ackredit.scope("pipeline"),
            ackredit.capture(name) as outer,
        ):
            with ackredit.capture("child") as child:
                credit()
                credit()
        for run in (outer, child):
            data = run.attribution.to_dict()
            assert len(data["uses"]) == 1
            assert data["uses"][0]["roles"] == ["executed_software"]
            assert data["uses"][0]["context"]["options"] == {"mode": "exact"}
            assert data["items"][0]["version"] == "2"
            assert ackredit.Attribution.from_json(json.dumps(data)).to_dict() == data


def test_replaced_or_deleted_registered_bibliography_cannot_be_credited(clean_registry):
    _declare()
    credit = ackredit.prepare_credit("prepared:software:2", "example.convert")
    clean_registry.items["prepared:software:2"]["version"] = "wrong"
    with ackredit.capture() as run, pytest.raises(ValueError) as error:
        credit()
    assert error.value.code == "ACKREDIT-E010"
    assert run.attribution.to_dict()["items"] == []
    del clean_registry.items["prepared:software:2"]
    with pytest.raises(ValueError):
        credit()
    assert ackredit.get_used_items() == {}


def test_registered_tuple_metadata_matches_public_portable_tracking(clean_registry):
    ackredit.register_item(
        id="tuple-record", title="Tuple metadata", authors=("Ruiz, Ana", "Lee, Min")
    )
    credit = ackredit.prepare_credit(
        "tuple-record", "example.convert", roles=["executed_software"]
    )
    with ackredit.session("public"), ackredit.capture("result") as public:
        ackredit.track_item(
            "tuple-record", used_by="example.convert", roles=["executed_software"]
        )
    with ackredit.session("prepared"), ackredit.capture("result") as prepared:
        credit()
    assert prepared.attribution.to_dict() == public.attribution.to_dict()
    assert clean_registry.items["tuple-record"]["authors"] == ("Ruiz, Ana", "Lee, Min")


def test_prepared_credit_uses_the_existing_journal_writer(clean_registry, tmp_path):
    _declare()
    credit = ackredit.prepare_credit(
        "prepared:software:2", "example.convert", roles=["executed_software"]
    )
    path = tmp_path / "journal.json"
    with ackredit.session("writer"):
        ackredit.enable_persistence(path)
        with ackredit.scope("example.convert"):
            credit()
            credit()
    with ackredit.session("reader"):
        ackredit.aggregate([path])
        assert ackredit.get_used_items() == {"prepared:software:2": ["example.convert"]}


@pytest.mark.parametrize(
    "options", [{"used_by": ""}, {"roles": [""]}, {"context": {"bad": float("nan")}}]
)
def test_preparation_refuses_invalid_inputs_before_credit(clean_registry, options):
    _declare()
    kwargs = {"used_by": "example.convert", **options}
    with pytest.raises(ValueError):
        ackredit.prepare_credit("prepared:software:2", **kwargs)
    assert ackredit.get_used_items() == {}


def test_preparation_requires_a_registered_matching_reference(clean_registry):
    with pytest.raises(ValueError):
        ackredit.prepare_credit("missing", "example.convert")
    clean_registry.items["missing"] = {"id": "different", "title": "Mismatch"}
    with pytest.raises(ValueError):
        ackredit.prepare_credit("missing", "example.convert")
    assert ackredit.get_used_items() == {}
