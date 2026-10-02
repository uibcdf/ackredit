(About_Installation)=
# Installation

Ackredit has four runtime dependencies: three MolSysSuite infrastructure components,
`smonitor`, `depdigest` and `argdigest`, and `pyyaml`. The three suite components are
distributed through the `uibcdf` conda channel and not through PyPI. They are pure
Python, but the tree is not: ArgDigest requires `numpy`, which conda brings with it.

Ackredit is not on a package channel yet. That is a decision rather than an omission:
the API is still settling, and a published package is a commitment to what it contains.
Until the release before 1.0.0, **a Git tag is the release**, and installing one is two
commands.

## A released version

```bash
conda create -n work -c uibcdf -c conda-forge python=3.13 smonitor depdigest argdigest pyyaml pip
conda activate work
pip install --no-deps "git+https://github.com/uibcdf/ackredit@0.8.0"
```

The first command brings the suite dependencies from the `uibcdf` channel, which is where
they live; they are not on PyPI. `--no-deps` stops pip looking for them there.

Check it arrived whole:

```python
import ackredit

ackredit.__version__  # '0.8.0'
ackredit.dependency_info()  # what optional features this environment supports
```

## For working on Ackredit itself

The Python 3.14 adoption candidate targets Python 3.11–3.14 and installs
normally, without `--ignore-requires-python`. Its maintained environments and
required CI use the same range. ArgDigest 0.13.0 is the minimum release carrying
Python 3.14 support. Older immutable Ackredit tags keep their original range;
the `0.8.0` installation above remains a Python 3.11–3.13 example.

Source qualification and normal installation are tracked in
[Ackredit #80](https://github.com/uibcdf/ackredit/issues/80).
[MolSysSuite #29](https://github.com/uibcdf/molsyssuite/issues/29) owns transition
authorization and public admission. A development wheel does not establish a
public Conda release or a stable portable-API version.

```bash
git clone https://github.com/uibcdf/ackredit.git
cd ackredit
conda env create -f devtools/conda-envs/development_env.yaml -n ackredit
conda activate ackredit
pip install --no-deps -e .
```

An editable install reports a development version such as `0.8.0+3.gabc1234`, which says
how far past the tag it is. It is not the release, and it is not meant to be cited as one.

For an installed-package check, create the test environment with the interpreter
you want to qualify, build a wheel, and install that wheel with `pip install
--no-deps`. Run `devtools/installed_smoke.py` from outside the checkout. It
rejects editable/source provider imports and checks packaged citation metadata,
portable attribution, reused workflow references and saved-reader behavior.

## Once published

```bash
conda install -c uibcdf ackredit
```

This will work from the release before 1.0.0 onwards, and not before. The packaging is
built and verified — see `devtools/conda-build/README.md` — so what remains is the
decision to publish.

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
