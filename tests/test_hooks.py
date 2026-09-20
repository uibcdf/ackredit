from flowcite import add_injection, enable_import_hooks, get_used_items


def test_import_hook():
    # Register an injection for a module that is not loaded yet, or a fictitious one
    module_name = "math"  # always importable, enough to exercise the logic
    add_injection(module_name, ["paper:math"])

    enable_import_hooks()

    # Force the import so the finder is triggered; in a real run 'import math'
    # would call find_spec
    import math  # noqa: F401  # importing is the action under test

    # The finder should have triggered the citation
    used = get_used_items()
    # Note: if 'math' was already loaded, find_spec is not called again, so the
    # finder does not fire. Use a fictitious name to exercise the path reliably.

    fake_module = "non_existent_science_lib"
    add_injection(fake_module, ["paper:fake"])

    # Try to import the fictitious module
    try:
        __import__(fake_module)
    except ImportError:
        pass  # A failing import is fine; we only check that the finder fired

    used = get_used_items()
    assert "paper:fake" in used
    assert fake_module in used["paper:fake"]
