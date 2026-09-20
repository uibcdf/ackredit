"""The five checks of SMONITOR_GUIDE.md section 7, plus one of our own.

Each covers a failure mode that raises nothing, fails no test and prints no
warning. They only make diagnostics say less than they should, and are found
months later by a user reporting "the error message was blank".
"""

import ast
import pathlib
import subprocess
import sys
import warnings

import pytest

from ackredit._private.smonitor import CATALOG, CODES, META, PACKAGE_ROOT
from ackredit._private.smonitor import exceptions as exc_module
from ackredit._private.smonitor import warnings as warn_module
from ackredit._private.smonitor.emitter import bundle

ROOT = pathlib.Path(__file__).resolve().parents[1]

PROFILES = ("user", "dev", "qa", "agent", "debug")

# Names CatalogException and CatalogWarning assign last, from what they were
# given. A subclass that sets one before calling super() writes into a variable
# the base is about to overwrite, and the value is silently discarded.
BASE_OWNED = {"code", "message", "raw_message", "extra", "hint"}

CATALOG_CLASSES = [
    getattr(module, name)
    for module in (warn_module, exc_module)
    for name in module.__all__
    if getattr(getattr(module, name), "catalog_key", None)
]


def test_the_configuration_is_inside_the_package():
    """A _smonitor.py outside the package is found in a checkout and absent
    from the wheel, and that difference is invisible from a dev environment."""
    assert (PACKAGE_ROOT / "_smonitor.py").is_file()
    assert PACKAGE_ROOT.name == "ackredit"
    assert (PACKAGE_ROOT / "__init__.py").is_file()


def test_check_1_the_configuration_is_found_and_understood():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "smonitor.cli",
            "--validate-config",
            "--config-path",
            "ackredit",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(ROOT), "PATH": "/usr/bin:/bin"},
    )
    if result.returncode == 1 and "No module named" in result.stderr:
        pytest.skip("smonitor CLI not runnable as a module in this environment")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("group", ["warnings", "exceptions"])
def test_check_2_every_code_emitted_has_a_template(group):
    """A code in the catalog and absent from CODES emits an empty message."""
    missing = [
        f"{name} -> {entry['code']}"
        for name, entry in CATALOG[group].items()
        if entry["code"] not in CODES
    ]
    assert not missing, f"catalog entries with no template: {missing}"


def test_check_2_no_template_is_unreachable():
    """The other direction: a template nothing emits is dead weight."""
    emitted = {
        entry["code"]
        for group in ("warnings", "exceptions")
        for entry in CATALOG[group].values()
    }
    assert set(CODES) == emitted


@pytest.mark.parametrize("code", sorted(CODES))
def test_check_3_every_code_renders_in_every_profile(code):
    """SMonitor 0.13 has no per-profile fallback, so a code that defines only
    one field renders empty everywhere else."""
    entry = CODES[code]
    for profile in PROFILES:
        assert any(
            entry.get(field)
            for field in (f"{profile}_message", "message", "user_message")
        ), f"{code} renders empty under the {profile} profile"


@pytest.mark.parametrize("cls", CATALOG_CLASSES, ids=lambda c: c.__name__)
def test_check_4_catalog_classes_survive_being_rebuilt(cls):
    """warnings.warn(text, category) and pytest-xdist rebuild from args alone.
    Test args idempotence, not pickle: pickle restores __dict__ afterwards and
    so comes out correct even for a class written the wrong way."""
    instance = cls(extra={"probe": "value"})
    assert type(instance)(*instance.args).args == instance.args


def test_check_5_no_class_assigns_a_name_the_base_owns():
    """A static check: `hint` raises on assignment, the other four cannot."""
    offenders = []
    for path in (
        PACKAGE_ROOT / "_private" / "smonitor" / "warnings.py",
        PACKAGE_ROOT / "_private" / "smonitor" / "exceptions.py",
    ):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            for statement in ast.walk(node):
                if not isinstance(statement, ast.Assign):
                    continue
                for target in statement.targets:
                    name = getattr(target, "attr", None) or getattr(target, "id", None)
                    if name in BASE_OWNED:
                        offenders.append(f"{path.name}:{node.name}.{name}")
    assert not offenders, f"assigns a base-owned name: {offenders}"


@pytest.mark.parametrize("cls", CATALOG_CLASSES, ids=lambda c: c.__name__)
def test_rendered_messages_have_no_unresolved_placeholders(cls):
    """Our own check. A template that names a field the call site never passes
    reaches the user as a literal '{pypi}', which reads as a bug in the tool.

    Every field the templates reference is supplied here, so anything left in
    braces is a field no call site could satisfy either.
    """
    entry = CODES[
        CATALOG["warnings" if cls in vars(warn_module).values() else "exceptions"][
            cls.catalog_key
        ]["code"]
    ]
    fields = {
        name: f"<{name}>"
        for template in entry.values()
        for name in _placeholders(template)
    }
    rendered = str(cls(extra=fields))
    assert "{" not in rendered and "}" not in rendered, rendered


def _placeholders(template: str) -> set[str]:
    return {
        field
        for _, field, _, _ in __import__("string").Formatter().parse(template)
        if field
    }


def test_the_bundle_exports_a_usable_diagnostic():
    """Smoke test: a real emission carries its code and its typed facts."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        bundle.warn(warn_module.SessionLoadWarning(extra={"path": "/tmp/probe.json"}))

    assert len(caught) == 1
    emitted = caught[0].message
    assert emitted.code == "ACKREDIT-W001"
    assert "/tmp/probe.json" in str(emitted)
    assert emitted.extra["path"] == "/tmp/probe.json"
    # META reaches the payload, so a user can be pointed at the right issue tracker.
    assert emitted.extra["issues"] == META["issues"]
