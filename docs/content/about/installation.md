(About_Installation)=
# Installation

Ackredit depends only on the MolSysSuite infrastructure components, `smonitor` and
`depdigest`. Both are pure Python and are distributed through the `uibcdf` conda channel.

## From source

Ackredit is not published yet, so this is the way to install it today:

```bash
git clone https://github.com/uibcdf/ackredit.git
cd ackredit
conda env create -f devtools/conda-envs/development_env.yaml -n ackredit
conda activate ackredit
pip install --no-deps -e .
```

The environment file brings the suite dependencies from the `uibcdf` channel. `--no-deps`
keeps pip from trying to resolve them again from PyPI, where they are not published.

## Once released

```bash
conda install -c uibcdf ackredit
```

## Extra features

The core reporting works without any of these; each one unlocks a single optional
feature. Ask what the current environment supports with `ackredit.dependency_info()`.

| Feature | Needs | Install |
| --- | --- | --- |
| Interactive dashboard, `serve_ui()` | `flask` | `conda install -c conda-forge flask` |
| DueCredit bridge, `export_to_duecredit()` | `duecredit` | `conda install -c conda-forge duecredit` |

## System requirements (optional)

The automatic **PDF compilation** in `dump(build_pdf=True)` shells out to `pdflatex` and
`bibtex`, which are system binaries rather than Python packages:

*   **Linux:** `sudo apt install texlive-latex-extra` (or similar)
*   **macOS:** [MacTeX](https://tug.org/mactex/)
*   **Windows:** [MiKTeX](https://miktex.org/)

Without them the LaTeX and BibTeX files are still written, and Ackredit reports that the
PDF step was skipped.
