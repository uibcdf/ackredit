"""Isolation for a library whose state is process-wide by design.

The two halves of that state are not the same kind of thing. **Declarations**
live in the registry and are made once, at import: a host library says what it
*could* cite, and by the time a test runs that import has happened and cannot be
repeated. **Observations** live in the session and are per run.

So they are isolated differently.

The session is cleared around every test, always. Carrying one test's tracking
into the next is what let `test_csl_json` assert on `report()[0]` and read an
item another file had tracked; it passed only because of the order the files
happened to run in, and broke as soon as a file was added between them.

The registry is left alone unless a test asks for `clean_registry`, which empties
it and puts it back afterwards. A test that cleared it outright destroyed the
import-time declarations the example libraries had made, for every test that ran
later — which worked only while those files happened to run last.
"""

import pytest

from ackredit.core.registry import Registry
from ackredit.core.session import current_session


@pytest.fixture(autouse=True)
def _isolated_session():
    current_session().clear()
    yield
    current_session().clear()


@pytest.fixture
def clean_registry():
    """An empty registry for this test, restored when it ends."""
    items = dict(Registry.items)
    injections = {key: list(value) for key, value in Registry.injections.items()}

    Registry.items.clear()
    Registry.injections.clear()
    yield Registry

    Registry.items.clear()
    Registry.items.update(items)
    Registry.injections.clear()
    Registry.injections.update(injections)
