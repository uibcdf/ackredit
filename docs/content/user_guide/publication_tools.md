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

## Presentation boundaries

| Boundary | Observed behavior |
| --- | --- |
| Generated software/dataset BibTeX | Uses `@misc` with `howpublished = {Software}` or `{Dataset}`. `plain.bst` prints that description. |
| Version and DOI in BibTeX | Remain in the export and Pandoc's BibTeX reader. `plain.bst` does not print them. Two releases remain separate entries. |
| Editors on an untyped `other` record | Export retains `editor`; `plain.bst`'s `@misc` layout does not print it. A declared CFF book supplies a book layout without guessing its kind. |
| Imported `@software` | Export keeps the type. A real `plain.bst` run warns that it is undefined and falls back; this is not qualified software styling. |
| CSL-JSON and citeproc | Keeps software/dataset/book kinds; the selected Chicago style prints versions and DOI links in the fixture. |
| DOI stored as a full URL | Original text remains. The tested CSL style adds another DOI prefix, producing unsuitable presentation. Use a bare DOI for new declarations; no automatic normalization or duplicate merging is promised. |
| Capitalization, particles and sorting | Engines/styles can change displayed capitalization and name order. Converted or formatted text is not an exact copy of the original. |

This does not establish Zotero, Mendeley or EndNote imports, BibLaTeX/Biber
compatibility, arbitrary Unicode with every TeX engine, or journal-style coverage.
Reference-manager imports and duplicate identity remain open roadmap work.
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
