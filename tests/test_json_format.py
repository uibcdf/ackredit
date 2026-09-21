"""The machine-readable report must carry what identifies a citation.

`json` is advertised by `available_formats()`, and it emitted six fixed keys. It
kept `note`, usually null, and dropped the DOI, the authors, the journal and the
URL — everything a parser would ask for this format to get. The call succeeded
and the output was valid JSON, so nothing told the caller.
"""

import datetime
import json

import pytest

import ackredit
from ackredit.core.registry import Registry
from ackredit.core.session import current_session

FULL_ITEM = {
    "id": "a:1",
    "type": "article",
    "title": "Array programming with NumPy",
    "authors": ["Harris, Charles R.", "Millman, K. Jarrod"],
    "year": 2020,
    "doi": "10.1038/s41586-020-2649-2",
    "journal": "Nature",
    "url": "https://doi.org/10.1038/s41586-020-2649-2",
    "note": "Used for the array backend.",
    "version": "1.26.0",
}


@pytest.fixture(autouse=True)
def _clean():
    current_session().clear()
    Registry.items.clear()
    yield
    current_session().clear()
    Registry.items.clear()


def report_for(**item) -> dict:
    ackredit.register_item(**item)
    ackredit.track_item(item["id"], used_by="run")
    (record,) = json.loads(ackredit.report(format="json"))
    return record


@pytest.mark.parametrize("field", sorted(FULL_ITEM))
def test_every_registered_field_survives(field):
    """The defect: four of these were dropped, the DOI among them."""
    record = report_for(**FULL_ITEM)
    assert field in record, f"the json report dropped {field!r}"
    assert record[field] == FULL_ITEM[field]


def test_provenance_is_carried():
    assert report_for(**FULL_ITEM)["used_by"] == ["run"]


def test_ackredits_own_bookkeeping_stays_out():
    """`_source` tells the LaTeX escaper where a field came from. It is not data."""
    record = report_for(**FULL_ITEM, _source="bibtex")
    assert not [key for key in record if key.startswith("_")]


def test_the_registry_key_is_the_identity():
    ackredit.register_item(id="a:1", title="T")
    ackredit.track_item("a:1", used_by="run")
    (record,) = json.loads(ackredit.report(format="json"))
    assert record["id"] == "a:1"


def test_an_item_that_was_never_registered_is_still_reported():
    ackredit.track_item("unknown:1", used_by="run")
    (record,) = json.loads(ackredit.report(format="json"))
    assert record["id"] == "unknown:1"
    assert record["used_by"] == ["run"]


def test_a_value_that_is_not_json_does_not_cost_the_report():
    """A date reaches register_item easily. Losing the whole report over one
    field is worse than rendering it as the text it prints as."""
    record = report_for(id="a:1", title="T", released=datetime.date(2026, 9, 21))
    assert record["released"] == "2026-09-21"


def test_the_report_is_valid_json_for_the_data_ackredit_ships():
    from ackredit.core.standard_injections import STANDARD_INJECTIONS

    for items in STANDARD_INJECTIONS.values():
        for item in items:
            ackredit.register_item(**item)
            ackredit.track_item(item["id"], used_by="run")

    records = json.loads(ackredit.report(format="json"))
    assert len(records) == sum(len(v) for v in STANDARD_INJECTIONS.values())
    for record in records:
        assert record["authors"], f"{record['id']} reaches a parser with no authors"
        assert record.get("doi") or record.get("url")
