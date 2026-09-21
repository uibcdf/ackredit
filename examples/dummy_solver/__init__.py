"""DummySolver — a host library, small enough to read and real enough to test.

It exists to show what integrating Ackredit looks like from the other side, and
to give the test suite a host that behaves like one: it declares what it can
cite while it is being imported, credits some of that unconditionally and some
of it only on the path that used it, and keeps working when Ackredit is absent.

Nothing here computes anything interesting. Everything here is what a real host
would do.
"""

from ._ackredit import ACKREDIT_INSTALLED, add_injection, bind, register_item
from .core import solve

# Declared while this module is imported, which is the moment a host has. The
# registry is shared and outlives any session, so this is the right place; what
# was *used* is recorded later, per run.
register_item(
    id="dummysolver:2026:method",
    type="article",
    title="A direct method for dummy systems",
    authors=["Ruiz, Ana", "Gómez, Luis"],
    year=2026,
    journal="Journal of Dummy Computation",
    doi="10.1234/dummy.2026.001",
)

register_item(
    id="dummysolver:2026:iterative",
    type="article",
    title="An iterative refinement for dummy systems",
    authors=["Ruiz, Ana"],
    year=2026,
    journal="Journal of Dummy Computation",
)

register_item(
    id="dummysolver:software",
    type="software",
    title="DummySolver",
    authors=["Ruiz, Ana"],
    url="https://example.org/dummysolver",
)

# The method paper is what `solve` always rests on, so it is bound to the target
# and credited by `credit_bound=True` rather than repeated in the body. The
# iterative paper is not bound: only the branch that uses it credits it.
bind(target="dummy_solver.solve", items=["dummysolver:2026:method"])

# A third-party package this library uses internally. The user never calls it,
# so they would never think to cite it; an injection says that using this
# library means using that work.
add_injection(target_module="numpy", items=["external:numpy"])

__all__ = ["ACKREDIT_INSTALLED", "solve"]
