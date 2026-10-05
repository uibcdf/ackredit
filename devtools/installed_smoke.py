"""Qualify Ackredit's installed package and portable attribution outside a checkout."""

from __future__ import annotations

import argparse
import importlib
import importlib.metadata as metadata
import json
import os
import platform
import re
import sys
from pathlib import Path


def verify_citation(citation: dict, version: str):
    """Bind installed canonical releases to their own discovered bibliography."""
    assert citation and citation["title"] == "Ackredit" and citation["authors"], (
        citation
    )
    # Development wheels derive from a previous tag while CFF names the release
    # being prepared. Exact Conda/tagged release versions must agree instead.
    if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        assert str(citation.get("version")) == version, (citation, version)


def verify(*, expected_python: str | None = None, expected_version: str | None = None):
    """Refuse shadowed providers and exercise the installed result/workflow contract."""
    interpreter = f"{sys.version_info.major}.{sys.version_info.minor}"
    if expected_python is not None:
        assert interpreter == expected_python, (interpreter, expected_python)
    if sys.platform == "darwin":
        assert platform.machine() == "arm64", platform.machine()

    prefix = Path(sys.prefix).resolve()
    providers = {}
    for name in ("ackredit", "smonitor", "depdigest", "argdigest"):
        module = importlib.import_module(name)
        origin = Path(module.__file__).resolve()
        assert origin.is_relative_to(prefix) and "site-packages" in origin.parts, (
            name,
            origin,
            prefix,
        )
        providers[name] = {"version": metadata.version(name), "origin": str(origin)}

    import ackredit
    from ackredit.core.cff import find_and_parse_cff

    version = metadata.version("ackredit")
    assert ackredit.__version__ == version, (ackredit.__version__, version)
    if expected_version is not None:
        assert version == expected_version, (version, expected_version)
    citation = find_and_parse_cff(Path(ackredit.__file__).parent)
    verify_citation(citation, version)

    with ackredit.session("installed qualification"):
        ackredit.register_item(
            id="installed:software",
            type="software",
            title="Installed producer",
            authors=[{"literal": "Installed Qualification Consortium"}],
            version=version,
        )
        results = []
        for name in ("first", "reused"):
            with ackredit.capture(
                name, context={"producer_version": version}
            ) as result:
                ackredit.track_item(
                    "installed:software",
                    roles=["executed_software"],
                    context={"software": "ackredit", "software_version": version},
                )
            results.append(result.attribution)
        assert all(len(result.to_dict()["items"]) == 1 for result in results)
        assert len(ackredit.get_attribution().to_dict()["items"]) == 1
        saved = results[0].to_json()

    with ackredit.session("saved reader"):
        restored = ackredit.Attribution.from_json(saved)
        assert restored.to_json() == saved
        assert restored.to_dict()["items"][0]["version"] == version
        assert "author = {{Installed Qualification Consortium}}" in restored.report(
            format="bibtex"
        )
        assert ackredit.get_used_items() == {}

    return {
        "python": platform.python_version(),
        "providers": providers,
        "requires_python": metadata.metadata("ackredit")["Requires-Python"],
        "portable_attribution": "passed",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-python")
    parser.add_argument("--expected-version", default=os.environ.get("PKG_VERSION"))
    arguments = parser.parse_args()
    print(json.dumps(verify(**vars(arguments)), sort_keys=True))


if __name__ == "__main__":
    main()
