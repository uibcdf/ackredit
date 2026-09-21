"""A pipeline step that calls another library."""

from dummy_solver import solve

from ._ackredit import scope, track_item


def analyse(measurements, method="direct", use_reference=False):
    """Analyse measurements, solving them with DummySolver.

    The scope is entered explicitly rather than through a decorator, because
    part of this function is worth attributing and part is not. What
    DummySolver credits inside the call lands under this scope, so the
    provenance tree shows one library's citations arriving through another's
    call.
    """
    with scope("dummy_pipeline.analyse"):
        track_item("dummypipeline:2026:workflow")

        if use_reference:
            track_item("dummypipeline:dataset")

        return solve(measurements, method=method)
