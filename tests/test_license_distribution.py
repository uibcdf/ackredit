"""Actual wheel/sdist payloads must preserve Ackredit's SPDX and original notice."""

import shutil
import subprocess
import sys
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_wheel_sdist_and_rebuilt_wheel_preserve_license(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for name in ("pyproject.toml", "README.md", "LICENSE"):
        shutil.copy2(ROOT / name, source / name)
    shutil.copytree(
        ROOT / "ackredit",
        source / "ackredit",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    original = (ROOT / "LICENSE").read_bytes()

    def build(directory, target, output):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "build",
                "--no-isolation",
                target,
                "--outdir",
                str(output),
                str(directory),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    def wheel_notice(path):
        with zipfile.ZipFile(path) as archive:
            (metadata_path,) = [
                name
                for name in archive.namelist()
                if name.endswith(".dist-info/METADATA")
            ]
            metadata = BytesParser().parsebytes(archive.read(metadata_path))
            assert metadata["License-Expression"] == "MIT"
            assert metadata.get_all("License-File") == ["LICENSE"]
            notice = metadata_path.removesuffix("METADATA") + "licenses/LICENSE"
            assert archive.read(notice) == original

    output = tmp_path / "original"
    build(source, "--wheel", output)
    wheel_notice(next(output.glob("*.whl")))
    build(source, "--sdist", output)
    unpacked = tmp_path / "unpacked"
    unpacked.mkdir()
    with tarfile.open(next(output.glob("*.tar.gz"))) as archive:
        archive.extractall(unpacked, filter="data")
    (rebuilt_source,) = unpacked.iterdir()
    assert (rebuilt_source / "LICENSE").read_bytes() == original
    metadata = BytesParser().parsebytes((rebuilt_source / "PKG-INFO").read_bytes())
    assert metadata["License-Expression"] == "MIT"
    assert metadata.get_all("License-File") == ["LICENSE"]
    rebuilt = tmp_path / "rebuilt"
    build(rebuilt_source, "--wheel", rebuilt)
    wheel_notice(next(rebuilt.glob("*.whl")))
