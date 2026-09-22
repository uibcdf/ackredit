"""The ArgDigest decorator, bound to Ackredit's configuration.

ArgDigest finds a library's configuration from the module name of the function
it decorates, and this hands it ours explicitly, which is the pattern every
suite component uses.

**Where this may be used.** The decorator costs 11.71 µs on the machine that
measured `docs/content/about/performance.md`, against 1.02 µs for
`track_item`. Declaration and reporting are decorated; the tracking path, which
runs once per credited citation, is not, and validates inline where it must.
`skip_digestion` is not the answer there: the guide reserves it for internal
calls carrying values the library just built, and never for a public boundary.
"""

from __future__ import annotations

from argdigest import arg_digest as _arg_digest


def arg_digest(*args, **keywords):
    """Digest arguments against `ackredit/_argdigest.py`."""
    return _arg_digest(config="ackredit._argdigest", *args, **keywords)
