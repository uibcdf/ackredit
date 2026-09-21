"""DOI enrichment fills in what a user did not supply, so it must fill it in
from the right work.

The cache was keyed by `doi.replace("/", "_")`, and a DOI suffix may contain
either character, so two works shared one file. Unlike a network failure, a
poisoned cache entry keeps returning the wrong answer.
"""

import hashlib

import pytest

from ackredit.core.registry import _cache_name, _user_agent

COLLIDING = [
    ("10.1234/a_b", "10.1234/a/b"),
    ("10.5281/zenodo.1_2", "10.5281/zenodo.1/2"),
    ("10.1000/x_y_z", "10.1000/x/y/z"),
]


@pytest.mark.parametrize("first,second", COLLIDING)
def test_distinct_dois_never_share_a_cache_entry(first, second):
    """These pairs all mapped to one file under the previous naming."""
    assert first.replace("/", "_") == second.replace("/", "_")  # the old collision
    assert _cache_name(first) != _cache_name(second)


@pytest.mark.parametrize(
    "doi",
    [
        "10.5281/zenodo.1298752",
        "10.1234/a_b",
        "10.1038/s41586-024-00001-2",
        "10.1000/../../etc/passwd",
        "10.1000/with spaces and ünïcode",
    ],
)
def test_a_cache_name_is_a_single_safe_file_name(doi):
    name = _cache_name(doi)

    assert name
    assert "/" not in name and "\\" not in name
    assert ".." not in name
    # Distinct enough to identify the work it belongs to.
    assert hashlib.sha256(doi.encode()).hexdigest()[:16] in name


def test_the_same_doi_always_maps_to_the_same_entry():
    assert _cache_name("10.1234/a") == _cache_name("10.1234/a")


def test_the_user_agent_announces_the_running_version():
    """Crossref routes by user agent. This was pinned at 0.4.0 while the
    package moved on, announcing a version that does not exist."""
    import ackredit

    agent = _user_agent()

    assert ackredit.__version__ in agent
    assert "0.4.0" not in agent or ackredit.__version__ == "0.4.0"
    assert agent.startswith("Ackredit/")


def test_datacite_titles_are_read_from_the_field_the_schema_defines():
    """DataCite has `titles: [{title: ...}]` and no scalar `title`. The branch
    reading the latter was dead, which is why nobody noticed it."""
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "ackredit" / "core" / "registry.py"
    text = source.read_text(encoding="utf-8")

    assert 'dc_data.get("title")' not in text
    assert 'dc_data.get("titles", [])' in text
