from ackredit.core.registry import Registry, bind, register_item


def test_register_and_bind():
    register_item(id="paper:1", type="article", title="Paper 1")
    bind("pkg.func", ["paper:1"])
    assert "paper:1" in Registry.items
    assert "pkg.func" in Registry.bindings
