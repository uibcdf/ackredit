"""The devguide states facts about the code. They must be facts.

`vision.md` claimed Ackredit depended only on `smonitor` and `depdigest`, and
that everything beyond those two lived in `optional-dependencies`. It had three
runtime dependencies: `pyyaml` arrived when the `CITATION.cff` reader stopped
guessing at YAML, and the pillar was never revisited.

A normative document that disagrees with the code is worse than a missing one,
because it is read as authority.
"""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
VISION = (ROOT / "devguide/vision.md").read_text(encoding="utf-8")

WRITTEN_NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def _names(requirements) -> set[str]:
    return {re.split(r"[<>=!~\[ ]", item, maxsplit=1)[0] for item in requirements}


def test_the_lean_core_pillar_counts_the_real_dependencies():
    runtime = _names(PYPROJECT["project"]["dependencies"])
    count = WRITTEN_NUMBERS[len(runtime)]

    assert f"{count} runtime dependencies" in VISION, (
        f"devguide/vision.md does not say Ackredit has {count} runtime "
        f"dependencies, and it has: {sorted(runtime)}"
    )


def test_the_lean_core_pillar_names_every_one_of_them():
    for dependency in _names(PYPROJECT["project"]["dependencies"]):
        assert f"`{dependency}`" in VISION, (
            f"{dependency} is a runtime dependency that devguide/vision.md does "
            f"not name, so the pillar understates what a host installs"
        )


def test_nothing_is_both_required_and_optional():
    runtime = _names(PYPROJECT["project"]["dependencies"])
    optional = {
        name
        for extra in PYPROJECT["project"].get("optional-dependencies", {}).values()
        for name in _names(extra)
    }
    assert not runtime & optional, (
        f"{sorted(runtime & optional)} is declared as both required and optional"
    )
