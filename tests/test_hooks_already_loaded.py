"""An injection is credited whether its module arrived before the hook or after.

The finder sees imports, and an import of a module already in `sys.modules`
never reaches a finder. So a module loaded before `enable_import_hooks()` was
never credited — and since `uibcdf/ackredit#62`, `import ackredit` loads numpy
itself, through ArgDigest. The user guide's discovery example and the
integration guide's injection recipe both credited nothing for numpy, and the
old root demo that exercised it exited 0 (`uibcdf/ackredit#69`).

Declared injections are now credited either way. Discovery is deliberately not
swept, and a test here holds that too.

The standard library, meanwhile, was discovered module by module and warned for
each one (`uibcdf/ackredit#70`).

Import state is process-wide, so every case runs in a fresh interpreter.
"""

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def in_a_fresh_process(body: str) -> dict:
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(body)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr[-2000:]
    return {
        "out": json.loads(result.stdout.strip().splitlines()[-1]),
        "err": result.stderr,
    }


# --- injections ---------------------------------------------------------------


def test_an_injection_on_a_module_ackredit_already_loaded_is_credited():
    """The integration guide's recipe, on the package it names."""
    run = in_a_fresh_process("""
        import json, sys
        import ackredit

        assert "numpy" in sys.modules, "the case needs numpy loaded before the hook"
        ackredit.register_item(id="paper:numpy", type="article", title="NumPy")
        ackredit.add_injection("numpy", ["paper:numpy"])
        ackredit.enable_import_hooks()
        import numpy
        print(json.dumps(sorted(ackredit.get_used_items())))
    """)
    assert run["out"] == ["paper:numpy"]


def test_an_injection_declared_after_the_hook_is_on_is_credited():
    run = in_a_fresh_process("""
        import json, sys
        import ackredit

        ackredit.enable_import_hooks()
        assert "yaml" in sys.modules
        ackredit.register_item(id="paper:yaml", type="software", title="PyYAML")
        ackredit.add_injection("yaml", ["paper:yaml"])
        print(json.dumps(sorted(ackredit.get_used_items())))
    """)
    assert run["out"] == ["paper:yaml"]


def test_a_module_the_host_imported_first_is_credited():
    """The ordinary host: a submodule imports a package before `__init__`
    reaches the line that enables the hook."""
    run = in_a_fresh_process("""
        import json, sys
        import ackredit
        import csv  # the host's submodule, imported first

        ackredit.register_item(id="paper:csv", type="article", title="CSV")
        ackredit.add_injection("csv", ["paper:csv"])
        ackredit.enable_import_hooks()
        print(json.dumps(sorted(ackredit.get_used_items())))
    """)
    assert run["out"] == ["paper:csv"]


def test_an_injection_on_a_module_not_yet_imported_waits_for_the_import(tmp_path):
    """A module written for the test, because whether a real one is already
    loaded depends on the interpreter: `import ackredit` loads `csv` on Python
    3.11 and 3.12 and not on 3.13, which is how this case first failed in CI."""
    (tmp_path / "injected_probe.py").write_text("VALUE = 1\n", encoding="utf-8")
    run = in_a_fresh_process(f"""
        import json, sys
        sys.path.insert(0, {str(tmp_path)!r})
        import ackredit

        assert "injected_probe" not in sys.modules
        ackredit.register_item(id="paper:probe", type="article", title="Probe")
        ackredit.add_injection("injected_probe", ["paper:probe"])
        ackredit.enable_import_hooks()
        before = sorted(ackredit.get_used_items())
        import injected_probe
        after = sorted(ackredit.get_used_items())
        print(json.dumps([before, after]))
    """)
    assert run["out"] == [[], ["paper:probe"]]


def test_without_the_hook_an_injection_credits_nothing():
    """Injections belong to the import hooks; declaring one does not enable them."""
    run = in_a_fresh_process("""
        import json
        import ackredit

        ackredit.register_item(id="paper:numpy", type="article", title="NumPy")
        ackredit.add_injection("numpy", ["paper:numpy"])
        print(json.dumps(sorted(ackredit.get_used_items())))
    """)
    assert run["out"] == []


