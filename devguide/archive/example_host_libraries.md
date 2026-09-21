---
summary: Two host libraries in the repository, integrated for real, used by the documentation and the tests.
issue: uibcdf/ackredit#23
status: resolved
opened: 2026-09-21
closed: 2026-09-21
verification: reproduced
area: [documentation, testing]
guard: tests/test_example_libraries.py
normative: devguide/roadmap.md
blocked_by: []
supersedes: []
---

# Two example host libraries, for the documentation and the tests

## What

`tests/test_integration_guide.py` executes the guide's template and compares every
fallback signature against the real one. That checks shapes. Six things only appear when a
library is actually built on Ackredit, and none of them was covered: registering while a
host is imported, citations nesting across two libraries, `credit_bound` inside a real
call graph, `add_injection` for a package the host uses internally, a host working with
Ackredit genuinely absent, and a report naming both libraries.

## How

`examples/dummy_solver` and `examples/dummy_pipeline`, the second calling the first. They
compute nothing; they are integrated the way a real host would be.

The design that makes them worth more than a fixture: each `_ackredit.py` **is** the
guide's template, asserted byte-identical rather than copied. The guide stops being a
snippet checked in isolation and becomes a file two working libraries use.

## Why

Every defect found in `standards/ACKREDIT_GUIDE.md` so far — an import that raised and was
swallowed by the template's own `except`, a fallback whose signature had drifted, a
`NameError` in the advanced sections, four names with no fallback — was found by reading
it. These would have been found by using it.

## What was refuted

**Treating this as roadmap theme C.** It is not, and it is recorded separately so it
cannot be counted as progress towards it. A host written here makes the mistakes we
anticipated; the value of `molsysmt` integrating is that they will make one we did not.
This lowers the cost of that and does not substitute for it.

**One library instead of two.** The interesting case is the second: a pipeline calling a
solver, so citations cross a boundary and the provenance tree describes something real. A
single dummy cannot exercise that, and it is the case the tree exists for.

**A stubbed import for the "Ackredit absent" test.** It proves the fallbacks parse, not
that a host survives. The test runs a subprocess where importing `ackredit` genuinely
raises, which is the state a user without it is in.

## Scope and exclusions

Covers the libraries, the tests over them, and the documentation page that runs them. They
are not part of the installed distribution, asserted by a test rather than assumed.

## Acceptance criteria

Met by the commit closing this record:

- two host libraries whose `_ackredit.py` is the guide verbatim, guarded — verified by
  making one drift, which fails with the guide named as the authority;
- a run crediting only the path it took, across both libraries: two citations one way,
  four the other, from the same call;
- the provenance tree showing which call brought each citation in, with neither library
  naming the other's papers;
- both hosts working in a subprocess where importing Ackredit raises;
- a documentation page that runs them, whose quoted output is asserted against what the
  code actually prints. The provenance block was written from memory first and was wrong,
  which is why that assertion exists.
