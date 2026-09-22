"""Runtime behaviour of bind(): introspection and opt-in crediting."""

from ackredit import (
    bind,
    bound_items,
    credit_bound,
    get_used_items,
    register_item,
    scope,
    scoped_usage,
    track_item,
)
from ackredit.core.registry import Registry


def test_bound_items_reads_back_declarations():
    register_item(id="bi:base", type="article", title="Base paper")
    bind("bi.target", ["bi:base"])

    assert bound_items("bi.target") == ["bi:base"]
    assert Registry.bound_items("bi.target") == ["bi:base"]


def test_bound_items_returns_a_copy():
    bind("bi.copy", ["bi:one"])

    bound_items("bi.copy").append("bi:injected")

    assert bound_items("bi.copy") == ["bi:one"]


def test_bound_items_of_unknown_target_is_empty():
    assert bound_items("bi.never.declared") == []


def test_scoped_usage_does_not_credit_bindings_by_default():
    """The conditional path stays the default; bind alone must not credit."""
    register_item(id="bi:default", type="article", title="Not credited")
    bind("bi.default_target", ["bi:default"])

    @scoped_usage("bi.default_target")
    def run():
        pass

    run()

    assert "bi:default" not in get_used_items()


def test_scoped_usage_credits_bindings_when_opted_in():
    register_item(id="bi:opt", type="article", title="Credited paper")
    bind("bi.opt_target", ["bi:opt"])

    @scoped_usage("bi.opt_target", credit_bound=True)
    def run():
        pass

    run()

    used = get_used_items()
    assert "bi:opt" in used
    assert used["bi:opt"] == ["bi.opt_target"]


def test_opt_in_crediting_coexists_with_conditional_tracking():
    register_item(id="bi:always", type="article", title="Always cited")
    register_item(id="bi:advanced", type="article", title="Advanced only")
    bind("bi.hybrid", ["bi:always"])

    @scoped_usage("bi.hybrid", credit_bound=True)
    def detect(mode="basic"):
        if mode == "advanced":
            track_item("bi:advanced")

    detect()
    used = get_used_items()
    assert "bi:always" in used
    assert "bi:advanced" not in used

    detect(mode="advanced")
    used = get_used_items()
    assert "bi:advanced" in used
    assert used["bi:advanced"] == ["bi.hybrid"]


def test_credit_bound_returns_credited_ids_and_is_idempotent():
    register_item(id="bi:r1", title="R1")
    register_item(id="bi:r2", title="R2")
    bind("bi.returns", ["bi:r1", "bi:r2"])

    assert credit_bound("bi.returns") == ["bi:r1", "bi:r2"]

    credit_bound("bi.returns")
    assert get_used_items()["bi:r1"] == ["bi.returns"]


def test_credit_bound_without_declarations_is_a_no_op():
    before = dict(get_used_items())

    assert credit_bound("bi.nothing_bound") == []

    assert get_used_items() == before


def test_scope_credits_bindings_when_opted_in():
    register_item(id="bi:block", type="article", title="Block paper")
    bind("bi.block", ["bi:block"])

    with scope("bi.block"):
        pass
    assert "bi:block" not in get_used_items()

    with scope("bi.block", credit_bound=True):
        pass
    assert get_used_items()["bi:block"] == ["bi.block"]


def test_credited_bindings_appear_in_the_provenance_tree():
    from ackredit import report

    register_item(id="bi:prov", type="article", title="Provenance paper")
    bind("bi.prov_target", ["bi:prov"])

    @scoped_usage("bi.prov_target", credit_bound=True)
    def run():
        pass

    run()

    tree = report(format="provenance")
    assert "bi.prov_target" in tree
    assert "(Cite: Provenance paper)" in tree
