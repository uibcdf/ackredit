"""What Ackredit switches on, it must be able to switch off.

`enable_import_hooks` inserts a finder into `sys.meta_path` and
`enable_auto_reminder` registers a function with `atexit`. Both are
process-wide, and neither could be undone: a notebook user who called one to try
it had changed the interpreter for as long as it lived.

The cost was measured before it was fixed. `tests/test_hooks.py` had to reach
into `sys.meta_path` and put it back by hand, because a finder left installed
made every later `find_spec` in the suite run discovery and emit diagnostics for
modules no test chose — six warnings on a green suite.
"""

import subprocess
import sys

import pytest

import ackredit
from ackredit.core import hooks


@pytest.fixture(autouse=True)
def _restore_the_process():
    original = list(sys.meta_path)
    enabled = hooks._IMPORT_HOOKS_ENABLED
    reminder = hooks._REMINDER_ENABLED
    yield
    ackredit.disable_auto_reminder()
    sys.meta_path[:] = original
    hooks._IMPORT_HOOKS_ENABLED = enabled
    hooks._REMINDER_ENABLED = reminder


def installed() -> int:
    return sum(isinstance(finder, hooks.InjectionsFinder) for finder in sys.meta_path)


# --- the import hooks -----------------------------------------------------


def test_disabling_leaves_sys_meta_path_as_it_was():
    before = list(sys.meta_path)
    ackredit.enable_import_hooks()
    assert installed() == 1

    ackredit.disable_import_hooks()
    assert installed() == 0
    assert sys.meta_path == before


def test_every_finder_goes_not_just_the_first():
    """However many were inserted, the process is left clean."""
    sys.meta_path.insert(0, hooks.InjectionsFinder())
    ackredit.enable_import_hooks()
    sys.meta_path.insert(0, hooks.InjectionsFinder())
    assert installed() >= 2

    ackredit.disable_import_hooks()
    assert installed() == 0


def test_disabling_what_was_never_enabled_does_nothing():
    before = list(sys.meta_path)
    ackredit.disable_import_hooks()
    ackredit.disable_import_hooks()
    assert sys.meta_path == before


def test_enabling_again_after_disabling_works():
    """`enable` is guarded by a flag, which `disable` has to clear or the
    second enable silently does nothing."""
    ackredit.enable_import_hooks()
    ackredit.disable_import_hooks()
    ackredit.enable_import_hooks()
    assert installed() == 1


# --- the exit reminder ----------------------------------------------------

RUN = """
import ackredit
{setup}
ackredit.register_item(id="a:1", title="A Work")
ackredit.track_item("a:1")
"""


def run(setup: str) -> str:
    """Run a real interpreter to exit, which is when the reminder happens."""
    result = subprocess.run(
        [sys.executable, "-c", RUN.format(setup=setup)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stderr


def test_the_reminder_arrives_at_exit_when_enabled():
    assert "asks to be cited" in run("ackredit.enable_auto_reminder()")


def test_disabling_takes_the_reminder_away():
    output = run("ackredit.enable_auto_reminder()\nackredit.disable_auto_reminder()")
    assert "asks to be cited" not in output
    assert output == ""


def test_nothing_is_said_when_it_was_never_enabled():
    assert run("") == ""


def test_disabling_twice_and_without_enabling_is_quiet():
    assert (
        run("ackredit.disable_auto_reminder()\nackredit.disable_auto_reminder()") == ""
    )


def test_enabling_again_after_disabling_restores_it():
    output = run(
        "ackredit.enable_auto_reminder()\n"
        "ackredit.disable_auto_reminder()\n"
        "ackredit.enable_auto_reminder()"
    )
    assert "asks to be cited" in output
