"""Shared graphs are expanded once and deep valid graphs do not recurse (#91)."""

import sys

from ackredit.formats.provenance import render_tree


def test_shared_subgraph_expands_once_and_retains_every_target():
    layers = 9
    tree = {
        f"step{layer}{suffix}": {
            "items": ["paper:last"] if layer == layers else [],
            "children": [f"step{layer + 1}a", f"step{layer + 1}b"]
            if layer < layers
            else [],
        }
        for layer in range(layers + 1)
        for suffix in "ab"
    }
    rendered = render_tree(tree, {"paper:last": {"title": "Last reference"}})
    assert len(rendered.splitlines()) <= 3 * len(tree)
    assert rendered.count("(shared; shown above)") == 18
    assert rendered.count("(Cite: Last reference)") == 2
    assert all(target in rendered for target in tree)


def test_a_flat_graph_longer_than_the_recursion_limit_is_readable():
    length = sys.getrecursionlimit() + 20
    tree = {
        f"target{index}": {
            "items": [],
            "children": [f"target{index + 1}"] if index + 1 < length else [],
        }
        for index in range(length)
    }
    rendered = render_tree(tree, {})
    assert len(rendered.splitlines()) == length + 2
    assert f"target{length - 1}" in rendered


def test_shared_edges_keep_their_actual_parents():
    tree = {
        "left": {"items": [], "children": ["shared"]},
        "right": {"items": [], "children": ["shared"]},
        "shared": {"items": ["paper"], "children": []},
    }
    assert render_tree(tree, {"paper": {"title": "Shared paper"}}) == (
        "# Citation Provenance Graph\n\n"
        "├── left\n│   └── shared\n│       └── (Cite: Shared paper)\n"
        "└── right\n    └── shared (shared; shown above)"
    )
