"""Consumer dispatch preserves the shared tool's identity and rejection outcome."""

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "devtools/check_dependency_routes.py"
spec = importlib.util.spec_from_file_location("ackredit_dependency_routes", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


@pytest.fixture
def provider(tmp_path):
    root = tmp_path / "provider"
    tool = root / "devtools/scripts/dependency_routes.py"
    tool.parent.mkdir(parents=True)
    tool.write_text(
        "import argparse\n"
        "from pathlib import Path\n"
        "p = argparse.ArgumentParser()\n"
        "p.add_argument('--root', type=Path)\n"
        "p.add_argument('--inventory')\n"
        "a = p.parse_args()\n"
        "assert a.inventory == 'devtools/dependency_routes.toml'\n"
        "print('shared rejection: ' + str(a.root.resolve()))\n"
        "raise SystemExit(1)\n"
    )

    def git(*arguments):
        return subprocess.check_output(["git", *arguments], cwd=root, text=True).strip()

    git("init", "-q")
    git("add", "devtools")
    git(
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "Reviewed tool",
    )
    return root, git("rev-parse", "HEAD"), tool


def test_different_provider_commit_is_refused(provider):
    root, _, _ = provider
    with pytest.raises(ValueError, match="expected"):
        check.checked_tool(root, "0" * 40)


@pytest.mark.parametrize("change", ["modified", "untracked"])
def test_changed_provider_code_is_refused_before_execution(provider, change):
    root, commit, tool = provider
    if change == "modified":
        tool.write_text("raise SystemExit(0)\n")
    else:
        (tool.parent / "noarch_conda.py").write_text("unreviewed = True\n")
    with pytest.raises(ValueError, match="modified or untracked"):
        check.checked_tool(root, commit)


def test_shared_failure_exit_and_consumer_root_are_retained(provider, tmp_path):
    root, commit, _ = provider
    consumer = tmp_path / "consumer"
    (consumer / "devtools").mkdir(parents=True)
    (consumer / "devtools/dependency_routes.toml").write_text(
        f'[shared_tool]\ncommit = "{commit}"\n'
    )
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            "--suite-root",
            str(root),
            "--root",
            str(consumer),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert f"shared rejection: {consumer.resolve()}" in result.stdout
