(About_Citation)=
# Citation

If you use Ackredit in a scientific publication, please cite it as its `CITATION.cff`
asks. That file is the authoritative record and it ships inside the package, so Ackredit
also discovers itself: `ackredit.report()` includes this entry when Ackredit was used.

> Prada-Gracia, D., & Moreno-Vargas, L. M. *Ackredit: workflow-aware citation and
> acknowledgement tracking for scientific Python.* UIBCDF, 2026.

This page used to abbreviate the authors to "Prada, D. et al." for a work with exactly
two named authors, which hid one of them, and to give a different title and year from
`CITATION.cff`. `tests/test_self_citation.py` now checks this page against that file.
