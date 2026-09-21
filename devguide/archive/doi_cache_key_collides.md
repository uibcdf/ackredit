---
summary: Two DOIs could share one cache file, so one work's metadata was served for another.
issue: uibcdf/ackredit#12
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: high
verification: reproduced
area: [metadata]
guard: tests/test_enrichment.py
normative:
blocked_by: []
supersedes: []
---

# The DOI metadata cache can serve one work's metadata for another

## What

The cache was keyed by `doi.replace("/", "_")`. A DOI suffix may contain either character,
so distinct DOIs collided and the title, authors and year of one work were written into
the citation of another.

## How

```python
"10.1234/a_b".replace("/", "_")   -> "10.1234_a_b"
"10.1234/a/b".replace("/", "_")   -> "10.1234_a_b"
```

## Why

Enrichment exists to supply what the user did not. Supplying it from a different work
names the wrong people and the wrong paper in a file that goes to a journal. Unlike a
network failure it is sticky: a poisoned entry keeps returning the wrong answer across
restarts.

## What was refuted

Escaping more characters was rejected: any lossy transformation of an identifier can
collide, and the property needed is that distinct DOIs map to distinct names, which only a
digest gives. The readable prefix is kept so the directory can still be inspected by eye,
but identity rests on the digest.

Writing the DOI into the cached document and checking it on read was also considered.
It detects the collision rather than preventing it, and still leaves two works fighting
over one file.

## Scope and exclusions

Covers cache identity and two defects in the same path: the request announced
`Ackredit/0.4.0` while the package was at 0.5.0, and the DataCite branch read a scalar
`title` the DataCite schema does not define, so it was dead code. Excludes cache expiry,
which is not implemented and is not claimed to be.

## Acceptance criteria

Met by the commit closing this record:

- a cache name carries a digest of the DOI, so distinct DOIs cannot collide;
- the name is a single safe file name for adversarial input, carrying no path separator
  and no dot run;
- the user agent announces the running version, read from the package;
- DataCite titles are read from `titles`, the field its schema defines;
- `tests/test_enrichment.py` pins each, including the three DOI pairs that collided.
