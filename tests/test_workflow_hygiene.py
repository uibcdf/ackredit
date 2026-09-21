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
