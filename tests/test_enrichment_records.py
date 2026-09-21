"""What comes back from Crossref and DataCite becomes a citation, so it must
survive the journey as itself.

Fetching and caching were guarded; applying the record was not.

Crossref escapes its text. It returns the Matplotlib paper's container title as
"Computing in Science &amp; Engineering", Ackredit stored that string, and the
LaTeX escaper then escaped the `&` of `&amp;`, so a bibliography printed
`\\&amp;`. A record with an empty title list raised IndexError out of
enrichment and stopped `enrich_all` where it stood. A creator with no name
became an author called "None".

These apply records through the cache, so they need no network.
"""

import json
import warnings

import pytest

import ackredit
from ackredit._private.smonitor.warnings import MetadataRecordWarning
from ackredit.core.registry import Registry, _cache_name


@pytest.fixture(autouse=True)
def cache(tmp_path, monkeypatch, clean_registry):
    """A cache of this test's own, and no network.

    The real cache is in the user's home, and a cached record that is empty is
    falsy, so enrichment falls through to Crossref for it. Closing that door
    keeps these tests hermetic and makes the fallback deterministic.
    """
    monkeypatch.setattr(Registry, "_get_cache_dir", classmethod(lambda cls: tmp_path))
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("no network in tests")),
    )
    return tmp_path


def enrich(cache, record, doi="10.9999/probe", **fields) -> dict:
    (cache / f"{_cache_name(doi)}.json").write_text(json.dumps(record))
    ackredit.register_item(id="x:1", type="article", doi=doi, **fields)
    Registry.enrich_item("x:1")
    return Registry.items["x:1"]


# --- what the network escapes ---------------------------------------------


def test_html_entities_do_not_become_characters_of_the_title(cache):
    item = enrich(cache, {"title": ["Tom &amp; Jerry &lt;i&gt;"]})
    assert item["title"] == "Tom & Jerry <i>"


def test_the_journal_is_unescaped_too(cache):
    """The measured case: `journal = {Computing in Science \\&amp; Engineering}`."""
    item = enrich(
        cache, {"container-title": ["Computing in Science &amp; Engineering"]}
    )
    assert item["journal"] == "Computing in Science & Engineering"

    ackredit.track_item("x:1")
    rendered = ackredit.report(format="bibtex")
    assert r"journal = {Computing in Science \& Engineering}" in rendered
    assert "amp;" not in rendered


def test_an_author_name_is_unescaped(cache):
    item = enrich(cache, {"author": [{"family": "O&#39;Neill", "given": "Ann"}]})
    assert item["authors"] == ["O'Neill, Ann"]


def test_the_cache_keeps_what_the_api_answered(cache):
    """Unescaping on read, not on write, so a cache written before this is
    repaired and stays a faithful copy of the answer."""
    record = {"title": ["Tom &amp; Jerry"]}
    enrich(cache, record)
    (written,) = list(cache.iterdir())
    assert json.loads(written.read_text()) == record


# --- records that used to end the run -------------------------------------


def test_a_record_with_no_title_leaves_the_title_unset(cache):
    """It raised IndexError: the default is used when the key is absent, and an
    empty list is not absent."""
    item = enrich(cache, {"title": [], "author": []})
    assert "title" not in item


def test_enrich_all_does_not_stop_at_a_bad_record(cache):
    """The blast radius: every item after the bad one was left unenriched."""
    (cache / f"{_cache_name('10.9999/bad')}.json").write_text(json.dumps({"title": []}))
    (cache / f"{_cache_name('10.9999/good')}.json").write_text(
        json.dumps({"title": ["A Real Title"]})
    )
    ackredit.register_item(id="bad:1", type="article", doi="10.9999/bad")
    ackredit.register_item(id="good:1", type="article", doi="10.9999/good")

    ackredit.enrich_all()

    assert Registry.items["good:1"]["title"] == "A Real Title"


@pytest.mark.parametrize(
    "record",
    [
        {"title": "not a list"},
        {"issued": "not a mapping"},
        {"issued": {"date-parts": []}},
        {"issued": {"date-parts": [[]]}},
        {"container-title": None},
        {"author": "not a list"},
        {},
    ],
    ids=lambda record: str(record)[:28],
)
def test_no_shape_of_record_costs_the_caller_their_run(cache, record):
    # Some of these are reported, which is the point; the assertion is that
    # none of them raises.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        item = enrich(cache, record, doi=f"10.9999/{abs(hash(str(record)))}")
    assert item["id"] == "x:1"


def test_a_record_that_cannot_be_read_is_reported(cache):
    """Never swallowed: a malformed record is data, and the caller is told."""
    with pytest.warns(MetadataRecordWarning):
        enrich(cache, {"issued": "not a mapping"})


# --- creators who name nobody ---------------------------------------------


def test_a_creator_with_no_name_is_not_an_author(cache):
    """DataCite yields family=None for a creator with neither familyName nor
    name, and that became `author = {None}`."""
    item = enrich(
        cache,
        {"author": [{"family": None, "given": ""}, {"family": "Real", "given": "A"}]},
    )
    assert item["authors"] == ["Real, A"]


def test_an_empty_crossref_creator_is_not_an_author(cache):
    item = enrich(cache, {"author": [{}, {"family": "Real", "given": "A"}]})
    assert item["authors"] == ["Real, A"]


def test_nothing_invented_reaches_a_bibliography(cache):
    enrich(cache, {"title": ["T"], "author": [{"family": None, "given": None}]})
    ackredit.track_item("x:1")
    rendered = ackredit.report(format="bibtex")

    assert "None" not in rendered
    assert "author = {}" not in rendered


def test_a_family_only_creator_keeps_its_name(cache):
    """An organisation has a family and no given name, and is still an author."""
    item = enrich(cache, {"author": [{"family": "SciPy 1.0 Contributors"}]})
    assert item["authors"] == ["SciPy 1.0 Contributors"]


# --- what enrichment must not overwrite -----------------------------------


def test_what_the_host_registered_wins(cache):
    item = enrich(cache, {"title": ["From the network"]}, title="From the host")
    assert item["title"] == "From the host"
