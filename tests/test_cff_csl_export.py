"""A saved CFF reference must retain its meaning in a reference manager."""

import importlib
import json
import subprocess
import sys

import pytest

from ackredit.core.attribution import Attribution, get_attribution
from ackredit.core.cff import parse_cff
from ackredit.core.collector import get_used_items
from ackredit.core.hooks import InjectionsFinder
from ackredit.core.registry import Registry
from ackredit.core.session import current_session
from ackredit.formats.csl_json import render


def exported(fields):
    item = {"id": "fixture:reference", "title": "Original", **fields}
    return json.loads(render({item["id"]: []}, {item["id"]: item}))[0]


@pytest.mark.parametrize(
    "cff_type,csl_type",
    [
        ("book", "book"),
        ("edited-work", "book"),
        ("proceedings", "book"),
        ("manual", "report"),
        ("report", "report"),
        ("thesis", "thesis"),
        ("conference-paper", "paper-conference"),
        ("magazine-article", "article-magazine"),
        ("newspaper-article", "article-newspaper"),
        ("pamphlet", "pamphlet"),
        ("patent", "patent"),
        ("personal-communication", "personal_communication"),
        ("blog", "post-weblog"),
        ("map", "map"),
        ("unpublished", "manuscript"),
    ],
)
def test_original_cff_reference_kind_reaches_csl(cff_type, csl_type):
    data = parse_cff(
        f"title: Root\npreferred-citation:\n  type: {cff_type}\n  title: Original\n"
    )
    assert data["_cff_type"] == cff_type
    assert exported(data)["type"] == csl_type


@pytest.mark.parametrize("cff_type", ["generic", "historical-work", "unknown-kind"])
def test_unmapped_original_type_stays_in_saved_metadata(cff_type):
    data = parse_cff(
        f"title: Root\npreferred-citation:\n  type: {cff_type}\n  title: Original\n"
    )
    assert data["_cff_type"] == cff_type
    assert exported(data)["type"] == "document"
    assert not any(key.startswith("_") for key in exported(data))


@pytest.mark.parametrize(
    "fields,expected",
    [
        ({"date-published": "2024-02-29"}, {"date-parts": [[2024, 2, 29]]}),
        ({"date-released": "2023-10-05"}, {"date-parts": [[2023, 10, 5]]}),
        (
            {"date-published": "2024-02-29", "date-released": "2023-10-05"},
            {"date-parts": [[2024, 2, 29]]},
        ),
        ({"year": "2024", "month": "2"}, {"date-parts": [[2024, 2]]}),
        (
            {"year": "2024", "month": "2", "date-published": "2024-02-29"},
            {"date-parts": [[2024, 2, 29]]},
        ),
        (
            {"year": "2022", "date-published": "2024-02-29"},
            {"date-parts": [[2022]]},
        ),
        (
            {"year": "2024", "month": "3", "date-published": "2024-02-29"},
            {"date-parts": [[2024, 3]]},
        ),
        ({"date-published": "in press"}, {"literal": "in press"}),
        ({"date-published": "2023-02-29"}, {"literal": "2023-02-29"}),
        ({"date-published": "2024/2025"}, {"literal": "2024/2025"}),
        ({"year": "in press", "date-released": "2024-02-29"}, {"literal": "in press"}),
        ({"year": "2024/2025", "month": "2"}, {"literal": "2024/2025"}),
        ({"year": "2024", "month": "13"}, {"date-parts": [[2024]]}),
        ({"year": "2024", "month": "February"}, {"date-parts": [[2024]]}),
        ({"year": "2024"}, {"date-parts": [[2024]]}),
    ],
)
def test_date_precision_and_original_conflicts_are_not_invented(fields, expected):
    assert exported(fields)["issued"] == expected


def test_month_without_year_does_not_invent_a_date():
    assert "issued" not in exported({"month": "2"})


@pytest.mark.parametrize("value", ["2024-W09-4", "20240229", "2023-02-29"])
def test_non_cff_calendar_dates_stay_literal_through_parsing(value):
    data = parse_cff(
        "title: Root\npreferred-citation:\n  type: article\n  title: Paper\n"
        f"  date-published: '{value}'\n"
    )
    assert "year" not in data
    assert exported(data)["issued"] == {"literal": value}


