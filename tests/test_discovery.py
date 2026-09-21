from ackredit import get_used_items
from ackredit.core.hooks import InjectionsFinder


def test_metadata_discovery():
    # Rather than relying on a real import, which may already be cached,
    # exercise the finder's discovery method directly
    finder = InjectionsFinder()

    # Use 'pytest': it is installed and is known to expose package metadata
    finder._record("pytest")

    used = get_used_items()
    assert any(
        k.startswith("metadata:pytest") or k.startswith("discovered:pytest")
        for k in used.keys()
    )
