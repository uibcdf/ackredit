"""Coverage has an explicit scope and publishes only retained, trusted reports."""

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _workflow():
    return yaml.safe_load((ROOT / ".github/workflows/coverage.yaml").read_text())


def test_coverage_does_not_add_a_suite_to_internal_pushes():
    workflow = _workflow()
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) == {"schedule", "workflow_dispatch"}
    assert triggers["schedule"] == [{"cron": "43 6 * * MON"}]
    assert workflow["permissions"] == {"contents": "read"}


def test_the_full_installed_suite_is_measured_without_a_coverage_floor():
    workflow = _workflow()
    steps = workflow["jobs"]["measure"]["steps"]
    install = next(step for step in steps if step.get("name") == "Install package")
    assert "pip install . --no-deps" in install["run"]
    tests = next(
        step for step in steps if step.get("name") == "Run tests with runtime coverage"
    )
    command = tests["run"]
    assert 'cd "${RUNNER_TEMP}"' in command
    assert "coverage run" in command
    assert '-m pytest --receptor=ci "${GITHUB_WORKSPACE}/tests"' in command
    assert not tests.get("continue-on-error")
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())["tool"]["coverage"]
    assert config["run"]["source"] == ["ackredit"]
    assert config["run"]["omit"] == ["*/ackredit/_version.py"]
    assert config.get("report", {}).get("fail_under", 0) == 0
    assert config["paths"]["ackredit"][0] == "ackredit"


def test_upload_consumes_the_exact_retained_report_with_trusted_oidc():
    jobs = _workflow()["jobs"]
    upload = jobs["upload"]
    assert upload["needs"] == "measure"
    assert upload["if"] == "github.ref == 'refs/heads/main'"
    assert upload["permissions"] == {"contents": "read", "id-token": "write"}
    retained = next(
        step
        for step in jobs["measure"]["steps"]
        if "upload-artifact@" in step.get("uses", "")
    )
    download = next(
        step for step in upload["steps"] if "download-artifact@" in step.get("uses", "")
    )
    assert retained["with"]["name"] == download["with"]["name"]
    assert retained["with"]["path"] == "coverage.xml"
    assert retained["with"]["if-no-files-found"] == "error"
    publisher = next(
        step
        for step in upload["steps"]
        if step.get("name") == "Upload measured report to Codecov"
    )
    assert (
        publisher["uses"]
        == "codecov/codecov-action@303a32d7a59b442fa8d48b6a1cc6825c09c847a5"
    )
    assert publisher["with"] == {
        "use_oidc": True,
        "files": "coverage-report/coverage.xml",
        "disable_search": True,
        "fail_ci_if_error": True,
    }
    assert not publisher.get("continue-on-error")


@pytest.mark.parametrize("complete", [True, False])
def test_report_scope_verifier_refuses_an_omitted_runtime_module(tmp_path, complete):
    package = tmp_path / "ackredit"
    package.mkdir()
    for name in ("__init__.py", "optional.py", "_version.py"):
        (package / name).write_text("value = 1\n")
    files = ["__init__.py", "optional.py"] if complete else ["__init__.py"]
    classes = "".join(
        f'<class filename="{name}"><lines><line number="1" hits="1"/></lines></class>'
        for name in files
    )
    (tmp_path / "coverage.xml").write_text(
        f'<coverage lines-valid="{len(files)}" lines-covered="{len(files)}">'
        f"<sources><source>{package}</source></sources>"
        f"<packages><package><classes>{classes}</classes></package></packages></coverage>"
    )
    steps = _workflow()["jobs"]["measure"]["steps"]
    step = next(s for s in steps if s.get("name") == "Verify coverage report scope")
    code = step["run"].split("python - <<'PYTHON'\n", 1)[1].rsplit("\nPYTHON", 1)[0]
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=tmp_path, text=True, capture_output=True
    )
    assert result.returncode == (0 if complete else 1), result.stderr
