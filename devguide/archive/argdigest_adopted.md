---
summary: ArgDigest adopted where it fits and refused where it costs, closing six public functions that accepted arguments that could not be right.
issue: uibcdf/ackredit#62
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: high
verification: measured
area: [api, dependencies]
guard: tests/test_argument_contract.py
normative: devguide/vision.md
blocked_by: []
supersedes: []
---

# ArgDigest adopted

## What

ArgDigest is the third MolSysSuite infrastructure component. Decision 6 adopted SMonitor
and DepDigest and was silent about it; MolSysMT uses it in thirty-five files and Ackredit
used it in none, with no `ARGDIGEST_GUIDE.md` and nothing recording the non-adoption as a
decision.

What that cost, measured in `uibcdf/ackredit#61`:

```python
ackredit.bind("mylib.convert", "paper:2024")
ackredit.bound_items("mylib.convert")
# ['p', 'a', 'e', 'r', ':', '2', '0', '4']

ackredit.aggregate("session.json")     # the brackets forgotten
# merged: {} — each character is a path that does not exist, and a missing file
#              is skipped by design, so nothing was merged and nothing said so
```

## How, and where not

The decorator costs **11.71 µs**, against **1.02 µs** for `track_item`. So the adoption is
selective, and the boundary is measured rather than felt:

- **declaration and reporting**, called at import or a handful of times per run, are
  decorated: `register_item`, `bind`, `add_injection`, `load_bibtex`, `aggregate`,
  `enable_persistence`, `scoped_usage`, `register_format`, `report`, `dump`, `compile_pdf`,
  `dependency_info`;
- **the tracking path** is not: `track_item`, `track_target`, `credit_bound`,
  `bound_items`. Where a defect was measured there — `track_item(None)` putting `{None: []}`
  in the report — the check is an `isinstance`, and it moved the published cost from 1.02 µs
  to 1.17.

`skip_digestion` is not the answer for that path: the guide reserves it for internal calls
carrying values the library just built, and never for a public boundary, which is what
`track_item` is.

Both axes are declared, as rule 7 requires of a function taking `**kwargs`:

- `register_item(**item)` admits the `citation_field` domain — any field name except the
  underscore-prefixed ones Ackredit keeps. That is not tidiness: `register_item(id="x",
  title=r"\\textbf{$}", _source="bibtex")` used to reach straight past the escaping closed
  in `#7` and `#9`, and the rendered BibTeX carried raw LaTeX.
- `report(format, **kwargs)` admits `format_options`, a `by_value` domain keyed on the
  format and **derived from the renderer table** rather than written out, so a format
  registered by a plugin is covered and the declaration cannot drift from what it declares.

## What the adoption removed

`report` checked its options by binding the renderer's signature, which `#53` had added.
ArgDigest now refuses them first, against a domain reading the same table, so that check
and its `ACKREDIT-E007` are gone. Adopting a component means not doing by hand what it
does; keeping both would have left two checks that can disagree.

The cost is a less specific message: ours named the format and what it accepts, and
ArgDigest's names the argument. That is reported upstream rather than worked around.

## What was refuted

- **Decorating everything.** Measured: the tracking path would go from 1.02 µs to about
  12.7, and "light in execution" is one of the four things this library is for.
- **`STRICTNESS = "warn"`.** A citation field is an open value space — a title is free
  text, a year may be "in press" — so a warning per undigested field is noise on every
  call. Which *names* are admissible is axis 1's answer and it is declared; the values are
  not ours to constrain.
- **Declining the `format_options` domain because our own message was better.** The domain
  is expressible, so "cannot be expressed" would have been false, and the guide is the
  standard.

## Mistakes worth recording

`admits=["signature", "format_options"]` reads `signature` as the name of a domain, which
does not exist, and the refusal that follows says the function "does not accept the
argument 'unknown'". The token only means anything as the whole value. Reported upstream.

Two edits of mine landed wrong and the tests caught both: `report` received the decorator
twice while `dump` received none, and `digest_formats` refused `formats=None`, which is how
`dump` says "the default list".

## Acceptance criteria

- a string where a sequence is expected is refused, for `bind`, `add_injection`,
  `aggregate` and `dump` — met;
- a name that is not one is refused, on the decorated path and on the tracking path — met;
- a path that is not one is refused, where a bare `TypeError` from `pathlib` used to
  surface — met;
- a reserved key is refused and an ordinary field accepted — met;
- an option reaches the format that takes it and is refused by one that does not — met;
- the decorated and undecorated sets are asserted, because the boundary is the decision —
  met;
- `tests/test_argument_contract.py`, 38 tests.
