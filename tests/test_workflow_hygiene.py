"""A CI step that cannot fail is worse than no step at all.

A multi-line `run:` is one shell script, and GitHub takes its exit status from
the last command. Without `set -e`, an intermediate failure does not stop it, so
a check that ends with `echo "::endgroup::"` reports success while printing a
traceback. That is what happened to the import smoke check, which raised
`AttributeError: module 'ackredit' has no attribute '__version__'` on a green
run.
"""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.y*ml"))


def _multi_line_steps():
    """Every (workflow, job, step) whose `run:` is more than one command."""
    found = []
    for path in WORKFLOWS:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        for job_name, job in (document.get("jobs") or {}).items():
            for index, step in enumerate(job.get("steps") or []):
                script = step.get("run")
                if not script:
                    continue
                commands = [
                    line
                    for line in script.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                if len(commands) > 1:
                    name = step.get("name") or f"step {index}"
                    found.append((f"{path.name}:{job_name}:{name}", script))
    return found


MULTI_LINE_STEPS = _multi_line_steps()


def test_there_are_multi_line_steps_to_check():
    """Guard the guard: a broken reader would make the check below vacuous."""
    assert MULTI_LINE_STEPS


@pytest.mark.parametrize(
    "label,script", MULTI_LINE_STEPS, ids=[s[0] for s in MULTI_LINE_STEPS]
)
def test_a_multi_line_step_stops_at_the_first_failure(label, script):
    assert "set -e" in script, (
        f"{label}: a multi-line run: needs `set -e`, or a failing command in the "
        "middle leaves the step green"
    )


def test_the_installed_ruff_matches_the_pinned_one():
    """A local gate running a different Ruff is not the gate CI runs.

    This was found the hard way: a locally green `ruff format --check` under
    0.16.1 failed CI under the pinned 0.16.5, because the two format Python
    inside Markdown differently.
    """
    import re
    import subprocess
    import sys
    import tomllib

    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pins = [
        dependency
        for group in pyproject["project"]["optional-dependencies"].values()
        for dependency in group
        if dependency.startswith("ruff==")
    ]
    assert pins, "no pinned Ruff to compare against"
    pinned = pins[0].split("==", 1)[1]

    result = subprocess.run(
        [sys.executable, "-m", "ruff", "--version"], capture_output=True, text=True
    )
    if result.returncode != 0:
        pytest.skip("ruff is not importable in this environment")
    running = re.search(r"(\d+\.\d+\.\d+)", result.stdout).group(1)

    assert running == pinned, (
        f"ruff {running} is installed but the suite policy pins {pinned}; "
        "the local format gate does not match CI"
    )


def _ci() -> dict:
    import yaml

    return yaml.safe_load(
        (ROOT / ".github/workflows/CI.yaml").read_text(encoding="utf-8")
    )


def _contract_versions() -> list[str]:
    """The minor versions `requires-python` promises."""
    import re
    import tomllib

    contract = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = contract["project"]["requires-python"]
    low, high = re.findall(r"3\.(\d+)", declared)
    return [f"3.{minor}" for minor in range(int(low), int(high))]


def test_ci_runs_every_version_the_contract_promises():
    """It ran 3.13 alone while promising 3.11 to 3.13, so two of the three had
    never been run by anything — `uibcdf/ackredit#63`. A version promised and
    never executed is found by the user who has it."""
    matrix = _ci()["jobs"]["test"]["strategy"]["matrix"]

    assert sorted(matrix["python-version"]) == sorted(_contract_versions())


def test_an_experimental_version_is_outside_the_contract():
    """3.14 is in the matrix as evidence for `uibcdf/molsyssuite#29` and claims
    nothing. Were it ever moved into the promised list without the contract
    moving too, the lane would have become a claim by accident."""
    matrix = _ci()["jobs"]["test"]["strategy"]["matrix"]
    promised = set(_contract_versions())

    for entry in matrix.get("include", []):
        assert entry["python-version"] not in promised
        assert entry["experimental"] is True, "an evidence lane must not gate a merge"


def test_the_experimental_lane_does_not_gate():
    job = _ci()["jobs"]["test"]
    assert "matrix.experimental" in str(job.get("continue-on-error", ""))
