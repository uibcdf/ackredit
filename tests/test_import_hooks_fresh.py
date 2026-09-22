"""Auto-discovery has to work in a process that has just started.

`enable_import_hooks()` followed by importing anything not already imported
raised `ImportError`: the finder called `_read_citation_file`, which imports
`ackredit.core.cff`, which imports yaml at module level, which reached the
finder again — and `cff` was still executing its own import line.

Every test that enables the hooks runs in a process where `ackredit.core.cff`
is already imported, by an earlier test or by the test module itself, so the
cycle never appeared. It needs `cff` unloaded at the moment of the first hooked
import, which only a fresh interpreter gives. These are subprocesses for that
reason, and for no other.

Found by roadmap theme D, instrumenting a real workflow.
"""

import subprocess
import sys
import textwrap

import pytest


def in_a_fresh_process(body: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(body)],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("package", ["csv", "sqlite3", "xml"])
def test_importing_with_hooks_on_does_not_raise(package):
    result = in_a_fresh_process(f"""
        import sys
        import ackredit

        assert "ackredit.core.cff" not in sys.modules, "the cycle needs it unloaded"
        ackredit.enable_import_hooks()
        import {package}
        print("ok")
    """)

    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout


def test_the_cycle_itself():
    """The exact shape: the first hooked import loads cff, whose own import
    reaches the finder again."""
    result = in_a_fresh_process("""
        import sys
        import ackredit

        assert "yaml" not in sys.modules
        ackredit.enable_import_hooks()
        import sqlite3            # anything that is not loaded yet
        print("ok")
    """)

    assert "partially initialized" not in result.stderr
    assert result.returncode == 0, result.stderr


def test_discovery_still_credits_what_it_finds():
    """The guard must not switch discovery off; a package that ships a
    CITATION.cff is still credited."""
    result = in_a_fresh_process("""
        import warnings
        import ackredit

        ackredit.enable_import_hooks()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import ackredit.core.cff          # loads yaml through the hook path
            import pytest                     # a real distribution
        print(len(ackredit.get_used_items()))
    """)

    assert result.returncode == 0, result.stderr
    assert int(result.stdout.strip()) >= 1


def test_what_ackredit_imports_for_itself_is_not_credited():
    """yaml is pulled in by the citation reader, not by the caller's code, and
    the run did not use it."""
    result = in_a_fresh_process("""
        import warnings
        import ackredit

        ackredit.enable_import_hooks()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import sqlite3
        print([name for name in ackredit.get_used_items() if "yaml" in name])
    """)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"


def test_the_discovery_machinery_is_loaded_before_the_finder_is():
    """The invariant the fix rests on, and the one a later change could break.

    A lazy import inside the discovery path is what made the cycle. Loading
    everything discovery needs before installing the finder means no such
    import can reach it, and this asserts the order rather than the symptom.
    """
    result = in_a_fresh_process("""
        import sys
        import ackredit

        assert "ackredit.core.cff" not in sys.modules
        assert "yaml" not in sys.modules
        ackredit.enable_import_hooks()
        print(all(name in sys.modules for name in
                  ("ackredit.core.cff", "yaml", "importlib.metadata")))
    """)

    assert result.stdout.strip() == "True", result.stderr


def test_a_package_ackredit_pulled_in_is_still_discovered_if_the_caller_imports_it():
    """The guard returns before the name is marked as handled, so a later,
    genuine import of the same package is not lost."""
    result = in_a_fresh_process("""
        import warnings
        import ackredit
        from ackredit.core.hooks import InjectionsFinder

        ackredit.enable_import_hooks()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import sqlite3
        finder = next(f for f in __import__("sys").meta_path
                      if isinstance(f, InjectionsFinder))
        print("yaml" in finder._triggered)
    """)

    assert result.stdout.strip() == "False", (
        "yaml was marked as handled, so a caller importing it would not be discovered"
    )
