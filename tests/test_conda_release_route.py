"""Publication uses one staged artifact and the executed installed-matrix receipt."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _workflow(name):
    return yaml.load(
        (ROOT / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader
    )


def test_staging_and_promotion_cannot_rebuild_under_the_same_coordinate():
    stage = _workflow("build_and_upload_conda_packages.yaml")
    promote = _workflow("promote_conda_package.yaml")
    assert set(stage["on"]) == {"workflow_dispatch"}
    assert set(promote["on"]) == {"workflow_dispatch"}
    assert "promote" not in stage["on"]["workflow_dispatch"]["inputs"]
    for workflow, phase in ((stage, "stage"), (promote, "promote")):
        job = workflow["jobs"][phase]
        assert "steps" not in job
        assert re.fullmatch(r"[0-9a-f]{40}", job["uses"].split("@")[1])
    promoted = promote["jobs"]["promote"]
    assert "/promote-noarch-conda.yaml@" in promoted["uses"]
    assert {"candidate_sha", "version", "sha256", "installed_run_id"} <= set(
        promoted["with"]
    )


def test_installed_qualification_identifies_the_exact_file_without_a_secret():
    installed = _workflow("test_staged_conda_package.yaml")
    assert set(installed["on"]) == {"workflow_dispatch"}
    assert installed["run-name"] == (
        "Installed ${{ inputs.filename }} ${{ inputs.sha256 }}"
    )
    job = installed["jobs"]["installed"]
    assert "secrets" not in job
    assert {"candidate_sha", "filename", "sha256"} == set(job["with"])
    assert "/test-installed-noarch-conda.yaml@" in job["uses"]


def test_administrative_qualification_retains_explicit_original_producer_identity():
    installed = _workflow("test_staged_conda_package.yaml")
    promote = _workflow("promote_conda_package.yaml")
    assert installed["jobs"]["installed"]["with"]["candidate_sha"] == (
        "${{ inputs.candidate_sha }}"
    )
    promoted = promote["jobs"]["promote"]
    assert promoted["with"]["candidate_sha"] == "${{ inputs.candidate_sha }}"
    assert promoted["with"]["qualification_sha"] == "${{ inputs.qualification_sha }}"
    assert "qualification_sha" in promote["on"]["workflow_dispatch"]["inputs"]
    assert (
        installed["jobs"]["installed"]["uses"].split("@")[1]
        == (promoted["uses"].split("@")[1])
    )
