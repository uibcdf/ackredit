"""DOI display projection must never become bibliography identity (#121)."""

import hashlib
import json
from pathlib import Path

import pytest

import ackredit
from ackredit._private.smonitor.exceptions import AttributionConflictError
from ackredit.contrib.jupyter import CitationsHTML
from ackredit.formats._links import doi_link, doi_name

NAME = "10.5555/Original.Case(a)_v2"
FORMS = [
    NAME,
    f"doi:{NAME}",
    f"DOI: {NAME}",
    f"https://doi.org/{NAME}",
    f"http://doi.org/{NAME}",
    f"http://dx.doi.org/{NAME}",
    f"HTTPS://DX.DOI.ORG/{NAME}",
    f"  https://doi.org/{NAME}  ",
]


def test_receiving_receipt_retains_original_bytes_and_the_paired_projection():
    root = Path(__file__).resolve().parents[1]
    receipt = json.loads(
        (root / "devtools/receipts/doi_presentation_121_2026-10-06.json").read_text()
    )
    assert receipt["issue"] == "uibcdf/ackredit#121"
    assert receipt["candidate"]["before"] == receipt["candidate"]["after"]
    old, new = receipt["baseline"]["probe"], receipt["candidate"]["probe"]
    assert old["styles"] == new["styles"] and old["executables"] == new["executables"]
    assert (
        old["input_sha256"] == new["input_sha256"] == receipt["paired_input"]["sha256"]
    )
    for side in (receipt["baseline"], receipt["candidate"]):
        for export in side["exports"].values():
            assert (
                hashlib.sha256(export["text"].encode()).hexdigest() == export["sha256"]
            )
    assert (
        receipt["baseline"]["exports"]["references.bib"]
        == receipt["candidate"]["exports"]["references.bib"]
    )
    assert (
        "https://doi.org/<a"
        in receipt["baseline"]["exports"]["bibliography.html"]["text"]
    )
    assert (
        "https://doi.org/<a"
        not in receipt["candidate"]["exports"]["bibliography.html"]["text"]
    )
    source = ackredit.Attribution.from_dict(receipt["paired_input"]["payload"])
    assert hashlib.sha256(source.to_json().encode()).hexdigest() == new["input_sha256"]
    assert json.loads(source.report("csl-json")) == json.loads(
        receipt["candidate"]["exports"]["references.csl.json"]["text"]
    )
    policy = receipt["identity_policy"]
    assert policy["same_id_conflicting_originals"] == "ACKREDIT-E011"
    assert not policy["doi_display_projection_is_merge_key"]


def saved(item_id="original", doi=NAME, version="1.0", **fields):
    return ackredit.Attribution(
        dict(
            schema="ackredit.attribution@1",
            name=item_id,
            context={},
            items=[
                dict(
                    id=item_id,
                    type="software",
                    title="Original release",
                    doi=doi,
                    version=version,
                    **fields,
                )
            ],
            uses=[],
            usage_tree={},
        )
    )


@pytest.mark.parametrize("original", FORMS)
def test_supported_presentations_export_one_name_and_keep_originals(original):
    attribution = saved(doi=original)
    before = attribution.to_json()
    assert doi_name(original) == NAME
    assert doi_link(original) == f"https://doi.org/{NAME}"
    assert json.loads(attribution.report("csl-json"))[0]["DOI"] == NAME
    assert json.loads(attribution.report("json"))[0]["doi"] == original
    # BibTeX retains its existing original field and escaping boundary.
    expected_bibtex = original.replace("_", r"\_")
    assert f"doi = {{{expected_bibtex}}}" in attribution.report("bibtex")
    assert attribution.to_json() == before
    assert attribution.to_dict()["items"][0]["doi"] == original
    assert ackredit.get_used_items() == {}


@pytest.mark.parametrize("original", FORMS)
def test_markdown_workflow_and_notebook_links_use_one_resolver(original):
    attribution = saved(doi=original)
    expected = f"https://doi.org/{NAME}"
    for fmt in ("markdown", "workflow"):
        rendered = attribution.report(fmt)
        assert expected in rendered
        assert "doi.org/https://" not in rendered
        assert "doi.org/http://" not in rendered
        assert "doi.org/doi:" not in rendered.lower()
    html = CitationsHTML(
        {"original": []}, {"original": attribution.to_dict()["items"][0]}
    )._repr_html_()
    assert f"href='{expected}'" in html
    assert "doi.org/https://" not in html


@pytest.mark.parametrize(
    "original",
    [
        "https://doi.org/10.5555/escaped%2Fname",
        "https://doi.org/10.5555/name?download=1",
        "https://doi.org/10.5555/name#section",
        "https://doi.org.evil.example/10.5555/name",
        "https://doi.org:443/10.5555/name",
        "https://other.example/10.5555/name",
        "https://doi.org/abcde",
        "doi: https://doi.org/10.5555/name",
        "doi: unknown",
        "10.5555/",
        "not a DOI",
        1234,
    ],
)
def test_ambiguous_and_unknown_values_are_not_repaired_or_validated(original):
    attribution = saved(doi=original)
    assert doi_name(original) == original
    assert json.loads(attribution.report("csl-json"))[0]["DOI"] == original
    assert attribution.to_dict()["items"][0]["doi"] == original


def test_distinct_release_ids_and_conflicting_claims_stay_distinct():
    first = saved("release:1", NAME, "1.0", note="Original first claim")
    second = saved(
        "release:2", f"https://doi.org/{NAME}", "2.0", note="Original second claim"
    )
    originals = [first.to_dict(), second.to_dict()]
    bundle = ackredit.compose_attributions([first, second])
    records = json.loads(bundle.report("csl-json"))
    assert [item["id"] for item in records] == ["release:1", "release:2"]
    assert [item["version"] for item in records] == ["1.0", "2.0"]
    assert [item["DOI"] for item in records] == [NAME, NAME]
    assert [item["note"] for item in records] == [
        "Original first claim",
        "Original second claim",
    ]
    assert bundle.to_dict()["attributions"] == originals
    reread = ackredit.AttributionBundle.from_json(bundle.to_json())
    assert reread.report("csl-json") == bundle.report("csl-json")
    assert reread.to_dict()["attributions"] == originals
    assert ackredit.get_used_items() == {}


def test_same_id_different_doi_spelling_remains_an_original_record_conflict():
    first = saved("same", NAME)
    second = saved("same", f"https://doi.org/{NAME}")
    originals = [first.to_dict(), second.to_dict()]
    assert first.report("csl-json") == second.report("csl-json")
    with pytest.raises(AttributionConflictError) as caught:
        ackredit.compose_attributions([first, second])
    assert caught.value.code == "ACKREDIT-E011"
    assert [first.to_dict(), second.to_dict()] == originals
    assert ackredit.get_used_items() == {}


def test_equal_originals_share_by_id_but_equal_dois_under_different_ids_do_not():
    first = saved("first")
    identical = saved("first")
    distinct_id = saved("second")
    bundle = ackredit.compose_attributions([first, identical, distinct_id])
    records = json.loads(bundle.report("csl-json"))
    assert [item["id"] for item in records] == ["first", "second"]
    assert len(bundle.attributions) == 3
    assert bundle.to_dict()["attributions"] == [
        first.to_dict(),
        identical.to_dict(),
        distinct_id.to_dict(),
    ]
