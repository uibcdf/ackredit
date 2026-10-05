"""Release gates bind self-citation to the candidate, before its tag exists."""

import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_self_citation_matches_committed_release_candidate():
    plan = tomllib.loads((ROOT / "devtools/conda-build/release_plan.toml").read_text())
    for relative in ("CITATION.cff", "ackredit/CITATION.cff"):
        citation = yaml.safe_load((ROOT / relative).read_text())
        assert str(citation["version"]) == plan["version"], relative


def test_installed_release_smoke_refuses_stale_self_citation():
    """The recipe/source CI must actually compare discovery with installed identity."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "installed_smoke", ROOT / "devtools/installed_smoke.py"
    )
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    import pytest

    smoke.verify_citation(
        {"title": "Ackredit", "authors": ["Consortium"], "version": "0.10.1"}, "0.10.1"
    )
    with pytest.raises(AssertionError):
        smoke.verify_citation(
            {"title": "Ackredit", "authors": ["Consortium"], "version": "0.9.0"},
            "0.10.1",
        )
