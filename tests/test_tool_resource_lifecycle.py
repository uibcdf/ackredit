"""Exercise scratch owners without builds, scientific callbacks or downloads (#132)."""

from __future__ import annotations

import importlib
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("operation", ["lifecycle", "provenance", "plugins"])
@pytest.mark.parametrize("failure", [None, "callback", "cleanup", "both"])
def test_scratch_cleans_both_exits_and_never_removes_caller_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    operation: str,
    failure: str | None,
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "devtools"))
    lifecycle = importlib.import_module("benchmark_lifecycle")
    provenance = importlib.import_module("benchmark_provenance")
    plugins = importlib.import_module("benchmark_plugins")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    caller = tmp_path / "caller.txt"
    caller.write_text("caller-owned evidence")
    output = tmp_path / "output"
    monkeypatch.setattr(tempfile, "tempdir", str(scratch))
    seen: set[Path] = set()

    def callback() -> None:
        roots = list(scratch.iterdir())
        assert len(roots) == 1
        seen.update(roots)
        (roots[0] / "owned.txt").write_text("scratch payload")
        if failure in ("callback", "both"):
            raise RuntimeError("controlled callback failure")

    if failure in ("cleanup", "both"):

        def refuse_removal(cls: type, name: str, **kwargs: object) -> None:
            assert Path(name) in seen
            raise PermissionError("controlled cleanup failure")

        monkeypatch.setattr(
            tempfile.TemporaryDirectory, "_rmtree", classmethod(refuse_removal)
        )

    def child(command: list[str], **kwargs: object) -> SimpleNamespace:
        if "--reader" in command:
            return SimpleNamespace(
                stdout=json.dumps({"references": 1, "json_sha256": "fixture"}),
                stderr="",
            )
        callback()
        cwd = Path(str(kwargs["cwd"]))
        assert cwd.is_relative_to(scratch)
        field = "retained_delta_bytes" if "--memory" in command else "elapsed_us"
        result = {
            "identities": {},
            "measurements": {"stage": {field: 1}},
            "facts": {"references": 1, "json_sha256": "fixture"},
        }
        if "operations" in command:
            result["detached"] = "original detached fixture"
        return SimpleNamespace(stdout=json.dumps(result), stderr="")

    monkeypatch.setattr(lifecycle, "child", child)

    def measure(*args: object) -> dict:
        callback()
        return {"samples": [1], "median": 1}

    monkeypatch.setattr(provenance, "measure", measure)

    def environment(directory: Path, wheels: list[Path]) -> Path:
        directory.mkdir(parents=True)
        return directory / "python"

    monkeypatch.setattr(plugins, "environment", environment)
    monkeypatch.setattr(plugins, "build_packs", lambda *args, **kwargs: {})
    core = tmp_path / "core"
    core.mkdir()
    (core / "manifest.json").write_text("{}")

    def invoke() -> None:
        if operation == "lifecycle":
            lifecycle.study({"fixture": {"kind": "references"}}, 2, 2)
        elif operation == "plugins":
            plugins.study(core, output, 2, 2)
        else:
            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "benchmark_provenance.py",
                    "--baseline",
                    "HEAD",
                    "--samples",
                    "1",
                    "--iterations",
                    "1",
                    "--output",
                    str(output),
                ],
            )
            provenance.main()

    if failure:
        cleanup_failed = failure in ("cleanup", "both")
        error = PermissionError if cleanup_failed else RuntimeError
        message = (
            "controlled cleanup failure"
            if cleanup_failed
            else "controlled callback failure"
        )
        with pytest.raises(error, match=message) as caught:
            invoke()
        if failure == "both":
            assert isinstance(caught.value.__context__, RuntimeError)
            assert "controlled callback failure" in str(caught.value.__context__)
    else:
        invoke()

    assert seen, "the actual tool must enter its scratch scope"
    assert caller.read_text() == "caller-owned evidence"
    assert (core / "manifest.json").read_text() == "{}"
    if failure in ("cleanup", "both"):
        assert set(scratch.iterdir()) == seen
    else:
        assert not list(scratch.iterdir())
        assert all(not path.exists() for path in seen)
    if operation == "plugins":
        assert output.is_dir(), "explicit installed-variant output is caller-owned"
        assert (output / "packs_0_references_1/env").is_dir()
        if not failure:
            assert (output / "packs_0_references_1/detached.json").read_text() == (
                "original detached fixture"
            )
    elif operation == "provenance" and not failure:
        assert (
            json.loads(output.read_text())["schema"]
            == "ackredit.provenance-benchmark@1"
        )
