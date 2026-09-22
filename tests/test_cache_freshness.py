"""A cached answer must be able to become wrong.

`enrich_item` cached a DOI's metadata and never looked at its age, so an answer
was kept for as long as the directory survived. For a published record that is
almost always right. For one that was `"in press"` when it was cached it is
wrong permanently: the year arrives, and Ackredit keeps reporting what it saw
first.

Staleness triggers a refresh and never a discard. A cache exists so a run
without a network still has its metadata, and expiring into nothing would take
from the user a citation they already had.
"""

import json
import os
import time
import urllib.request

import pytest

import ackredit
from ackredit.core.registry import _CACHE_MAX_AGE, Registry, _cache_name

DOI = "10.9999/freshness"


@pytest.fixture(autouse=True)
def cache(tmp_path, monkeypatch, clean_registry):
    monkeypatch.setattr(Registry, "_get_cache_dir", classmethod(lambda cls: tmp_path))
    return tmp_path


@pytest.fixture
def fetched(monkeypatch):
    """What the services would answer, and how often they were asked."""
    answers = {"count": 0, "title": "From the network"}

    def fetch(url, headers):
        answers["count"] += 1
        return {"message": {"title": [answers["title"]]}}

    monkeypatch.setattr("ackredit.core.registry._fetch", fetch)
    return answers


def write_cache(cache, title, age_seconds=0.0):
    path = cache / f"{_cache_name(DOI)}.json"
    path.write_text(json.dumps({"title": [title]}))
    when = time.time() - age_seconds
    os.utime(path, (when, when))
    return path


def enrich() -> dict:
    ackredit.register_item(id="x:1", type="article", doi=DOI)
    Registry.enrich_item("x:1")
    return Registry.items["x:1"]


# --- fresh, stale, absent -------------------------------------------------


def test_a_fresh_answer_is_used_without_asking(cache, fetched):
    write_cache(cache, "From the cache", age_seconds=60)
    assert enrich()["title"] == "From the cache"
    assert fetched["count"] == 0


def test_a_stale_answer_is_refreshed(cache, fetched):
    """The defect: this answer was kept for ever."""
    write_cache(cache, "From the cache", age_seconds=_CACHE_MAX_AGE + 60)
    assert enrich()["title"] == "From the network"
    assert fetched["count"] == 1


def test_no_answer_at_all_is_fetched(cache, fetched):
    assert enrich()["title"] == "From the network"
    assert fetched["count"] == 1


def test_a_refresh_replaces_what_the_cache_held(cache, fetched):
    path = write_cache(cache, "From the cache", age_seconds=_CACHE_MAX_AGE + 60)
    enrich()
    assert json.loads(path.read_text())["title"] == ["From the network"]


def test_a_fresh_answer_is_not_rewritten(cache, fetched):
    """Nothing was fetched, so nothing should be written back."""
    path = write_cache(cache, "From the cache", age_seconds=60)
    before = path.stat().st_mtime
    enrich()
    assert path.stat().st_mtime == before


# --- staleness refreshes, never discards ----------------------------------


def test_a_stale_answer_survives_a_refresh_that_fails(cache, monkeypatch):
    """Expiring into nothing would take from the user a citation they had."""

    def fetch(url, headers):
        raise OSError("no network")

    monkeypatch.setattr("ackredit.core.registry._fetch", fetch)
    write_cache(cache, "From the cache", age_seconds=_CACHE_MAX_AGE + 60)

    assert enrich()["title"] == "From the cache"


def test_nothing_is_reported_when_the_stale_answer_is_used(cache, monkeypatch, recwarn):
    """Nothing was lost, so there is nothing to report."""

    def fetch(url, headers):
        raise OSError("no network")

    monkeypatch.setattr("ackredit.core.registry._fetch", fetch)
    write_cache(cache, "From the cache", age_seconds=_CACHE_MAX_AGE + 60)
    enrich()

    assert not [w for w in recwarn if "could not be retrieved" in str(w.message)]


def test_a_failure_with_nothing_to_fall_back_on_is_reported(cache, monkeypatch):
    from ackredit._private.smonitor.warnings import MetadataFetchWarning

    def fetch(url, headers):
        raise OSError("no network")

    monkeypatch.setattr("ackredit.core.registry._fetch", fetch)
    with pytest.warns(MetadataFetchWarning):
        enrich()


# --- what was cached before this ------------------------------------------


def test_an_entry_written_before_this_is_aged_not_discarded(cache, fetched):
    """Its format is unchanged, because the age is the file's own."""
    write_cache(cache, "From an older Ackredit", age_seconds=60)
    assert enrich()["title"] == "From an older Ackredit"
    assert fetched["count"] == 0


def test_the_stored_format_is_still_what_the_service_answered(cache, fetched):
    enrich()
    stored = json.loads((cache / f"{_cache_name(DOI)}.json").read_text())
    assert stored == {"title": ["From the network"]}


def test_the_freshness_is_long_enough_to_spare_the_services():
    assert 7 * 24 * 3600 <= _CACHE_MAX_AGE <= 365 * 24 * 3600


def test_nothing_reaches_the_network_here(cache, monkeypatch):
    """The guard for the guards."""

    def forbidden(*arguments, **keywords):
        raise AssertionError("a test reached the network")

    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    write_cache(cache, "From the cache", age_seconds=60)
    assert enrich()["title"] == "From the cache"
