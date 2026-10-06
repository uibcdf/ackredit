(About_Installation)=
# Installation

Ackredit has four runtime dependencies: three MolSysSuite infrastructure components,
`smonitor`, `depdigest` and `argdigest`, and `pyyaml`. The three suite components are
distributed through the `uibcdf` conda channel and not through PyPI. They are pure
Python, but the tree is not: ArgDigest requires `numpy`, which conda brings with it.

Ackredit **0.10.1** is available from the public `uibcdf` Conda channel. It retains
`Attribution`, `capture`, `get_attribution` and the portable
`ackredit.attribution@1` contract first published in 0.9.0. Its metadata requires
Python 3.11–3.14. The same `noarch: python` archive was qualified on Linux x86-64
and macOS arm64 across all four Python minors before publication.

This checkpoint also ships provisional function-provider observation, prepared
contextual credits and the offline `workflow` report. See the
[release notes](release_notes.md) for their scope and the additive self-citation
repair. A client using only the released portable contract can retain its
`ackredit>=0.9.0` minimum. The stable-provider decision is accepted in source;
0.11.0 is the candidate under [#107](https://github.com/uibcdf/ackredit/issues/107),
with its exact-file qualification/public delivery still pending. Public 0.10.1
retains its original provisional provider contract.

## Install from Conda

Create an environment with Ackredit and its runtime dependencies:

```bash
conda create -n work --override-channels --strict-channel-priority -c uibcdf -c conda-forge python=3.14 ackredit=0.10.1=py_0
conda activate work
```

You can select Python 3.11, 3.12 or 3.13 instead. Conda resolves the dependencies
from `uibcdf` and `conda-forge`; no source checkout or staging channel is needed.
For an existing environment, use:

```bash
conda install --override-channels --strict-channel-priority -c uibcdf -c conda-forge ackredit=0.10.1=py_0
```

Check it arrived whole:

```python
import ackredit

ackredit.__version__  # '0.10.1'
ackredit.dependency_info()  # what optional features this environment supports
```

The published file is
[`ackredit-0.10.1-py_0.tar.bz2`](https://conda.anaconda.org/uibcdf/noarch/ackredit-0.10.1-py_0.tar.bz2),
with SHA-256:

```text
26e75a0780ad4e6abc2de55df90b29b4a2aa4e510d6b50fa54a5812ad929228e
```

The [installed matrix](https://github.com/uibcdf/ackredit/actions/runs/37268949725)
and [exact-file promotion](https://github.com/uibcdf/ackredit/actions/runs/37269544505)
retain the original artifact identity. A separate clean public-channel
installation on Linux/Python 3.14 verifies installed origins, packaged citation,
portable attribution, reference reuse, saved readers, CLI and dependency closure.
The [real PyUnitWizard matrix](https://github.com/uibcdf/ackredit/actions/runs/37268949118)
passes 48 mandatory tests against the same Conda file across all eight cells.
Public Sabueso 0.12.0 passes its 56 receiving tests and offline attribution
example in the clean public Python 3.14 environment. The
[delivery receipt](https://github.com/uibcdf/ackredit/blob/main/devtools/conda-build/receipts/ackredit_0.10.1_public_2026-10-05.json)
retains these independently bounded claims and exact identities.

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
