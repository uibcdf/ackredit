---
summary: The integration guide reached no repository and opened without saying what Ackredit is.
issue: uibcdf/ackredit#24
status: resolved
opened: 2026-09-21
closed: 2026-09-21
verification: reproduced
area: [documentation, governance]
guard: tests/test_integration_guide.py
normative: MOLSYSSUITE_GUIDE.md
blocked_by: []
supersedes: []
---

# The integration guide reaches no repository, and opens without saying what Ackredit is

## What

`standards/ACKREDIT_GUIDE.md` is registered in `suite.toml` as a guide Ackredit owns, with
`consumers = []`. Every other component guide lists the repositories that receive it.

Looking at why it had not been distributed turned up the better question: it was not ready
to be. It opened at "1. Centralization File: `_ackredit.py`", so a maintainer finding that
file appear in their repository had no way to know what Ackredit was or why it had
arrived, and it had no "Required behavior" section. Every mature component guide has both.

```
section                              SMonitor  ArgDigest  DepDigest  Ackredit
What is X                              yes        yes        yes       no
Why this matters in this library       yes        yes        yes       no
Required behavior (non-negotiable)     yes        yes        yes       no
SMonitor Integration                    —         yes        yes       no
```

## Why

A guide that reaches nobody is documentation of an integration nobody can discover. The
last row mattered particularly: Ackredit has emitted catalog diagnostics since
`uibcdf/ackredit#6`, and a host integrating it should know which codes it will see and
that none of them is swallowed.

## What was refuted

**Registering consumers first and improving the guide afterwards.** Registering means
other maintainers receive a document; sending one that does not say what it is for would
have been asking five repositories to carry a puzzle.

**Guessing the consumer list.** The classification in `suite.toml` belongs to
`uibcdf/molsyssuite`, so the proposal there names the five `scientific-component`
members — the boundary the registry already draws — rather than a set we invented.

**Waiting for the guide to survive a real integration.** Roadmap theme C expects it to be
corrected by one, which argues for delaying, but consumer copies are synchronized from the
canonical source and never repaired locally, so they receive the correction. Waiting would
mean the first integrator works without the guide, which is the wrong way round. The
concern is stated in the central proposal rather than settled quietly here.

## Scope and exclusions

Covers the guide's content. Registering consumers edits `suite.toml` and is requested in
`uibcdf/molsyssuite#35`.

## Acceptance criteria

Met by the commit closing this record:

- the guide says what Ackredit is and why a host would want it, before the wiring;
- four non-negotiable behaviours are stated, including that declaring belongs at import
  and crediting belongs at runtime, which is the distinction the library exists for;
- the six diagnostics a host is most likely to meet are tabulated, and a test asserts
  every code the guide promises exists — a documented code that never arrives is worse
  than an undocumented one, because the host filters for it and believes it is covered;
- the guide points at the two example libraries, whose `_ackredit.py` is its own template
  asserted byte-identical, so what it shows is what runs.
