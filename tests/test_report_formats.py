"""Asking for a format Ackredit does not know must not produce a different one.

A typo in "bibtex" used to return plain text, and `dump` wrote it to a `.txt`
file the caller never asked for. The failure was silent and the output was
plausible: a plain-text citation list looks like a report, so nothing prompted
anyone to check until a `.bib` reached a TeX engine.
"""

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import UnknownFormatError
from ackredit.core.collector import Collector
from ackredit.core.registry import Registry
from ackredit.core.report import _ALIASES, _RENDERERS


@pytest.fixture(autouse=True)
def _one_item():
    Collector.used_items.clear()
    Collector.used_targets.clear()
    Collector.usage_tree.clear()
    Registry.items.clear()
    ackredit.register_item(id="x:1", title="A Title", authors=["Ana Ruiz"], year=2024)
    ackredit.track_item("x:1")
    yield


@pytest.mark.parametrize(
    "name",
    [
        "bibtext",  # a typo in a real format
        "BibTeX",  # the spelling the format's own documentation uses
        "csl_json",  # underscore where the name has a hyphen
        "yaml",  # a format that does not exist
        "",
    ],
)
def test_an_unknown_format_is_refused(name):
    with pytest.raises(UnknownFormatError) as raised:
        ackredit.report(format=name)

    assert raised.value.code == "ACKREDIT-E004"
    assert name in str(raised.value) or not name
    # The message must say what to use instead, not only what was wrong.
    assert "bibtex" in str(raised.value)


def test_it_is_also_a_value_error():
    """Callers catching the ordinary exception for a bad argument keep working."""
    with pytest.raises(ValueError):
        ackredit.report(format="nope")


@pytest.mark.parametrize("name", sorted(_RENDERERS))
def test_every_advertised_format_renders(name):
    """available_formats() must not promise something report() cannot do."""
    assert isinstance(ackredit.report(format=name), str)


def test_available_formats_is_the_whole_truth():
    assert ackredit.available_formats() == sorted(_RENDERERS)
    assert "csl" not in ackredit.available_formats()  # an alias, not a name


@pytest.mark.parametrize("alias,canonical", sorted(_ALIASES.items()))
def test_a_published_alias_still_resolves(alias, canonical):
    assert ackredit.report(format=alias) == ackredit.report(format=canonical)


def test_dump_refuses_an_unknown_format_instead_of_writing_txt(tmp_path):
    """The typo used to pick the fallback extension too, so the caller received
    a file named for neither the format they asked for nor the one they got."""
    with pytest.raises(UnknownFormatError):
        ackredit.dump(tmp_path, formats=["bibtext"])


@pytest.mark.parametrize("name", sorted(_RENDERERS))
def test_dump_writes_one_file_per_advertised_format(tmp_path, name):
    ackredit.dump(tmp_path / name, formats=[name])

    written = sorted(p.name for p in (tmp_path / name).iterdir())
    assert len(written) == 1, written
    assert written[0].startswith("ackredit_report.")


def test_the_renderer_and_the_extension_cannot_disagree():
    """They were two tables listing slightly different formats."""
    for name, (render, extension) in _RENDERERS.items():
        assert callable(render), name
        assert extension and not extension.startswith("."), name
