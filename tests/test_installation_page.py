"""The installation page is the one a user follows literally.

It pinned `@0.6.0` after `0.7.0` was tagged, and its `conda create` line kept
naming the dependencies of a release that no longer described `main`: ArgDigest
became a runtime dependency in `uibcdf/ackredit#62`, the page never learnt it,
and raising the pin at the next release — the one edit that looks sufficient —
would have produced an environment where `import ackredit` fails
(`uibcdf/ackredit#66`).

Both facts already have an authority. `CITATION.cff` is held to the release by
its own guard, and `pyproject.toml` declares what the package needs. This holds
the page to them rather than to someone remembering.
"""

import re
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "content" / "about" / "installation.md"


def _page() -> str:
    return PAGE.read_text(encoding="utf-8")


def _release() -> str:
    return str(
        yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))["version"]
    )


def _runtime_dependencies() -> list[str]:
    declared = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return [
        re.split(r"[<>=!~;\[ ]", requirement, maxsplit=1)[0].strip().lower()
        for requirement in declared["project"]["dependencies"]
    ]


# Where the page states which release to install. Prose such as "the release
# before 1.0.0" is not an install instruction and is left alone.
_STATED = [
    re.compile(r"ackredit@(\d+\.\d+\.\d+)"),
    re.compile(r"__version__\s*#\s*'(\d+\.\d+\.\d+)'"),
    re.compile(r"`(\d+\.\d+\.\d+)\+\d+\.g[0-9a-f]+`"),
]


def test_the_page_installs_the_current_release():
    stated = [found for pattern in _STATED for found in pattern.findall(_page())]

    assert stated, "the page no longer says which release to install; update this guard"
    assert set(stated) == {_release()}, (
        f"the page states {sorted(set(stated))}; CITATION.cff names {_release()}"
    )


def test_the_environment_it_creates_can_import_ackredit():
    """`pip install --no-deps` installs nothing else, so whatever the conda line
    leaves out is simply missing."""
    lines = [line for line in _page().splitlines() if line.startswith("conda create")]
    assert lines, "the page no longer shows the environment it creates"

    for line in lines:
        named = {word.lower() for word in line.split()}
        missing = [name for name in _runtime_dependencies() if name not in named]
        assert not missing, f"`{line}` leaves out {missing}"


def test_the_helper_reads_requirements_by_name():
    """The guard above is only as good as this."""
    assert "argdigest" in _runtime_dependencies()
    assert all(re.fullmatch(r"[a-z0-9_.-]+", name) for name in _runtime_dependencies())
