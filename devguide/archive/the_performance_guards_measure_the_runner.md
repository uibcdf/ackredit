---
summary: Both timing guards compared a small sample against a large one, so a shared runner failed a commit that could not have caused it.
issue: uibcdf/ackredit#45
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: measured
area: [testing]
guard: tests/test_persistence_cost.py
normative:
blocked_by: []
supersedes: []
---

# The performance guards measure the runner

## What

`test_crediting_one_more_caller_costs_the_same_at_ten_thousand` failed on CI for commit
`c350455`, which changed `ackredit/formats/csl_json.py` and nothing that crediting touches:

```
AssertionError: 0.9 µs/call with 500 callers became 4.4 µs with 5 000
assert 4.426e-06 < (8.912e-07 * 3)
```

It passed locally five runs out of five.

Both timing assertions had the same shape. Each compared **a small sample against a large
one** — 200 items against 2 000, 500 callers against 5 000 — so the two measurements did
not have comparable noise, and the smaller was the noisier of the two. When it came out
fast it set a threshold an ordinary scheduling hiccup exceeded.

## How

Both sides now measure the same number of operations, so their noise is comparable, and
differ only in the state that already exists: 400 items into an empty session against 400
into one holding 4 000; 400 calls against no callers against 400 against 5 000.

Each side is the **minimum of three repetitions**. Interference only ever adds time, so the
minimum is the closest estimate of the real cost available on a machine we do not own.

## Why

A gate that fails at random is worse than no gate, which is what
`tests/test_workflow_hygiene.py` already says about a step that cannot fail: people stop
reading it. This one had just cost a green run on a commit that could not have caused it,
and the natural next step for anyone in a hurry is to re-run until it passes.

## What was refuted

- **Loosening the thresholds.** It treats the symptom and makes the guards weaker against
  the defects they exist for, which are large effects, not marginal ones.
- **Dropping the timing tests for an assertion about the implementation** — that
  `_callers` is a set, that the journal is appended. It tests how rather than what, and
  would pass a rewrite that was correct in shape and slow in fact.
- **Marking them as expected to fail on CI.** The only thing worse than a gate nobody
  trusts is one nobody runs.

## Acceptance criteria

- both guards pass consistently, including with eight processes saturating the CPU — met,
  three runs out of three under load and eight out of eight without it;
- both still fail on the defect they exist for — met, verified by reintroducing each:
  removing the caller index fails the second, and rewriting the whole document on every
  event fails the first with a ratio of twenty, `1 046 µs` against `20 440 µs`;
- the suite does not get slower for it — met, the file runs in 0.2 s.
