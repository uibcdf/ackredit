"""`dump` is the one function whose whole job is to put the report on disk.

Run end to end from a host library, it lost reports in three ways, all silent:

- `dump("citations.bib", formats=["bibtex", "markdown"])` wrote the BibTeX and
  discarded the Markdown. The code said so in a comment.
- `dump("refs.bib")` wrote *Markdown* into a file named `.bib`, because the
  default format list was filled in before the file name was ever read.
- `dump(directory, formats=["text", "provenance"])` wrote both to
  `ackredit_report.txt`, so the file held whichever came last.

That is the silent-data-loss class closed everywhere else in this library
(`uibcdf/ackredit#65`).
"""

import pytest

from ackredit._private.smonitor.exceptions import ManyFormatsOneFileError
from ackredit._private.smonitor.warnings import FormatExtensionWarning
from ackredit.core.collector import track_item
from ackredit.core.registry import register_item
from ackredit.core.report import dump, report


@pytest.fixture(autouse=True)
def _one_citation(clean_registry):
    register_item(id="paper:dump", type="article", title="Dumped Paper", year=2026)
    track_item("paper:dump", used_by="pkg.run")


# --- a file holds one report ------------------------------------------------


def test_several_formats_and_one_file_is_refused(tmp_path):
    target = tmp_path / "citations.bib"

    with pytest.raises(ManyFormatsOneFileError) as raised:
        dump(target, formats=["bibtex", "markdown"])

    assert raised.value.code == "ACKREDIT-E009"
    assert not target.exists(), "refusing means writing nothing, not the first one"


def test_the_refusal_is_also_a_value_error(tmp_path):
    """What a caller catching the ordinary exception for a bad value expects."""
    with pytest.raises(ValueError):
        dump(tmp_path / "citations.bib", formats=["bibtex", "markdown"])


# --- the name chooses when nothing else does --------------------------------


@pytest.mark.parametrize(
    "name,format",
    [
        ("refs.bib", "bibtex"),
        ("refs.md", "markdown"),
        ("refs.tex", "latex"),
        ("refs.json", "json"),
        # The longest extension wins: this is CSL-JSON, not JSON.
        ("refs.csl.json", "csl-json"),
        # Two formats share `.txt`; the table's own order picks plain text.
        ("refs.txt", "text"),
        ("REFS.BIB", "bibtex"),
    ],
)
def test_a_file_name_with_no_formats_chooses_the_format(
    tmp_path, recwarn, name, format
):
    target = tmp_path / name

    dump(target)

    assert target.read_text() == report(format=format)
    assert not [w for w in recwarn if isinstance(w.message, FormatExtensionWarning)]


def test_a_name_that_asks_for_nothing_is_markdown(tmp_path, recwarn):
    target = tmp_path / "citations.dat"

    dump(target)

    assert target.read_text() == report(format="markdown")
    assert not [w for w in recwarn if isinstance(w.message, FormatExtensionWarning)]


def test_an_empty_format_list_is_no_format_list(tmp_path):
    target = tmp_path / "refs.bib"
    dump(target, formats=[])
    assert target.read_text() == report(format="bibtex")


# --- an explicit request wins, and a contradicting name is said out loud -----


def test_a_format_the_name_contradicts_is_written_and_warned(tmp_path):
    target = tmp_path / "notes.md"

    with pytest.warns(FormatExtensionWarning, match="bibtex"):
        dump(target, formats=["bibtex"])

    assert target.read_text() == report(format="bibtex")


def test_a_format_the_name_agrees_with_is_not_warned(tmp_path, recwarn):
    dump(tmp_path / "notes.md", formats=["markdown"])
    assert not [w for w in recwarn if isinstance(w.message, FormatExtensionWarning)]


def test_an_alias_is_the_format_it_names(tmp_path, recwarn):
    """`csl` is `csl-json`, so `refs.csl.json` agrees with it."""
    dump(tmp_path / "refs.csl.json", formats=["csl"])
    assert not [w for w in recwarn if isinstance(w.message, FormatExtensionWarning)]


# --- a directory takes several, and none overwrites another ------------------


def test_formats_that_share_an_extension_each_get_a_file(tmp_path):
    dump(tmp_path, formats=["text", "provenance"])

    written = {path.name: path.read_text() for path in tmp_path.iterdir()}

    assert written == {
        "ackredit_report_text.txt": report(format="text"),
        "ackredit_report_provenance.txt": report(format="provenance"),
    }


def test_the_default_directory_names_are_unchanged(tmp_path):
    """The LaTeX report says `\\bibliography{ackredit_report}`, so the `.bib`
    must keep that name. Only a clash is renamed."""
    dump(tmp_path)

    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "ackredit_report.bib",
        "ackredit_report.md",
        "ackredit_report.tex",
        "ackredit_report.txt",
    ]
    assert (
        "\\bibliography{ackredit_report}"
        in (tmp_path / "ackredit_report.tex").read_text()
    )