# --- discovery is not swept ---------------------------------------------------


def test_discovery_credits_nothing_that_was_already_loaded():
    """Sweeping `sys.modules` would credit Ackredit's own dependencies in every
    report, and in a notebook the 32 packages an empty kernel loads."""
    run = in_a_fresh_process("""
        import json, sys
        import ackredit

        assert {"numpy", "smonitor", "argdigest"} <= set(sys.modules)
        ackredit.enable_import_hooks()
        assert "yaml" in sys.modules, "the hook loads it, through the CITATION.cff reader"
        import numpy, yaml, argdigest
        print(json.dumps(sorted(ackredit.get_used_items())))
    """)
    assert run["out"] == []


# --- the standard library -----------------------------------------------------

# Which of these `import ackredit` has already loaded depends on the Python
# version, so the test uses whichever are fresh and requires enough of them.
_STDLIB = [
    "sqlite3",
    "decimal",
    "fractions",
    "colorsys",
    "wave",
    "mailbox",
    "csv",
    "json",
]


def test_importing_the_standard_library_is_silent_and_credits_nothing():
    run = in_a_fresh_process(f"""
        import json, sys, warnings
        import ackredit

        fresh = [name for name in {_STDLIB!r} if name not in sys.modules]
        assert len(fresh) >= 3, f"too few unimported stdlib modules to test: {{fresh}}"
        ackredit.enable_import_hooks()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            for name in fresh:
                __import__(name)
        print(json.dumps({{
            "credited": sorted(ackredit.get_used_items()),
            "warnings": [str(w.message) for w in caught],
        }}))
    """)
    assert run["out"]["credited"] == []
    assert run["out"]["warnings"] == []
    assert "No citation information" not in run["err"]


def test_an_injection_on_a_standard_library_module_is_still_honoured():
    """Skipping discovery for the standard library is not refusing a person."""
    run = in_a_fresh_process("""
        import json
        import ackredit

        ackredit.register_item(id="paper:sqlite", type="software", title="SQLite")
        ackredit.add_injection("sqlite3", ["paper:sqlite"])
        ackredit.enable_import_hooks()
        import sqlite3
        print(json.dumps(sorted(ackredit.get_used_items())))
    """)
    assert run["out"] == ["paper:sqlite"]


# --- what the documentation promises ------------------------------------------


def _footprint() -> set[str]:
    """Top-level packages `import ackredit` loads by itself."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys, json; before = set(sys.modules); import ackredit; "
            "print(json.dumps(sorted({m.split('.')[0] for m in set(sys.modules) - before})))",
        ],
        capture_output=True,
        text=True,
    )
    loaded = set(json.loads(result.stdout))
    return {name for name in loaded if name not in sys.stdlib_module_names}


def _documents():
    for path in [ROOT / "README.md", ROOT / "standards" / "ACKREDIT_GUIDE.md"]:
        yield path
    yield from (ROOT / "docs" / "content").rglob("*.md")


def test_no_page_shows_discovery_crediting_a_package_ackredit_loads_itself():
    """Discovery cannot see a package that was loaded before it, and Ackredit
    loads some packages itself. A page showing `enable_import_hooks()` and then
    `import numpy` as discovery promises what cannot happen."""
    footprint = _footprint()
    assert "numpy" in footprint or "yaml" in footprint, "the footprint probe is broken"

    promised = []
    for path in _documents():
        text = path.read_text(encoding="utf-8")
        for block in re.findall(r"```python\n(.*?)```", text, re.S):
            if "enable_import_hooks()" not in block or "add_injection" in block:
                continue
            after = block.split("enable_import_hooks()", 1)[1]
            for name in re.findall(r"^\s*import (\w+)", after, re.M):
                if name in footprint:
                    promised.append(f"{path.relative_to(ROOT)}: import {name}")

    assert not promised, promised
