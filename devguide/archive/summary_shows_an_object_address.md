---
summary: summary() defined only _repr_html_, so printing it anywhere but a notebook gave the object's address in memory.
issue: uibcdf/ackredit#51
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: medium
verification: measured
area: [contrib]
guard: tests/test_html_escaping.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# summary() shows an object address

## What

```
>>> print(ackredit.summary())
<ackredit.contrib.jupyter.CitationsHTML object at 0x7191343fc590>
```

`CitationsHTML` defined `_repr_html_` and nothing else, so Jupyter rendered the table and a
REPL, a script and a log got the default object repr. A user who tried the call the guide
shows them, anywhere but a notebook, was told where the object lives in memory.

## How

`__str__` renders through the `text` renderer that already exists, rather than a second
implementation, so the two cannot disagree about what a run cited. `__repr__` is the same:
a display object is read, not reconstructed.

## Why

It was also the whole of why the name was classified provisional — "an object whose only
contract is `_repr_html_`. What else that object should offer is unexplored." Three
renderings of one run is the contract, and it is written on the class.

## What was refuted

- **Rendering the Markdown report instead.** It is the default of `report()` and carries
  markup that a terminal shows as punctuation; `summary()` is for looking, and the text
  renderer is what that is for.
- **A `__repr__` that identifies rather than renders.** It is the convention for a value
  that can be reconstructed. This one exists to be looked at, and in a REPL `__repr__` is
  what is shown.

## Acceptance criteria

- `str()` and `repr()` of a summary name the citations, and neither contains an
  address — met;
- an empty session says so in text as it does in HTML — met;
- the notebook rendering is unchanged — met.
