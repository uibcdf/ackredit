(User_PublicationTools)=
# Bibliography for publication tools

Export the detached attribution saved beside a scientific result. Its records
describe that result's original references; exporting does not credit another
calculation or consult the producer's current bibliography:

```python
from pathlib import Path
import ackredit

saved = ackredit.Attribution.from_json(Path("result.json").read_text())
Path("references.bib").write_text(saved.report("bibtex"), encoding="utf-8")
Path("references.csl.json").write_text(saved.report("csl-json"), encoding="utf-8")
```

An export carries metadata; the receiving tool's selected style decides what to
print, abbreviate, sort or capitalize. Keep the saved attribution as the original
record rather than replacing it with a style engine's converted data.

## Tested receiving checkpoint

[Ackredit #120](https://github.com/uibcdf/ackredit/issues/120) exercises a normally
installed development wheel on Linux/Python 3.14.8 with BibTeX 0.99d and pdfTeX
1.40.25 from TeX Live 2023/Debian, plus Pandoc 3.11 and its built-in citeproc.
The styles are `plain.bst` and Pandoc's bundled **Chicago Manual of Style 18th
edition (author-date)**. Exact style hashes, inputs and observations are in the
[receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/publication_tools_120_2026-10-06.json).

Six synthetic records cover two software releases, a dataset, an article, explicit
editors and a typed CFF preferred collection. Both Pandoc readers retain all six
IDs, original versions and DOI forms. Institutional names with commas and `and`
remain indivisible; declared persons retain their name text and suffix. The
preferred work keeps its own metadata without borrowing the root software's
version or DOI. Non-ASCII names/titles and escaped TeX characters reach the
tested bibliography, and the BibTeX PDF compiles.

Development after public 0.11.0 repairs BibTeX editor export: `editors` becomes
the standard `editor` field, explicit name objects become names, and matching CFF
declarations preserve institutional identity, particles and suffixes. Explicit
name-list replacement still wins over old hints. CFF `book` and `edited-work`
become `@book`; other previously unmapped kinds keep their existing fallback.
Imported BibTeX entry types and LaTeX names remain original. These repairs await
a future qualified release; the immutable public 0.11.0 artifact lacks them.

## DOI presentation and duplicate identity

The follow-up [#121](https://github.com/uibcdf/ackredit/issues/121) repairs supported
DOI presentation in development after public 0.11.0. For example, an original
`https://doi.org/10.5555/work` becomes CSL `DOI: "10.5555/work"`; the selected
style then creates one resolver link. Markdown, workflow and notebook links
likewise use one `https://doi.org/` prefix. The workflow's DOI label still shows
the original text.

Supported forms are bare `10.<digits>/<suffix>` names, `doi:` labels, and exact
HTTP(S) `doi.org` or legacy `dx.doi.org` URLs with an unambiguous suffix. Wrapper
case and outer whitespace do not affect the projection; identifier case and
punctuation remain intact. This is presentation, not registration validation.
Resolver URLs with percent escapes, queries or fragments, nested wrappers,
shortDOIs, other hosts/ports and unknown values are left unchanged. No decoding,
network lookup or guess supplies a different identifier.

Saved attribution, the complete bundle and JSON/BibTeX exports keep the original
DOI field. The existing [composition identity contract](attribution_composition.md)
continues to use caller IDs and exact original records, independently of DOI
presentation:

- Equal originals with the same ID share one bibliographic entry.
- Different original records under one ID raise `ACKREDIT-E011`, even when their
  CSL DOI fields would look identical. No preferred spelling replaces a claim.
- Different IDs remain distinct, including releases sharing one DOI or equivalent
  DOI forms. There is no automatic alias detection or duplicate merging.

The new normally installed receiving checkpoint repeats the same six-record
saved input and unchanged engines/styles from #120: CSL readers keep all IDs and
versions, the full-URL DOI gets one prefix, and original BibTeX bytes remain
identical. The
[paired receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/doi_presentation_121_2026-10-06.json)
retains baseline/candidate identities and the original unmodified input. These
development repairs await their own future release qualification.

## BibLaTeX and Biber receiving

The bounded [#122](https://github.com/uibcdf/ackredit/issues/122) checkpoint reads
the same six-record attribution with normally installed development Ackredit,
**BibLaTeX 3.19 / Biber 2.19**, pdfTeX 1.40.25 and the standard `authoryear` and
`numeric` styles. Both styles compile. Biber's tool-mode XML and manuscript BBL
retain all six citation keys, both software versions and the dataset version,
indivisible institutional names and declared editor prefix/suffix parts.
The original attribution and exported BibTeX bytes remain unchanged; export
creates no new execution credit. The
[receiving receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/receipts/biblatex_receiving_122_2026-10-06.json)
identifies the installed file, official tool archives, actual loaded TeX files,
reader output and presentation separately.

Both selected styles display versions 1.0, 2.0 and 2024.1, unlike `plain.bst`.
They print the generic record's editors but omit its publisher, although Biber
retains that field. The preferred collection stays a book with its own metadata.
Name order and line breaking vary by style; extracted PDF text includes
discretionary line-break hyphens. The original full-URL DOI is retained in
BibTeX/Biber rather than rewritten to apply CSL's presentation rule.

Biber warns that the fixture's synthetic ISBN `978-0-00-000000-0` is invalid.
The warning is retained and the original claim is not repaired. Compilation is
therefore not a clean metadata-validation certificate. This is a Linux/Python
3.14.8 study of those exact tools/styles, not a journal or manager qualification.
The host's LaTeX 2023 kernel cannot run downloaded BibLaTeX 3.22a: its initial
TeX pass fails on `\IfDocumentMetadataT`. The tested older pair is deliberately
isolated; compatibility with the latest pair is unqualified.

## Presentation boundaries

| Boundary | Observed behavior |
| --- | --- |
| Generated software/dataset BibTeX | Uses `@misc` with `howpublished = {Software}` or `{Dataset}`. `plain.bst` prints that description. |
| Version and DOI in BibTeX | Remain in the export and Pandoc's BibTeX reader. `plain.bst` does not print them. Two releases remain separate entries. |
| Editors on an untyped `other` record | Export retains `editor`; `plain.bst`'s `@misc` layout does not print it. A declared CFF book supplies a book layout without guessing its kind. |
| Imported `@software` | Export keeps the type. A real `plain.bst` run warns that it is undefined and falls back; this is not qualified software styling. |
| CSL-JSON and citeproc | Keeps software/dataset/book kinds; the selected Chicago style prints versions and DOI links in the fixture. |
| DOI stored as a full URL | #120 retained the duplicate-prefix defect. Development #121 strips supported wrappers only for presentation; saved originals and BibTeX remain intact. Ambiguous URL forms remain outside that projection. |
| Capitalization, particles and sorting | Engines/styles can change displayed capitalization and name order. Converted or formatted text is not an exact copy of the original. |

This does not establish Zotero, Mendeley or EndNote imports, general BibLaTeX/Biber
compatibility, arbitrary Unicode with every TeX engine, or journal-style coverage.
Reference-manager imports and other styles remain open roadmap work; duplicate
identity follows the explicit ID/original-record policy above.
Distinct IDs and different software releases are not silently combined because
their DOIs resemble one another. Other presentation can use an external style
engine or the [format extension point](reporting.md#adding-your-own-format).

## Reproducing the probe

With the external engines available, the repository tool reads a saved result and
writes exports, styles, converted records, formatted bibliography, PDF, local
process output and a receipt to a **new** directory:

```bash
python /path/to/ackredit/devtools/check_publication_tools.py \
  --attribution /path/to/result.json --output /tmp/publication-probe
```

Run outside the producing checkout with the intended Ackredit installation.
Engine failures propagate; BibTeX warnings are retained and prior evidence is
never replaced. The original input and current execution credits must remain
unchanged. Review warnings and rendered output as well as process status.
[Pandoc's citation documentation](https://pandoc.org/MANUAL.html#citations)
describes its bibliography/style interface. These remain optional external tools.

The designated local regression executes all optional receiving cases:

```bash
python -m pytest --receptor=llm --require-publication-tools tests/test_publication_tools.py
```

Ordinary environments without the tools skip external cases; this designated
command fails on missing tools. Portable export assertions still run.

For the separate BibLaTeX receiving route, make `biber`, `kpsewhich`, `pdflatex`
and `pdftotext` available, with TeX able to locate the selected BibLaTeX package:

```bash
python /path/to/ackredit/devtools/check_biblatex.py \
  --attribution /path/to/result.json --output /tmp/biblatex-probe \
  --style authoryear
```

`--style numeric` selects the other tested standard style. The probe installs
nothing and never falls back to a different route; `TEXINPUTS` may point to an
isolated compatible TeX tree. Official distributions and documentation belong to
[BibLaTeX](https://ctan.org/pkg/biblatex) and [Biber](https://ctan.org/pkg/biber).
The receipt records the exact historical official downloads used for #122.

The designated local regression executes both selected styles:

```bash
python -m pytest --receptor=llm --require-biblatex-tools tests/test_biblatex_receiving.py
```

Missing tools cause this designated command to fail. Ordinary CI does not install
the external engines and may skip these two real-tool cases; the retained reader
and receipt guards still execute. Publication probes share a process capture
helper that preserves exact stdout/stderr bytes and exit status, rendering
undecodable bytes as explicit escapes. Local raw streams remain available for
diagnosis.
