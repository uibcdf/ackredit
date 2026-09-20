import json

from flowcite import register_item, report, track_item


def test_csl_json_export():
    register_item(
        id="molsysmt:2024",
        type="article",
        title="MolSysMT Paper",
        authors=["Diego", "Other Author"],
        year=2024,
        doi="10.1234/msm.2024",
        journal="Nature Molecular Systems",
    )
    track_item("molsysmt:2024")

    # Render CSL
    csl_str = report(format="csl-json")
    csl = json.loads(csl_str)

    assert isinstance(csl, list)
    item = csl[0]
    assert item["id"] == "molsysmt:2024"
    assert item["type"] == "article-journal"
    assert item["title"] == "MolSysMT Paper"
    assert item["DOI"] == "10.1234/msm.2024"
    assert item["container-title"] == "Nature Molecular Systems"
    assert item["issued"]["date-parts"][0][0] == 2024
    assert item["author"][0]["literal"] == "Diego"
