"""The reminder is read by people and by logs, and must suit both.

It wrote ANSI colour to stderr unconditionally, so every redirected log, batch
job and CI record received `^[[94m` literally:

    ^[[94mℹ️  Ackredit: Your analysis utilized 1 components requiring citation.^[[0m

It also said "1 components", and described a citation report in the vocabulary
of an inventory. It was the last ANSI sequence in the package.
"""

import subprocess
import sys

import pytest

from ackredit.core.hooks import _is_a_terminal

RUN = """
import ackredit
ackredit.enable_auto_reminder()
{items}
"""

ONE = 'ackredit.register_item(id="a:1", title="A"); ackredit.track_item("a:1")'
THREE = "\n".join(
    f'ackredit.register_item(id="a:{n}", title="A"); ackredit.track_item("a:{n}")'
    for n in range(1, 4)
)


def run(items: str) -> str:
    result = subprocess.run(
        [sys.executable, "-c", RUN.format(items=items)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stderr


def test_a_redirected_stream_receives_no_escape_sequences():
    """The defect. `capture_output` is a pipe, which is not a terminal."""
    output = run(ONE)
    assert "\033" not in output
    assert "[94m" not in output
    assert "[0m" not in output


def test_one_work_is_described_in_the_singular():
    output = run(ONE)
    assert "1 work that asks to be cited" in output
    assert "1 works" not in output


def test_several_works_are_described_in_the_plural():
    assert "3 works that ask to be cited" in run(THREE)


def test_the_reminder_says_where_to_look():
    output = run(ONE)
    assert "ackredit.report()" in output
    assert "ackredit.summary()" in output


def test_nothing_is_said_when_nothing_was_tracked():
    assert run("") == ""


@pytest.mark.parametrize(
    "stream,expected",
    [
        (type("Tty", (), {"isatty": lambda self: True})(), True),
        (type("Pipe", (), {"isatty": lambda self: False})(), False),
        (type("Mute", (), {})(), False),
        (
            type(
                "Closed",
                (),
                {"isatty": lambda self: (_ for _ in ()).throw(ValueError("closed"))},
            )(),
            False,
        ),
    ],
    ids=["terminal", "pipe", "no-isatty", "closed"],
)
def test_a_stream_that_cannot_say_is_not_a_terminal(stream, expected):
    """A replaced stderr may have no `isatty`, and a closed one raises."""
    assert _is_a_terminal(stream) is expected
