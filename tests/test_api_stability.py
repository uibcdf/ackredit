"""Every public name must say what it promises.

`__all__` states what is public. It said nothing about what is *kept*, so a
reader could not tell `report` — 106 tests, 30 documentation mentions, its shape
decided in `devguide/decisions.md` — from `serve_ui`, which its own docstring
calls a conceptual stub.

1.0.0 means the public API is stable and we commit to not breaking it. This
holds `docs/content/about/stability.md` to `__all__`, so a name cannot join the
public surface without a decision about which of those two it is.
"""

import re
from pathlib import Path

import pytest

import ackredit

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "docs/content/about/stability.md").read_text(encoding="utf-8")

LEVELS = {"stable", "provisional"}

_ROW = re.compile(r"^\| `([^`]+)` \| (\w+) \| (.+?) \|\s*$", re.MULTILINE)
ROWS = _ROW.findall(PAGE)
CLASSIFIED = {name: (level, why) for name, level, why in ROWS}

STABLE = sorted(n for n, (level, _) in CLASSIFIED.items() if level == "stable")
PROVISIONAL = sorted(
    n for n, (level, _) in CLASSIFIED.items() if level == "provisional"
)

TEST_SOURCES = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "tests").glob("test_*.py"))
)


def test_the_table_was_read():
    assert ROWS, "no classification rows parsed from the stability page"


def test_every_public_name_is_classified():
    missing = sorted(set(ackredit.__all__) - set(CLASSIFIED))
    assert not missing, (
        f"{missing} is exported and says nothing about whether it is kept. "
        f"Add a row to docs/content/about/stability.md"
    )


def test_nothing_is_classified_that_is_not_public():
    extra = sorted(set(CLASSIFIED) - set(ackredit.__all__))
    assert not extra, (
        f"{extra} is classified on the stability page and is not in __all__, "
        f"so the page promises something the library does not expose"
    )


def test_no_name_is_listed_twice():
    names = [name for name, _, _ in ROWS]
    duplicated = sorted({name for name in names if names.count(name) > 1})
    assert not duplicated, f"{duplicated} appears more than once"


@pytest.mark.parametrize("name,level,why", ROWS, ids=[row[0] for row in ROWS])
def test_each_row_states_a_level_and_a_reason(name, level, why):
    assert level in LEVELS, f"{name} is '{level}', which is not one of {sorted(LEVELS)}"
    assert len(why.strip()) > 30, (
        f"{name} is classified with no reason worth reading. A provisional name "
        f"with no stated reason is indistinguishable from an oversight"
    )


@pytest.mark.parametrize("name", STABLE)
def test_a_stable_name_is_exercised(name):
    """Promising to keep something nothing runs is a promise made blind."""
    hits = len(re.findall(rf"\b{re.escape(name)}\b", TEST_SOURCES))
    assert hits > 0, (
        f"{name} is declared stable and no test mentions it. Either it is "
        f"exercised or it is provisional"
    )


def test_the_boundary_is_stated():
    """A reader must know that everything else is private."""
    assert "`__all__` is the boundary" in PAGE


def test_the_deprecation_policy_says_what_a_removal_requires():
    policy = PAGE.split("## Deprecation policy", 1)
    assert len(policy) == 2, "the page states no deprecation policy"
    assert "major release" in policy[1]
    assert "two minor releases" in policy[1]
