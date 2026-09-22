"""The provenance graph is not a tree, and the renderer assumed it was.

`devguide/vision.md` calls this "Hierarchical Provenance: see exactly *why* a
citation was triggered". Entering `scope("lib.fib")` inside itself records the
target as its own child — which is what a recursive function does — and two
functions that call each other record a cycle between them.

The renderer assumed a tree twice. It started from the targets nobody calls, so
a graph that is all cycle left it nothing to draw and the report came out empty,
silently. And it followed children without remembering where it had been, so a
cycle below a real root ran until Python stopped it with a RecursionError.

Recursion is ordinary in scientific code.
"""

import pytest

import ackredit
from ackredit.core.session import current_session


@pytest.fixture(autouse=True)
def _a_work(clean_registry):
    current_session().clear()
    ackredit.register_item(id="a:1", title="A Work")


def report() -> str:
    return ackredit.report(format="provenance")


# --- the cycles -----------------------------------------------------------


def test_a_recursive_function_is_still_drawn():
    """The report was the header and nothing else."""

    @ackredit.scoped_usage(target="lib.fib")
    def fib(n):
        ackredit.track_item("a:1")
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    fib(4)
    rendered = report()

    assert "lib.fib" in rendered
    assert "(Cite: A Work)" in rendered
    assert "lib.fib (above)" in rendered, "the recursion is shown, not followed"


def test_two_functions_that_call_each_other_are_still_drawn():
    with ackredit.scope("alpha"):
        with ackredit.scope("beta"):
            ackredit.track_item("a:1")
    with ackredit.scope("beta"):
        with ackredit.scope("alpha"):
            ackredit.track_item("a:1")

    rendered = report()
    assert "alpha" in rendered and "beta" in rendered
    assert "(above)" in rendered


def test_a_cycle_below_a_real_root_does_not_recurse_forever():
    """This raised RecursionError out of a public renderer."""
    with ackredit.scope("top"):
        with ackredit.scope("b"):
            with ackredit.scope("c"):
                ackredit.track_item("a:1")
    with ackredit.scope("c"):
        with ackredit.scope("b"):
            ackredit.track_item("a:1")

    rendered = report()
    assert "top" in rendered
    assert "b (above)" in rendered


def test_every_target_appears_somewhere():
    """A node the roots cannot reach is an entry point of its own, or it is
    simply missing from a report whose purpose is to account for everything."""
    with ackredit.scope("reachable"):
        ackredit.track_item("a:1")
    with ackredit.scope("island_a"):
        with ackredit.scope("island_b"):
            ackredit.track_item("a:1")
    with ackredit.scope("island_b"):
        with ackredit.scope("island_a"):
            ackredit.track_item("a:1")

    rendered = report()
    for target in ("reachable", "island_a", "island_b"):
        assert target in rendered


def test_the_report_is_finite_for_a_long_cycle():
    names = [f"step{index}" for index in range(12)]
    for first, second in zip(names, names[1:] + names[:1]):
        with ackredit.scope(first):
            with ackredit.scope(second):
                ackredit.track_item("a:1")

    rendered = report()
    assert len(rendered.splitlines()) < 200, "a cycle is drawn once, not unrolled"


# --- what must not change -------------------------------------------------


def test_an_ordinary_tree_renders_as_before():
    with ackredit.scope("outer"):
        ackredit.track_item("a:1")
        with ackredit.scope("inner"):
            ackredit.track_item("a:1")

    assert report() == (
        "# Citation Provenance Graph\n"
        "\n"
        "└── outer\n"
        "    ├── (Cite: A Work)\n"
        "    └── inner\n"
        "        └── (Cite: A Work)"
    )


def test_nothing_tracked_says_so():
    assert report() == "No tracking information available."


def test_two_roots_are_both_drawn():
    with ackredit.scope("first"):
        ackredit.track_item("a:1")
    with ackredit.scope("second"):
        ackredit.track_item("a:1")

    rendered = report()
    assert "├── first" in rendered
    assert "└── second" in rendered
