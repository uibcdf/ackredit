(About_Installation)=
# Installation

Ackredit has four runtime dependencies: three MolSysSuite infrastructure components,
`smonitor`, `depdigest` and `argdigest`, and `pyyaml`. The three suite components are
distributed through the `uibcdf` conda channel and not through PyPI.
Published ArgDigest 0.14.0 does not require NumPy for this core route; its scientific
extras can add it. The tree still includes compiled components: PyYAML and libyaml.
The clean Linux/Python 3.14 measurement adds six Conda packages, about 519 KiB of
compressed package payload and 2.52 MiB of recorded regular files to Python alone.
These exclude channel metadata and are logical file lengths, not physical disk
usage. See [the public installation measurement](performance.md#public-conda-installation-2026-10-06)
for exact versions, raw evidence and limits.

Ackredit **0.11.0** is available from the public `uibcdf` Conda channel. It retains
`Attribution`, `capture`, `get_attribution` and the portable
`ackredit.attribution@1` contract first published in 0.9.0. Its metadata requires
Python 3.11–3.14. The same `noarch: python` archive was qualified on Linux x86-64
and macOS arm64 across all four Python minors before publication.

This checkpoint delivers the accepted stable `prepare_credit`, `observe_calls`
and `ackredit.provider@1` contracts: clients requiring that bounded promise use
`ackredit>=0.11.0`. Clients using only the portable contract can retain
`ackredit>=0.9.0`. Evidence representation, opt-in collection and integrated
reporting remain provisional. See [API stability](stability.md) and the
[release notes](release_notes.md). Earlier public 0.10.0/0.10.1 retain their
original provisional provider contracts.

## Install from Conda

Create an environment with Ackredit and its runtime dependencies:

```bash
conda create -n work --override-channels --strict-channel-priority -c uibcdf -c conda-forge python=3.14 ackredit=0.11.0=py_0
conda activate work
```

You can select Python 3.11, 3.12 or 3.13 instead. Conda resolves the dependencies
from `uibcdf` and `conda-forge`; no source checkout or staging channel is needed.
For an existing environment, use:

```bash
conda install --override-channels --strict-channel-priority -c uibcdf -c conda-forge ackredit=0.11.0=py_0
```

Check it arrived whole:

```python
import ackredit

ackredit.__version__  # '0.11.0'
ackredit.dependency_info()  # what optional features this environment supports
```

The published file is
[`ackredit-0.11.0-py_0.tar.bz2`](https://conda.anaconda.org/uibcdf/noarch/ackredit-0.11.0-py_0.tar.bz2),
with SHA-256:

```text
df8963ca2d286f50b19eb778e95c54c5ebb79c12fb55a6504e7c23daf5717d4f
```

The [installed matrix](https://github.com/uibcdf/ackredit/actions/runs/37429662858)
and [exact-file promotion](https://github.com/uibcdf/ackredit/actions/runs/37430816845)
retain the original artifact identity. A separate clean public-channel
installation on Linux/Python 3.14 verifies installed origins, packaged citation,
portable attribution, reference reuse, saved readers, CLI and dependency closure.
The [real PyUnitWizard matrix](https://github.com/uibcdf/ackredit/actions/runs/37429666506)
passes 72 mandatory tests without skips against the same Conda file across all
eight cells. These gates do not certify a consumer's own release. The
[delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.11.0_public_2026-10-06.json)
retains independently verified native artifacts, original identities and limits.
The [previous 0.10.1 receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json)
keeps its historical public Sabueso evidence separately.

## For working on Ackredit itself

Routine development uses Python 3.14. Maintained environments, package metadata,
the recipe and required full CI agree on Python 3.11–3.14. ArgDigest 0.13.0 is
the minimum dependency release carrying Python 3.14 support. Older immutable
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
