---
summary: dependency_info was promised by naming which of DepDigest's two shapes is the contract and verifying the version it relays.
issue: uibcdf/ackredit#59
status: resolved
opened: 2026-09-22
closed: 2026-09-22
severity: low
verification: measured
area: [api, dependencies]
guard: tests/test_dependency_report.py
normative: docs/content/about/stability.md
blocked_by: []
supersedes: []
---

# dependency_info relays a promise

## What

`dependency_info` is `return get_info("ackredit", format=format)`, so the keys a caller
reads are DepDigest's. It was the last provisional name, and calling it stable without more
would promise something we do not decide.

## How

DepDigest does not have one shape, it has two, and only one of them is a contract:

```
format="table"  ->  [{"Library": …, "Status": "Not Installed", "Install (PyPI)": …}]
format="dict"   ->  {"schema": {"name": "depdigest.get_info", "version": "1.0"},
                     "dependencies": [{"library": …, "installed": false, …}], …}
```

The machine shape states its own version in the payload. The table is capitalised keys with
prose in the values, for a person to read. So the promise is the machine shape, relayed as
`depdigest.get_info@1.0`, and the table is a rendering that may change — both said on the
function.

The relayed version is checked. A payload declaring another raises `ACKREDIT-W017` and is
still returned, because it states its own schema and a caller who can read the new one may.

## Why

Removing it was the alternative and it is what `standards/ACKREDIT_GUIDE.md` tells a host
library to call to learn what its environment supports, with two more mentions in
`docs/content/about/installation.md`. Removing it would leave that advice with nothing
behind it.

Relaying is honest as long as it is said. What makes it safe is not the relay but the
check: a schema change on DepDigest's side is a change to this function's contract, and it
is now announced by us rather than discovered by a user.

## What was refuted

- **Pinning `depdigest` to the version that provides `get_info@1.0`.** It was the first
  plan and it cannot be written: the package version and the schema version are
  independent, so a pin expresses a guarantee it does not give. The payload carries the
  version, so the check gives exactly it.
- **Defining Ackredit's own shape and mapping DepDigest's into it.** It closes the question
  completely and duplicates a schema the sibling already versions and self-describes,
  leaving two shapes to keep in step. Worth revisiting only if DepDigest stops versioning
  it.
- **Refusing to return a payload whose version is not the promised one.** It would break a
  caller who can read the new shape, for a fact the payload already states.
- **Promising the table.** Its values are prose — "Not Installed" — and its keys are
  capitalised with spaces. It is a rendering, and rendering is where wording changes.

## Acceptance criteria

- the machine shape states `schema.version == "1.0"` and lists every declared library — met;
- a payload declaring another version is reported and still returned — met;
- a payload with no version is not guessed at — met, including the table;
- the guide's advice still works — met;
- with this, thirty-three public names and none provisional.
