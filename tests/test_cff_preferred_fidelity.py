"""The preferred work is its own reference, not software with a paper title."""

import importlib
import json

import pytest

from ackredit.core.attribution import Attribution, get_attribution
from ackredit.core.cff import parse_cff
from ackredit.core.collector import get_used_items
from ackredit.core.hooks import InjectionsFinder
from ackredit.core.registry import Registry
from ackredit.core.session import current_session

ROOT = """\
cff-version: 1.2.0
message: Please cite the preferred work.
type: software
title: Example Software
version: 9.0.0
doi: 10.1234/software
url: https://example.org/software
date-released: 2026-10-01
authors:
  - name: Software Team
"""
ARTICLE = """\
preferred-citation:
  type: article
  title: Example Methods
  authors:
    - family-names: Ruiz
      given-names: Ana
  year: 2024
  journal: Journal of Methods
  volume: 12
  issue: 3
  start: 101
  end: 115
"""


@pytest.fixture(autouse=True)
def _clean(clean_registry):
    yield


@pytest.fixture
def discovered(tmp_path, monkeypatch):
    def discover(content=ROOT + ARTICLE, shipped=()):
        name = "preferred_cff_fixture"
        package = tmp_path / name
        package.mkdir()
        (package / "__init__.py").write_text("", encoding="utf-8")
        (package / "CITATION.cff").write_text(content, encoding="utf-8")
        monkeypatch.syspath_prepend(str(tmp_path))
        importlib.invalidate_caches()
        from ackredit.core import standard_injections

        monkeypatch.setitem(standard_injections.STANDARD_INJECTIONS, name, shipped)
        InjectionsFinder().find_spec(name, None)
        used = get_used_items()
        assert len(used) == 1
        item_id = next(iter(used))
        assert used[item_id] == [name]
        return Registry.items[item_id]

    return discover


def test_typed_preferred_work_does_not_inherit_software_identity():
    data = parse_cff(ROOT + ARTICLE)
    assert data["type"] == "article"
    assert data["authors"] == ["Ruiz, Ana"]
    assert not {"version", "doi", "url", "date-released"} & data.keys()


def test_preferred_article_without_authors_does_not_invent_software_authorship():
    data = parse_cff(ROOT + "preferred-citation:\n  type: article\n  title: Paper\n")
    assert "authors" not in data


def test_discovered_preferred_article_retains_its_own_bibliography(discovered):
    item = discovered()
    assert item["type"] == "article"
    assert item["year"] == "2024"
    assert item["journal"] == "Journal of Methods"
    assert item["volume"] == "12"
    assert item["number"] == "3"
    assert item["pages"] == "101--115"
    assert not {"version", "doi", "url", "date-released"} & item.keys()


def test_preferred_selection_does_not_replace_or_credit_shipped_works(discovered):
    software = {
        "id": "shipped:software",
        "type": "software",
        "title": "Old software",
        "doi": "10.1234/old-software",
    }
    paper = {"id": "shipped:paper", "type": "article", "title": "Old paper"}
    Registry.register_item(**software)
    item = discovered(shipped=[software, paper])
    assert item["id"] == "discovered:preferred_cff_fixture:preferred"
    assert Registry.items[software["id"]] == software
    assert "shipped:paper" not in Registry.items


def test_detached_preferred_article_exports_to_reference_manager(
    discovered, monkeypatch
):
    item = discovered()
    saved = get_attribution().to_json()
    monkeypatch.setattr(Registry, "items", {})
    current_session().clear()
    detached = Attribution.from_json(saved)
    csl = json.loads(detached.report("csl-json"))[0]
    assert csl == {
        "id": item["id"],
        "type": "article-journal",
        "title": "Example Methods",
        "author": [{"family": "Ruiz", "given": "Ana"}],
        "issued": {"date-parts": [[2024]]},
        "container-title": "Journal of Methods",
        "volume": "12",
        "issue": "3",
        "page": "101--115",
    }
    workflow = detached.report("workflow")
    for text in ("Example Methods", "Journal of Methods", "2024", "101--115"):
        assert text in workflow
    assert "9.0.0" not in workflow
    assert "10.1234/software" not in workflow
    assert not get_used_items()  # The detached reader records no execution.


