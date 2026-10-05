(User_Reporting)=
# Generating Reports

Once your workflow has finished, Ackredit provides multiple ways to view and export the collected citations.

Ask which formats exist rather than guessing. A name Ackredit does not know is refused
with `ACKREDIT-E004`, naming the ones it does, rather than quietly producing a different
format:

```python
import ackredit

ackredit.available_formats()
```

## Jupyter Notebook Summary
In a notebook, you can see a stylized HTML table with clickable links.

```python
import ackredit

ackredit.summary()
```

## Standard Formats
Use `report(format=...)` to get a string in any of these formats:
*   `markdown` (Rich markdown with links)
*   `bibtex` (Standard BibTeX file content)
*   `csl-json` (For Zotero, Mendeley, and EndNote)
*   `json` (Every registered field, plus what used it; for your own tooling)
*   `provenance` (Hierarchical tree showing *why* each item was cited)
*   `latex` (A complete, compilable LaTeX document)
*   `text` (Plain text, for a log or a terminal)
*   `workflow` (Bibliography, contextual uses and graph together; since 0.10.0)

This list is the built-in list. `ackredit.available_formats()` returns it at runtime,
together with any format a plugin added, and asking for a name that is not there raises
`ACKREDIT-E004` rather than quietly returning a different report. A test keeps this page
and that function in agreement.

### CFF references in CSL-JSON

Development after 0.10.1 also carries original CFF work kinds into CSL-JSON:
books and edited collections become `book`, theses become `thesis`, reports
and CFF manuals become `report`, and conference papers become
`paper-conference`. Magazine and newspaper articles retain their specific
periodical kinds. Pamphlets, patents, personal communications, blogs, maps and
unpublished manuscripts have explicit mappings. Unsupported kinds remain
`document`, with their original `_cff_type` retained in the saved attribution.
Existing BibTeX source-type interpretation retains its own mapping.

Publication dates retain their recorded precision. A full `date-published`
takes precedence over `date-released`; release dates are used when publication
dates are absent. An explicit year and its numeric month, if any, win over
conflicting full dates. Consistent full dates can add day precision; year/month
alone never invent a day. Numeric months are interpreted only within 1–12.
Textual years and non-calendar dates stay literal, while all original fields
remain available in the portable payload. CFF calendar dates use `YYYY-MM-DD`;
ISO week dates, compact dates and impossible calendar days are not converted
into apparently valid publication dates. A stated literal publication date
does not borrow a release year.

