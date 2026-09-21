---
summary: The vision promised that anyone could add an output format, and only a private module dict existed.
issue: uibcdf/ackredit#36
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: measured
area: [api, formats, documentation]
guard: tests/test_format_plugins.py
normative: devguide/decisions.md
blocked_by: []
supersedes: []
---

# Output formats are not extensible

## What

`devguide/vision.md` listed as a design pillar: "Extensible: Anyone can add new output
formats or injections for third-party libraries."

Half of it was true. Injections were extensible through `add_injection` and the
`ackredit.citations` entry-point group. Formats were not: `_RENDERERS` was a private module
dict, there was no registration function, and no entry-point group resolved one, so a third
party could only add a format by reaching into a name `docs/content/about/stability.md`
explicitly says may change without notice.

It was the single entry left under "Pending Decisions", and theme F could not close over
it, because it decided whether `_RENDERERS` is implementation or surface.

## How

It is implementation, and `register_format(name, renderer, extension)` is the surface in
front of it. A renderer is called as `renderer(used, items)` and returns text; the
extension is what `dump` names the file. An `ackredit.formats` entry-point group mirrors
`ackredit.citations`: the entry point loads a callable that registers, so one package can
ship several formats.

Plugins load lazily, the first time the format table is consulted, and once. Requiring a
call before `report(format="mine")` works would make an unknown-format refusal the normal
first experience of the feature. The loaded flag is set before the scan rather than after,
because a plugin's register function may itself ask what formats exist; the import hook
marks a package the same way and for the same reason.

Three catalog codes, each added with the path that emits it: `ACKREDIT-E005` for a name
already taken, `ACKREDIT-E006` for a format that cannot work, `ACKREDIT-W014` for a plugin
that failed to load.

## Why

A citation tracker whose report is the product should let a group render that report the
way its journal, its institution or its pipeline needs, without forking. The alternative
was to delete the claim, which costs the same amount of honesty and none of the capability.

The rule that carries the design is that **a registered name is never replaced**, built-in
or from another plugin. A plugin taking over `bibtex` would make a request succeed and
return a report that is not the one asked for, which is the defect `uibcdf/ackredit#15`
closed. For the same reason names are held to one lower-case style at registration: lookups
match exactly, so `BibTeX` would become a second, silently different format rather than an
alias — the case-insensitive matching refused in #15, arriving through the back door.

## What was refuted

- **Dropping the pillar instead.** It was the cheaper honest option and it gives up the
  capability. The cost of building it is one public name and three catalog codes.
- **Letting the entry-point name be the format name, with the object as the renderer.**
  More declarative, and it cannot carry the file extension, which would split the one table
  that exists so a renderer and an extension cannot disagree about which formats exist.
- **Allowing a plugin to replace a built-in, for overriding output.** It is the whole
  defect class this library keeps closing. A group that wants different BibTeX registers
  `mylab-bibtex` and asks for it by name.
- **Case-insensitive lookup, so `BibTeX` would work.** Refused in #15 for a reason that
  still holds: it fixes `BibTeX` and leaves `bibtext` silently wrong. One style is enforced
  where the name is chosen instead.
- **Loading plugins eagerly at import.** It makes importing Ackredit scan the installed
  distributions, for a feature most processes never use.

## Scope and exclusions

Covers output formats. Aliases stay built-in: `csl` resolves to `csl-json` because it was
published, and a plugin cannot take an alias either.

## Acceptance criteria

- a format registered by hand renders, is advertised and reaches `dump` — met;
- a format arriving through an entry point does the same, and one plugin may ship
  several — met;
- no built-in name, alias, or name another plugin took can be replaced, and the built-in
  still renders after a refused attempt — met;
- a broken plugin is reported and costs nothing else — met;
- the distributions are scanned once, and a plugin that asks what exists does not
  recurse — met;
- `devguide/vision.md` now describes a mechanism that exists.
