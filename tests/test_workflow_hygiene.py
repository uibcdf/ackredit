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


def _matrix_workflows() -> list[str]:
    """Every workflow whose `test` job runs a Python matrix.

    Derived rather than listed: the weekly matrix gained the same evidence lane
    as CI.yaml, and a guard that read only CI.yaml would have let the defect of
    `uibcdf/ackredit#64` return there unseen.
    """
    found = []
    for path in WORKFLOWS:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        job = (document.get("jobs") or {}).get("test") or {}
        if "python-version" in ((job.get("strategy") or {}).get("matrix") or {}):
            found.append(path.name)
    return found


def _workflow(name: str) -> dict:
    return yaml.safe_load(
        (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
    )


def _matrix(name: str) -> dict:
    return _workflow(name)["jobs"]["test"]["strategy"]["matrix"]


def _contract_versions() -> list[str]:
    """The minor versions `requires-python` promises."""
    import re
    import tomllib

    contract = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = contract["project"]["requires-python"]
    low, high = re.findall(r"3\.(\d+)", declared)
    return [f"3.{minor}" for minor in range(int(low), int(high))]


def test_both_matrix_workflows_are_found():
    """The parametrised guards below are vacuous if this finds nothing."""
    assert {"CI.yaml", "CI_full_matrix.yaml"} <= set(_matrix_workflows())


@pytest.mark.parametrize("workflow", _matrix_workflows())
def test_ci_runs_every_version_the_contract_promises(workflow):
    """It ran 3.13 alone while promising 3.11 to 3.13, so two of the three had
    never been run by anything — `uibcdf/ackredit#63`. A version promised and
    never executed is found by the user who has it."""
    assert sorted(_matrix(workflow)["python-version"]) == sorted(_contract_versions())


@pytest.mark.parametrize("workflow", _matrix_workflows())
def test_required_workflows_have_no_unsupported_or_tolerated_test_cells(workflow):
    promised = set(_contract_versions())
    for entry in _matrix(workflow).get("include", []):
        assert entry["python-version"] in promised, entry
    job = _workflow(workflow)["jobs"]["test"]
    assert not job.get("continue-on-error", False)
    assert all(not step.get("continue-on-error", False) for step in job["steps"])


def test_feasibility_is_explicit_and_its_failure_stays_visible():
    document = _workflow("python314_feasibility.yaml")
    events = document.get("on", document.get(True))
    assert set(events) == {"workflow_dispatch"}
    job = document["jobs"]["feasibility"]
    assert set(job["strategy"]["matrix"]["python-version"]).isdisjoint(
        _contract_versions()
    )
    assert not job.get("continue-on-error", False)
    assert all(not step.get("continue-on-error", False) for step in job["steps"])


# --- a lane that never reached a test ---------------------------------------
#
# The first 3.14 lane asked micromamba for `python=3.14` against an environment
# file pinned to `python >=3.11,<3.14`. The solver refused, the job died in
# "Setup conda env", and because the lane is non-blocking the run was green with
# nothing measured (`uibcdf/ackredit#64`). Nothing here had noticed that a
# matrix can request a version its own environment forbids.


def _step(workflow: str, name: str) -> dict:
    job_name = "feasibility" if workflow == "python314_feasibility.yaml" else "test"
    for step in _workflow(workflow)["jobs"][job_name]["steps"]:
        if step.get("name") == name:
            return step
    raise AssertionError(f"the test job of {workflow} has no step named {name!r}")


def _environment_file(workflow: str) -> Path:
    return ROOT / _step(workflow, "Setup conda env")["with"]["environment-file"]


def _python_spec(environment: Path) -> str:
    document = yaml.safe_load(environment.read_text(encoding="utf-8"))
    for dependency in document["dependencies"]:
        if isinstance(dependency, str) and dependency.split()[0] == "python":
            return dependency
    raise AssertionError(f"{environment.name} names no interpreter")


def _admits(spec: str, version: str) -> bool:
    import re

    asked = tuple(int(part) for part in version.split("."))
    for operator, bound in re.findall(r"(>=|<=|<|>|==)\s*(\d+(?:\.\d+)*)", spec):
        limit = tuple(int(part) for part in bound.split("."))
        compared = asked[: len(limit)] if operator in (">=", "<=", "==") else asked
        padded = limit + (0,) * (len(compared) - len(limit))
        if operator == ">=" and not compared >= limit[: len(compared)]:
            return False
        if operator == "<" and not asked + (0,) * (len(padded) - len(asked)) < padded:
            return False
        if operator == "<=" and not compared <= limit[: len(compared)]:
            return False
        if operator == ">" and not compared > limit[: len(compared)]:
            return False
        if operator == "==" and compared != limit[: len(compared)]:
            return False
    return True


def _cells() -> list[tuple[str, str]]:
    cells = []
    for workflow in _matrix_workflows():
        matrix = _matrix(workflow)
        cells += [(workflow, version) for version in matrix["python-version"]]
        cells += [
            (workflow, entry["python-version"]) for entry in matrix.get("include", [])
        ]
    feasibility = _workflow("python314_feasibility.yaml")["jobs"]["feasibility"]
    cells += [
        ("python314_feasibility.yaml", version)
        for version in feasibility["strategy"]["matrix"]["python-version"]
    ]
    return cells


def test_the_helper_that_reads_a_version_bound_works():
    """The guard below is only as good as this, and a bound is easy to misread."""
    assert _admits("python >=3.11,<3.14", "3.13")
    assert not _admits("python >=3.11,<3.14", "3.14")
    assert not _admits("python >=3.11,<3.14", "3.10")
    assert _admits("python >=3.14,<3.15", "3.14")
    assert not _admits("python >=3.14,<3.15", "3.13")


@pytest.mark.parametrize("workflow,version", _cells())
def test_every_matrix_version_is_admitted_by_its_environment(workflow, version):
    """A cell whose environment forbids its interpreter dies in the solver, and
    a non-blocking one dies in silence."""
    environment = _environment_file(workflow)
    spec = _python_spec(environment)

    assert _admits(spec, version), (
        f"{workflow} asks for python {version} and {environment.name} "
        f"pins `{spec}`, which the solver cannot satisfy"
    )


def test_the_evidence_environment_is_the_contract_environment_but_for_python():
    """Feasibility measures the new interpreter against the same dependencies."""
    promised = yaml.safe_load(_environment_file("CI.yaml").read_text(encoding="utf-8"))
    evidence = yaml.safe_load(
        _environment_file("python314_feasibility.yaml").read_text(encoding="utf-8")
    )

    def without_python(document):
        return [
            item
            for item in document["dependencies"]
            if not (isinstance(item, str) and item.split()[0] == "python")
        ]

    assert promised["channels"] == evidence["channels"]
    assert without_python(promised) == without_python(evidence)


@pytest.mark.parametrize(
    "workflow", _matrix_workflows() + ["python314_feasibility.yaml"]
)
def test_only_the_feasibility_workflow_ignores_the_contract(workflow):
    install = _step(workflow, "Install package")["run"]
    assert ("--ignore-requires-python" in install) is (
        workflow == "python314_feasibility.yaml"
    )