CFF page counts reach CSL `number-of-pages`, separately from the page range
in `page`. Saving and rereading attribution preserves these original records;
export requires no producer import, network lookup or new execution credit.
These additions are tracked in [Ackredit #96](https://github.com/uibcdf/ackredit/issues/96)
and are not present in the already published 0.10.1 archive.

## Contextual workflow reports

The explicit `workflow` format ships in public 0.10.0 and recommended 0.10.1.
It combines numbered references, recorded roles, original software
versions, use/capture context and the graph in one offline Markdown report:

```python
saved = ackredit.Attribution.from_json(payload_json)
print(saved.report(format="workflow"))
```

This reader does not import the producer, consult its current bibliography or
record new credit. A software description article keeps its own publication
metadata while each use retains the software version it described. Graph
citations use the same reference numbers as the bibliography and use table.
Unknown metadata, roles and unscoped uses are shown explicitly.

The report counts distinct recorded uses; it does not infer invocation counts,
chronology, scientific success or complete instrumentation. An observed public
function earns entry evidence; a completed backend credit has the producer's
more specific completion boundary. Shared graph targets are expanded once and
later incoming edges remain visible as `shared; shown above`; ancestor cycles
remain `above`. Deep graphs do not consume Python's recursion stack.

`workflow` now reserves a built-in name. Existing third-party plugins using
that name must choose another. Existing bibliography formats remain available.
Selecting both `markdown` and `workflow` in `dump` writes separate `.md` files.

## Adding your own format

A renderer takes what the run credited and returns text:

```python
import ackredit


def render(used, items):
    """used: item id -> the names that credited it. items: the registry."""
    return "\n".join(
        f"{item_id}: {items[item_id]['title']}" for item_id in sorted(used)
    )


ackredit.register_format("titles", render, "txt")

print(ackredit.report(format="titles"))
ackredit.dump("reports", formats=["titles"])  # writes ackredit_report.txt
```

To ship one from a package, declare an entry point that registers it. Ackredit finds it
the first time a report is asked for, so nothing needs to be called first:

```toml
[project.entry-points."ackredit.formats"]
titles = "my_package.formats:register"
```

```python
# my_package/formats.py
def register():
    ackredit.register_format("titles", render, "txt")
```

Two rules are worth knowing before you choose a name.

**A name that exists is never replaced**, built-in or from another plugin: registering
over one raises `ACKREDIT-E005`. A format that could take over `bibtex` would let a
request succeed and return a report that is not the one asked for.

**Names are lower case**, matching the built-in ones, and are matched exactly. `BibTeX`
is refused with `ACKREDIT-E006` rather than accepted as a second name for the same thing.

A plugin that fails to load is reported as `ACKREDIT-W014` and costs nothing else: the
built-in formats and every other plugin still work.

## Consolidating Results (`dump`)
Save multiple formats at once to a directory.

```python
import ackredit

ackredit.dump("my_citations", formats=["markdown", "bibtex", "provenance", "latex"])
```

Each format is written to `ackredit_report.<extension>`. Two formats can share an
extension — `text` and `provenance` are both `.txt` — and asking for both writes
`ackredit_report_text.txt` and `ackredit_report_provenance.txt`, so neither replaces the
other. Only a clash is renamed: the LaTeX report points at `ackredit_report.bib`, and that
name does not move.

A file holds one report, and its name chooses it:

```python
ackredit.dump("refs.bib")  # BibTeX
ackredit.dump("refs.csl.json")  # CSL-JSON, for Zotero and friends
ackredit.dump("citations.md")  # Markdown
```

A name that says nothing, such as `citations.dat`, gets Markdown. Asking for a format
the name contradicts writes what you asked for and warns with `ACKREDIT-W018`, because
whoever opens the file later will trust its name. Asking for several formats and one file
is refused with `ACKREDIT-E009` and writes nothing; pass a directory instead.

### Automatic PDF Generation
If you have `pdflatex` installed, Ackredit can compile the LaTeX report into a PDF automatically.

```python
ackredit.dump("my_citations", build_pdf=True)
```

## Collaborative Workflows (Aggregation)
If you run analysis in a parallel cluster, you can merge multiple session files into one.

```python
import ackredit

ackredit.aggregate(["node1.json", "node2.json", "node3.json"])
print(ackredit.report())
```

## From the command line

Ackredit installs an `ackredit` command that works on a session file a run left behind,
so a report can be produced after the fact, from a job that has already finished.

```bash
ackredit report session.json --format bibtex
ackredit dump session.json reports/ --pdf
ackredit aggregate run-*.json --output all.json
```

`report` accepts any format `ackredit.available_formats()` offers, including one a plugin
registered. `aggregate` names on stderr any file it could not read, says how many of the
files it was given were actually merged, and exits non-zero when something you asked for
did not happen.

Reading never writes. A session file that does not exist is an error, not an empty report.

**What a session file can tell you.** A session is a journal of events — which id was
credited, and by what — and not the metadata of the items. That metadata lives in the
registry of the process that declared it, which is why a report produced inside your
workflow carries titles, authors and DOIs. A command line opening a file on its own has no
host library to import, so it names the items the run credited and cannot describe them:

```
- **molsysmt:software**
  - Used by: molsysmt.basic.convert
```

For a full bibliography, call `ackredit.report()` in the process that did the work, or
`ackredit.dump()` at the end of it.
