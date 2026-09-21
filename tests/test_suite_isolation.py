"""The suite must not depend on the order its files happen to run in.

Two failures of that kind were live. `test_csl_json` asserted on the *first*
entry of a report for an item it had registered itself, and the session is
process-wide, so it read whatever another file had tracked first; it passed on
luck and broke when a new file sorted between them.

The opposite one is quieter. The registry holds declarations, made once at
import — `examples/dummy_solver` and `examples/dummy_pipeline` register theirs
when they are imported, and `test_example_libraries` needs them. A test that
emptied the registry destroyed them for everything that ran afterwards, and they
cannot be remade because the import already happened. It worked only while those
files happened to sort last.

`conftest.py` now clears the session around every test and hands out a
`clean_registry` fixture that restores what it emptied. This holds the rule at
the line that would break it again.
"""

import re
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
FILES = sorted(path for path in TESTS.glob("test_*.py"))

_DESTRUCTIVE = re.compile(r"^\s*Registry\.\w+\.clear\(\)", re.MULTILINE)


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_no_test_empties_the_registry_by_hand(path):
    """Use the `clean_registry` fixture, which puts back what it emptied."""
    found = _DESTRUCTIVE.findall(path.read_text(encoding="utf-8"))
    assert not found, (
        f"{path.name} empties the registry directly. Declarations are made once "
        f"at import and cannot be remade, so every test that runs after this one "
        f"loses them. Request the `clean_registry` fixture instead"
    )


def test_the_shared_isolation_exists():
    conftest = (TESTS / "conftest.py").read_text(encoding="utf-8")
    assert "def _isolated_session" in conftest
    assert "def clean_registry" in conftest
