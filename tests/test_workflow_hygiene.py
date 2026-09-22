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


# --- a lane that never reached a test ---------------------------------------
#
# The first 3.14 lane asked micromamba for `python=3.14` against an environment
# file pinned to `python >=3.11,<3.14`. The solver refused, the job died in
# "Setup conda env", and because the lane is non-blocking the run was green with
# nothing measured (`uibcdf/ackredit#64`). Nothing here had noticed that a
# matrix can request a version its own environment forbids.


def _test_steps() -> list[dict]:
    return _ci()["jobs"]["test"]["steps"]


def _step(name: str) -> dict:
    for step in _test_steps():
        if step.get("name") == name:
            return step
    raise AssertionError(f"the test job has no step named {name!r}")


def _resolve(expression: str, experimental: bool) -> str:
    """Read a `${{ matrix.experimental && 'a' || 'b' }}` choice the way GitHub does."""
    import re

    match = re.search(
        r"\$\{\{\s*matrix\.experimental\s*&&\s*'([^']*)'\s*\|\|\s*'([^']*)'\s*\}\}",
        expression,
    )
    if not match:
        return expression
    chosen = match.group(1) if experimental else match.group(2)
    return expression[: match.start()] + chosen + expression[match.end() :]


def _environment_file(experimental: bool) -> Path:
    declared = _step("Setup conda env")["with"]["environment-file"]
    return ROOT / _resolve(declared, experimental)


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


def _cells() -> list[tuple[str, bool]]:
    matrix = _ci()["jobs"]["test"]["strategy"]["matrix"]
    cells = [(version, False) for version in matrix["python-version"]]
    cells += [
        (entry["python-version"], entry["experimental"])
        for entry in matrix.get("include", [])
    ]
    return cells


def test_the_helper_that_reads_a_version_bound_works():
    """The guard below is only as good as this, and a bound is easy to misread."""
    assert _admits("python >=3.11,<3.14", "3.13")
    assert not _admits("python >=3.11,<3.14", "3.14")
    assert not _admits("python >=3.11,<3.14", "3.10")
    assert _admits("python >=3.14,<3.15", "3.14")
    assert not _admits("python >=3.14,<3.15", "3.13")


@pytest.mark.parametrize("version,experimental", _cells())
def test_every_matrix_version_is_admitted_by_its_environment(version, experimental):
    """A cell whose environment forbids its interpreter dies in the solver, and
    a non-blocking one dies in silence."""
    environment = _environment_file(experimental)
    spec = _python_spec(environment)

    assert _admits(spec, version), (
        f"the matrix asks for python {version} and {environment.name} "
        f"pins `{spec}`, which the solver cannot satisfy"
    )


def test_the_evidence_environment_is_the_contract_environment_but_for_python():
    """Two environments that drift apart stop being comparable, and then the
    lane no longer says what it claims to say about the new interpreter."""
    promised = yaml.safe_load(_environment_file(False).read_text(encoding="utf-8"))
    evidence = yaml.safe_load(_environment_file(True).read_text(encoding="utf-8"))

    def without_python(document):
        return [
            item
            for item in document["dependencies"]
            if not (isinstance(item, str) and item.split()[0] == "python")
        ]

    assert promised["channels"] == evidence["channels"]
    assert without_python(promised) == without_python(evidence)


def test_only_the_experimental_lane_ignores_the_contract():
    """`requires-python` is what stops an unsupported interpreter installing the
    package. Bypassing it in a gating lane would retire that protection without
    anyone deciding to."""
    install = _step("Install package")["run"]

    assert "--ignore-requires-python" in install, (
        "the evidence lane cannot install under a `<3.14` contract without it"
    )
    assert _resolve(install, experimental=False).count("--ignore-requires-python") == 0
    assert _resolve(install, experimental=True).count("--ignore-requires-python") == 1
