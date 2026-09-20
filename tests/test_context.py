from flowcite import get_used_items, scope, track_item


def test_context_manager_scope():
    # Enter a scope
    with scope("my_block"):
        track_item("paper:block")

    used = get_used_items()
    assert "paper:block" in used
    assert "my_block" in used["paper:block"]


def test_nested_scopes():
    with scope("outer"):
        track_item("paper:outer")
        with scope("inner"):
            track_item("paper:inner")

    used = get_used_items()
    assert "outer" in used["paper:outer"]
    assert "inner" in used["paper:inner"]
    # Leaving the inner scope must restore the outer one
    with scope("top"):
        with scope("sub"):
            pass
        track_item("paper:top_again")

    used = get_used_items()
    assert "top" in used["paper:top_again"]
    assert "sub" not in used["paper:top_again"]
