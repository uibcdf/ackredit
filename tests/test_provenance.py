from flowcite import register_item, report, scope, scoped_usage, track_item


@scoped_usage("outer_func")
def outer():
    track_item("item:outer")
    inner()


@scoped_usage("inner_func")
def inner():
    track_item("item:inner")
    with scope("manual_block"):
        track_item("item:block")


def test_provenance_tree():
    register_item(id="item:outer", title="Outer Paper")
    register_item(id="item:inner", title="Inner Paper")
    register_item(id="item:block", title="Block Paper")

    outer()

    tree_str = report(format="provenance")
    print("\nGenerated Tree:\n")
    print(tree_str)

    # Check hierarchy presence
    assert "outer_func" in tree_str
    assert "└── inner_func" in tree_str
    assert "    └── manual_block" in tree_str

    # Check items attached to correct nodes
    assert "(Cite: Outer Paper)" in tree_str
    assert "(Cite: Inner Paper)" in tree_str
    assert "(Cite: Block Paper)" in tree_str
