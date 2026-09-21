"""DummyPipeline — a host library that depends on another host library.

This is the case one example cannot show. DummyPipeline calls DummySolver, both
integrate Ackredit, and neither knows what the other cites. A report of a run
has to credit both, and the provenance tree has to say which call led to which
citation — which is the whole point of tracking a run rather than listing
dependencies.
"""

from ._ackredit import ACKREDIT_INSTALLED, register_item
from .core import analyse

register_item(
    id="dummypipeline:2026:workflow",
    type="article",
    title="A workflow for dummy analyses",
    authors=["Moreno, Carla"],
    year=2026,
    journal="Journal of Dummy Workflows",
)

register_item(
    id="dummypipeline:dataset",
    type="dataset",
    title="Reference dummy measurements",
    authors=["Moreno, Carla"],
    doi="10.5281/zenodo.9999999",
)

__all__ = ["ACKREDIT_INSTALLED", "analyse"]
