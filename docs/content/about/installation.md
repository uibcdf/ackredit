(About_Installation)=
# Installation

Ackredit has four runtime dependencies: three MolSysSuite infrastructure components,
`smonitor`, `depdigest` and `argdigest`, and `pyyaml`. The three suite components are
distributed through the `uibcdf` conda channel and not through PyPI.
Published ArgDigest 0.15.0 does not require NumPy for this core route; its scientific
extras can add it. The tree still includes compiled components: PyYAML and libyaml.
The separately recorded historical Linux/Python 3.14 measurement adds six Conda packages, about 526 KiB of
compressed package payload and 2.59 MiB of recorded regular files to Python alone.
These exclude channel metadata and are logical file lengths, not physical disk
usage. See [the public installation measurement](performance.md#published-diagnostic-providers-2026-10-06)
for exact versions, raw evidence and limits.

Ackredit **0.12.2** is available from the public `uibcdf` Conda channel. It retains
`Attribution`, `capture`, `get_attribution` and the portable
`ackredit.attribution@1` contract first published in 0.9.0. Its metadata requires
Python 3.11–3.14. The same `noarch: python` archive was qualified on Linux x86-64
and macOS arm64 across all four Python minors before publication.

This maintenance release preserves the accepted stable `prepare_credit`, `observe_calls`
and `ackredit.provider@1` contracts: clients requiring that bounded promise use
`ackredit>=0.11.0`. Clients using only the portable contract can retain
`ackredit>=0.9.0`. Clients requiring the bounded evidence representation, opt-in collection,
explicit integrated reporting or standalone validator use `ackredit>=0.12.0`.
Public 0.11.0 retains its original provisional evidence classification and lacks
the standalone validator. See [API stability](stability.md) and the
[release notes](release_notes.md). Earlier public 0.10.0/0.10.1 retain their
original provisional provider contracts.

## Install from Conda

Create an environment with Ackredit and its runtime dependencies:

```bash
conda create -n work --override-channels --strict-channel-priority -c uibcdf -c conda-forge python=3.14 ackredit=0.12.2=py_1
conda activate work
```

You can select Python 3.11, 3.12 or 3.13 instead. Conda resolves the dependencies
from `uibcdf` and `conda-forge`; no source checkout or staging channel is needed.
For an existing environment, use:

```bash
conda install --override-channels --strict-channel-priority -c uibcdf -c conda-forge ackredit=0.12.2=py_1
```

Check it arrived whole:

```python
import ackredit

ackredit.__version__  # '0.12.2'
ackredit.dependency_info()  # what optional features this environment supports
```

The published file is
[`ackredit-0.12.2-py_1.tar.bz2`](https://conda.anaconda.org/uibcdf/noarch/ackredit-0.12.2-py_1.tar.bz2),
with SHA-256:

```text
ac3738d90d239a153d4f58221655e39bb793125091162e118428bdc0961bc510
```

The [installed matrix](https://github.com/uibcdf/ackredit/actions/runs/43142531629)
and [same-file promotion](https://github.com/uibcdf/ackredit/actions/runs/43143253907)
retain the original producer and archive identity. A fresh ordinary public-channel
Linux/Python 3.14.10 installation, with cache separate from staging and no Ackredit
before the solve, verifies origins, all 70 package files, SPDX and exact original
MIT notice, portable/provider/evidence contracts, reused references, saved readers,
actual optional absence, CLI and `pip check`. The code files are byte-identical
to public 0.12.1; only packaged self-citation and generated version differ.

The [real PyUnitWizard matrix](https://github.com/uibcdf/ackredit/actions/runs/43142535560)
passes 72 mandatory cases without skips across eight cells. All ten native
artifact digests/source bindings verify and the independently reconstructed
aggregate matches the hosted result. These gates do not certify every consumer
release. The [delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.12.2_public_2026-11-11.json)
retains actual versions, original identities, executed checks and limits.
The [GitHub release](https://github.com/uibcdf/ackredit/releases/tag/0.12.2) and tag
point to original producer `52e05baecef89043cc4220623fadc1ce1bd1f2f6`.

Build 1 is the qualified public file. The earlier staged `py_0` failed a test
that compared installed identity with pre-release checkout tags; it remains
immutable and unqualified. The correction retains rejection of stale packages
and repeats every source/installed/receiving gate for the new producer.

The [0.12.1 receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.12.1_public_2026-10-22.json)
retains its snapshot-scaling proof and original file. The
[0.12.0 receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.12.0_public_2026-10-07.json)
retains its separate BibTeX/Pandoc, two BibLaTeX/Biber styles and JabRef 5.15
qualification with fixture/tool warnings. This packaging maintenance release
makes no new manager/style or performance claim; see [performance](performance.md)
for the bounded historical measurements.
The [previous 0.10.1 receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json)
keeps its historical public Sabueso evidence separately.

## For working on Ackredit itself

Routine development uses Python 3.14. Maintained environments, package metadata,
the recipe and required full CI agree on Python 3.11–3.14. Ackredit now requires
ArgDigest >=0.15.0 for its corrected import without NumPy. Source builds require
Setuptools >=77.0.3; maintained build/test environments declare it explicitly. Older immutable
Ackredit tags keep their original range.

```bash
git clone https://github.com/uibcdf/ackredit.git
cd ackredit
conda env create -f devtools/conda-envs/development_env.yaml -n ackredit
conda activate ackredit
pip install --no-deps --editable .
```

An editable install reports a development version derived from the latest tag, which says
how far past the tag it is. It is not the release, and it is not meant to be cited as one.

For an installed-package check, create the test environment with the interpreter
you want to qualify, build a wheel, and install that wheel with `pip install
--no-deps`. Run `devtools/installed_smoke.py` from outside the checkout. It
rejects editable/source provider imports and checks packaged citation metadata,
portable attribution, reused workflow references and saved-reader behavior.

## Extra features

The core reporting works without any of these; each one unlocks a single optional
feature. Ask what the current environment supports with `ackredit.dependency_info()`.

| Feature | Needs | Install |
| --- | --- | --- |
| DueCredit bridge, `export_to_duecredit()` | `duecredit` | `conda install -c conda-forge duecredit` |

## System requirements (optional)

The automatic **PDF compilation** in `dump(build_pdf=True)` shells out to `pdflatex` and
`bibtex`, which are system binaries rather than Python packages:

*   **Linux:** `sudo apt install texlive-latex-extra` (or similar)
*   **macOS:** [MacTeX](https://tug.org/mactex/)
*   **Windows:** [MiKTeX](https://miktex.org/)

Without them the LaTeX and BibTeX files are still written, and Ackredit reports that the
PDF step was skipped.