@pytest.mark.parametrize(
    "bounds,expected",
    [("start: e101\n  end: e115", "e101--e115"), ("start: e101", "e101")],
)
def test_cff_page_bounds_are_not_confused_with_page_counts(bounds, expected):
    data = parse_cff(
        ROOT
        + f"preferred-citation:\n  type: article\n  title: Paper\n  {bounds}\n  pages: 15\n"
    )
    assert data["pages"] == expected
    assert data["page-count"] == "15"


def test_page_count_without_bounds_is_not_a_page_range():
    data = parse_cff(
        ROOT + "preferred-citation:\n  type: article\n  title: Paper\n  pages: 15\n"
    )
    assert "pages" not in data
    assert data["page-count"] == "15"


def test_lone_end_page_does_not_invent_a_beginning_page():
    data = parse_cff(
        ROOT + "preferred-citation:\n  type: article\n  title: Paper\n  end: e115\n"
    )
    assert "pages" not in data
    assert data["end-page"] == "e115"


def test_preferred_software_is_a_distinct_release_with_its_own_missing_fields(
    discovered,
):
    item = discovered(
        ROOT
        + "preferred-citation:\n  type: software\n  title: Another Release\n  version: 1.0.0\n"
    )
    assert item["type"] == "software"
    assert item["version"] == "1.0.0"
    assert not {"authors", "doi", "url", "year"} & item.keys()


def test_unknown_work_kind_is_retained_without_claiming_it_is_software(discovered):
    item = discovered(
        ROOT + "preferred-citation:\n  type: historical-work\n  title: Original\n"
    )
    assert item["type"] == "other"
    assert item["_cff_type"] == "historical-work"


def test_explicit_year_is_not_replaced_by_a_release_date():
    data = parse_cff(ROOT + ARTICLE + "  date-released: 2021-02-03\n")
    assert data["year"] == "2024"


@pytest.mark.parametrize("date_field", ["date-released", "date-published"])
def test_publication_year_is_derived_only_from_the_selected_work(date_field):
    data = parse_cff(
        ROOT
        + f"preferred-citation:\n  type: article\n  title: Paper\n  {date_field}: 2021-02-03\n"
    )
    assert data["year"] == "2021"
    assert data[date_field] == "2021-02-03"


def test_preferred_work_uses_its_own_doi_identifier_and_editors(discovered):
    item = discovered(
        ROOT
        + ARTICLE
        + """\
  identifiers:
    - type: doi
      value: 10.1234/paper
  editors:
    - name: Methods Editorial Team
  publisher:
    name: Example Press
"""
    )
    assert item["doi"] == "10.1234/paper"
    assert item["editors"] == ["Methods Editorial Team"]
    assert item["publisher"] == "Example Press"


def test_root_dataset_keeps_its_type_and_does_not_borrow_software_id(discovered):
    item = discovered(
        ROOT.replace("type: software", "type: dataset"),
        shipped=[{"id": "shipped:software", "type": "software", "title": "Wrong"}],
    )
    assert item["type"] == "dataset"
    assert item["id"] == "discovered:preferred_cff_fixture"
    assert item["year"] == "2026"


def test_reference_list_does_not_imply_that_every_work_was_used(discovered):
    item = discovered(
        ROOT
        + ARTICLE
        + """\
references:
  - type: article
    title: A listed but unobserved dependency
    authors:
      - name: Another Team
"""
    )
    assert item["title"] == "Example Methods"


def test_manual_injection_still_wins_over_preferred_work(discovered):
    Registry.register_item(id="manual:work", type="article", title="Host choice")
    Registry.add_injection("preferred_cff_fixture", ["manual:work"])
    assert discovered()["id"] == "manual:work"