def test_stated_literal_publication_date_does_not_borrow_release_year():
    data = parse_cff(
        "title: Root\npreferred-citation:\n  type: article\n  title: Paper\n"
        "  date-published: in press\n  date-released: 2024-02-29\n"
    )
    assert "year" not in data
    assert data["date-released"] == "2024-02-29"
    assert exported(data)["issued"] == {"literal": "in press"}


def test_cff_page_count_exports_separately_from_page_range():
    data = parse_cff(
        "title: Root\npreferred-citation:\n  type: article\n  title: Paper\n"
        "  pages: 15\n  start: 101\n  end: 115\n"
    )
    csl = exported(data)
    assert csl["number-of-pages"] == "15"
    assert csl["page"] == "101--115"


def test_bibtex_interpretation_keeps_its_existing_precedence():
    csl = exported({"type": "other", "_bibtex_type": "manual", "_cff_type": "manual"})
    assert csl["type"] == "book"


@pytest.mark.parametrize("cff_type,csl_type", [("book", "book"), ("data", "dataset")])
def test_discovered_reference_exports_in_a_fresh_offline_reader(
    cff_type, csl_type, tmp_path, monkeypatch, clean_registry
):
    name = "export_cff_fixture"
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "CITATION.cff").write_text(
        "cff-version: 1.2.0\nmessage: Please cite the preferred work.\n"
        "type: software\ntitle: Root software\nversion: 9.0.0\n"
        "authors:\n  - name: Root Team\npreferred-citation:\n"
        f"  type: {cff_type}\n  title: Original reference\n"
        "  authors:\n    - family-names: Ruiz\n      given-names: Ana\n"
        "  date-published: 2024-02-29\n  pages: 240\n"
        "  publisher:\n    name: Example Press\n  isbn: 978-0-00-000000-0\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    importlib.invalidate_caches()
    InjectionsFinder().find_spec(name, None)
    payload = get_attribution().to_json()
    saved = tmp_path / "original.json"
    saved.write_text(payload, encoding="utf-8")
    original = json.loads(payload)["items"][0]
    assert original["_cff_type"] == cff_type
    assert original["date-published"] == "2024-02-29"
    assert original["page-count"] == "240"
    assert "version" not in original
    monkeypatch.setattr(Registry, "items", {})
    current_session().clear()
    assert Attribution.from_json(payload).to_dict()["items"][0] == original
    assert not get_used_items()

    reader = tmp_path / "reader"
    reader.mkdir()
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import importlib.abc, json, pathlib, socket, sys, urllib.request\n"
            "class BlockProducer(importlib.abc.MetaPathFinder):\n"
            "    def find_spec(self, fullname, path=None, target=None):\n"
            "        if fullname == 'export_cff_fixture':\n"
            "            raise AssertionError('reader imported producer')\n"
            "sys.meta_path.insert(0, BlockProducer())\n"
            "def no_network(*args, **kwargs):\n"
            "    raise AssertionError('reader contacted network')\n"
            "urllib.request.urlopen = no_network\n"
            "socket.socket.connect = no_network\n"
            "socket.create_connection = no_network\n"
            "import ackredit\n"
            "payload = pathlib.Path(sys.argv[1]).read_text()\n"
            "result = ackredit.Attribution.from_json(payload)\n"
            "assert not ackredit.get_used_items()\n"
            "print(result.report('csl-json'))\n"
            "assert not ackredit.get_used_items()\n",
            str(saved),
        ],
        cwd=reader,
        capture_output=True,
        text=True,
        check=True,
    )
    csl = json.loads(result.stdout)[0]
    assert csl["type"] == csl_type
    assert csl["issued"] == {"date-parts": [[2024, 2, 29]]}
    assert csl["number-of-pages"] == "240"
    assert csl["publisher"] == "Example Press"
    assert csl["ISBN"] == "978-0-00-000000-0"
    assert csl["author"] == [{"family": "Ruiz", "given": "Ana"}]
    assert not any(key.startswith("_") for key in csl)
