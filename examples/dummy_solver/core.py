"""The library's actual work, such as it is."""

from ._ackredit import scoped_usage, track_item


@scoped_usage(target="dummy_solver.solve", credit_bound=True)
def solve(system, method="direct"):
    """Solve a dummy system.

    `credit_bound=True` credits the method paper on every call, because every
    path rests on it. The iterative paper is credited by the branch that uses
    it, which is the distinction Ackredit exists to make: a run that never
    refines should not cite the refinement.
    """
    if method == "iterative":
        track_item("dummysolver:2026:iterative")
        return f"{system} solved iteratively"

    return f"{system} solved directly"
