"""The declared test tool and the tool checked before hosted tests must agree."""

import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _receptor_pins():
    pins = []
    for path in sorted((ROOT / "devtools/conda-envs").glob("*.yaml")):
        dependencies = yaml.safe_load(path.read_text())["dependencies"]
        for dependency in dependencies:
            if isinstance(dependency, str) and dependency.startswith("pytest-receptor"):
                match = re.fullmatch(r"pytest-receptor ==(\d+\.\d+\.\d+)", dependency)
                assert match, f"{path.name}: test tool needs an exact published pin"
                pins.append(match.group(1))
    assert len(pins) >= 3, (
        "development and both test environments must declare the tool"
    )
    assert len(set(pins)) == 1, "maintained environments disagree on the receptor"
    return pins[0]


def _hosted_test_jobs():
    jobs = []
    for path in sorted((ROOT / ".github/workflows").glob("*.y*ml")):
        document = yaml.safe_load(path.read_text())
        for name, job in document.get("jobs", {}).items():
            steps = job.get("steps", [])
            tests = [
                index
                for index, step in enumerate(steps)
                if "--receptor=ci" in step.get("run", "")
            ]
            if tests:
                jobs.append((f"{path.name}:{name}", steps, tests))
    assert len(jobs) >= 3, (
        "routine, full and dedicated installed tests must be inspected"
    )
    return jobs


def _verification_code(steps):
    matches = [
        (index, step)
        for index, step in enumerate(steps)
        if step.get("name") == "Verify installed Pytest Receptor version"
    ]
    assert len(matches) == 1, "hosted tests need an explicit installed-version check"
    index, step = matches[0]
    assert not step.get("continue-on-error")
    command = shlex.split(step["run"])
    assert len(command) == 3 and command[:2] == ["python", "-c"]
    return index, command[2]


def test_maintained_test_environments_pin_one_receptor_release():
    _receptor_pins()


def test_every_hosted_test_job_checks_its_declared_tool_before_tests():
    pin = _receptor_pins()
    for label, steps, tests in _hosted_test_jobs():
        index, code = _verification_code(steps)
        assert index < min(tests), label
        assert 'version("pytest-receptor")' in code, label
        assert f'assert actual == "{pin}"' in code, label


@pytest.mark.parametrize("matches_pin", [True, False])
def test_hosted_version_check_rejects_a_different_installed_tool(matches_pin):
    pin = _receptor_pins()
    observed = pin if matches_pin else "0.0.0"
    for label, steps, _ in _hosted_test_jobs():
        _, code = _verification_code(steps)
        probe = (
            "from unittest.mock import patch\n"
            f"with patch('importlib.metadata.version', return_value={observed!r}):\n"
            f"    exec({code!r})\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe], capture_output=True, text=True
        )
        assert result.returncode == (0 if matches_pin else 1), (
            label,
            result.stdout,
            result.stderr,
        )
        assert f"pytest-receptor {observed}" in result.stdout
