"""Ackredit fetches from services it shares with everyone else.

It runs on many machines at once, so how it asks matters. It asked as fast as it
could: `enrich_all` issued one request per item with nothing between them, and
against a stand-in that answers instantly, 60 left in 11 ms — 5 326 per second
against the 5 Crossref advertises on every response.

It also identified no contact, which put it in the public pool at half the
allowance a contact earns, and a 429 was reported as `ACKREDIT-W006`, whose
message says to check network access. The network was fine; we asked too fast.

Nothing here reaches the network. The rates are the ones the services state.
"""

import io
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from ackredit.core import registry
from ackredit.core.registry import (
    _DEFAULT_RATE_INTERVAL,
    _DEFAULT_RATE_LIMIT,
    _fetch,
    _user_agent,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _fresh_throttle(monkeypatch):
    monkeypatch.delenv(registry.CONTACT_VARIABLE, raising=False)
    monkeypatch.setitem(registry._throttle, "limit", _DEFAULT_RATE_LIMIT)
    monkeypatch.setitem(registry._throttle, "interval", _DEFAULT_RATE_INTERVAL)
    monkeypatch.setitem(registry._throttle, "last", 0.0)


class Answer(io.BytesIO):
    def __init__(self, headers=None):
        super().__init__(json.dumps({"message": {"title": ["T"]}}).encode())
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *arguments):
        return False


# --- who we say we are ----------------------------------------------------


def test_no_contact_is_sent_unless_one_is_set():
    agent = _user_agent()
    assert "mailto" not in agent
    assert "@" not in agent


def test_a_contact_that_is_set_reaches_the_user_agent(monkeypatch):
    monkeypatch.setenv(registry.CONTACT_VARIABLE, "someone@example.org")
    assert _user_agent().endswith("mailto:someone@example.org")


def test_an_empty_contact_is_no_contact(monkeypatch):
    monkeypatch.setenv(registry.CONTACT_VARIABLE, "   ")
    assert "mailto" not in _user_agent()


def test_no_address_is_baked_into_the_source():
    """A maintainer's address would attribute every user's requests to one
    person and misuse the pool it earns."""
    source = (ROOT / "ackredit/core/registry.py").read_text(encoding="utf-8")
    assert "mailto:{contact}" in source, "the only address is the one a user sets"
    assert "@gmail" not in source and "@uibcdf" not in source


# --- how fast we ask ------------------------------------------------------


def _request_times(monkeypatch, count, headers=None):
    stamps = []

    def urlopen(request, timeout=None):
        stamps.append(time.monotonic())
        return Answer(headers)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    for _ in range(count):
        _fetch("https://example.org/works/x", {"User-Agent": "test"})
    return stamps


def test_requests_are_spaced_by_the_advertised_rate(monkeypatch):
    """A high rate keeps the test quick; what is under test is the spacing."""
    monkeypatch.setitem(registry._throttle, "limit", 100)
    stamps = _request_times(monkeypatch, 8)

    gaps = [second - first for first, second in zip(stamps, stamps[1:])]
    assert min(gaps) >= 0.009, f"requests were {min(gaps) * 1000:.1f} ms apart"


def test_no_more_than_the_limit_in_any_advertised_window(monkeypatch):
    # More requests than the window allows, or the assertion cannot fail: the
    # first version of this asked for 20 against a limit of 50.
    monkeypatch.setitem(registry._throttle, "limit", 10)
    monkeypatch.setitem(registry._throttle, "interval", 0.1)
    stamps = _request_times(monkeypatch, 25)

    worst = max(
        sum(1 for at in stamps if start <= at < start + 0.1) for start in stamps
    )
    assert worst <= 10, f"{worst} requests in a window that allows 10"


def test_the_default_is_what_an_unidentified_client_is_allowed():
    """Until a response states otherwise, assume the public pool."""
    assert (_DEFAULT_RATE_LIMIT, _DEFAULT_RATE_INTERVAL) == (5, 1.0)


def test_the_rate_a_service_states_is_adopted(monkeypatch):
    _request_times(
        monkeypatch,
        1,
        headers={"x-rate-limit-limit": "50", "x-rate-limit-interval": "1s"},
    )
    assert registry._throttle["limit"] == 50
    assert registry._throttle["interval"] == 1.0


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"x-rate-limit-limit": "not a number"},
        {"x-rate-limit-limit": "0", "x-rate-limit-interval": "1s"},
        {"x-rate-limit-limit": "5", "x-rate-limit-interval": "soon"},
    ],
    ids=["absent", "unparseable", "zero", "no-unit"],
)
def test_a_header_that_makes_no_sense_leaves_the_rate_alone(monkeypatch, headers):
    _request_times(monkeypatch, 1, headers=headers)
    assert registry._throttle["limit"] >= 1
    assert registry._throttle["interval"] > 0


# --- being asked to slow down ---------------------------------------------


def test_a_429_is_tried_once_more(monkeypatch):
    monkeypatch.setitem(registry._throttle, "limit", 100)
    monkeypatch.setitem(registry._throttle, "interval", 0.01)
    attempts = []

    def urlopen(request, timeout=None):
        attempts.append(1)
        if len(attempts) == 1:
            raise urllib.error.HTTPError(
                "u", 429, "Too Many Requests", {"x-rate-limit-limit": "5"}, None
            )
        return Answer()

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    assert _fetch("https://example.org/x", {})["message"]["title"] == ["T"]
    assert len(attempts) == 2


def test_a_429_that_persists_is_reported(monkeypatch):
    monkeypatch.setitem(registry._throttle, "limit", 100)
    monkeypatch.setitem(registry._throttle, "interval", 0.01)
    attempts = []

    def urlopen(request, timeout=None):
        attempts.append(1)
        raise urllib.error.HTTPError("u", 429, "Too Many Requests", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    with pytest.raises(urllib.error.HTTPError):
        _fetch("https://example.org/x", {})
    assert len(attempts) == 2, "tried once more, and only once"


def test_another_error_is_not_retried(monkeypatch):
    attempts = []

    def urlopen(request, timeout=None):
        attempts.append(1)
        raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    with pytest.raises(urllib.error.HTTPError):
        _fetch("https://example.org/x", {})
    assert len(attempts) == 1
