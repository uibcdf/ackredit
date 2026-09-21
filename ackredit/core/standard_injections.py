"""Citation metadata Ackredit injects for packages it knows.

**Every field here is transcribed from the work's own record, never written from
memory.** The three papers come from Crossref, by DOI; the MolSysSuite entries
come from each library's own `CITATION.cff`, or, where it ships none, from the
authorship its `pyproject.toml` declares. A citation library that invents a
detail is worse than one that has none, because the detail is carried into a
manuscript.

Author lists are complete, and a truncation is never written as a name. Half the
entries here once listed `"et al."` as an author, which BibTeX reads as a person
surnamed "al." with the given name "et", so a bibliography credited "E. al.".
Abbreviating a long list is a rendering decision and belongs to the style that
renders it, not to the data. `tests/test_standard_injections.py` enforces this.

SciPy's record lists 34 named authors followed by the collective author "SciPy
1.0 Contributors", and then that collective expanded into its 77 members. The
list kept here ends at the collective, which is the paper's author list as the
publisher records it; where it ends is read from the record, not chosen.

These entries exist for packages whose citation cannot be discovered at runtime.
When a package ships a `CITATION.cff`, that file is authoritative and what is
kept here is only a fallback for when it cannot be read.
"""

from __future__ import annotations

# Dictionary of standard injections for the scientific ecosystem.
# format: package_name -> [list of items (dict)]
STANDARD_INJECTIONS = {
    "numpy": [
        {
            "id": "numpy:paper:2020",
            "type": "article",
            "title": "Array programming with NumPy",
            "authors": [
                "Harris, Charles R.",
                "Millman, K. Jarrod",
                "van der Walt, Stéfan J.",
                "Gommers, Ralf",
                "Virtanen, Pauli",
                "Cournapeau, David",
                "Wieser, Eric",
                "Taylor, Julian",
                "Berg, Sebastian",
                "Smith, Nathaniel J.",
                "Kern, Robert",
                "Picus, Matti",
                "Hoyer, Stephan",
                "van Kerkwijk, Marten H.",
                "Brett, Matthew",
                "Haldane, Allan",
                "del Río, Jaime Fernández",
                "Wiebe, Mark",
                "Peterson, Pearu",
                "Gérard-Marchant, Pierre",
                "Sheppard, Kevin",
                "Reddy, Tyler",
                "Weckesser, Warren",
                "Abbasi, Hameer",
                "Gohlke, Christoph",
                "Oliphant, Travis E.",
            ],
            "year": 2020,
            "doi": "10.1038/s41586-020-2649-2",
            "journal": "Nature",
        }
    ],
    "scipy": [
        {
            "id": "scipy:paper:2020",
            "type": "article",
            "title": "SciPy 1.0: fundamental algorithms for scientific computing in Python",
            "authors": [
                "Virtanen, Pauli",
                "Gommers, Ralf",
                "Oliphant, Travis E.",
                "Haberland, Matt",
                "Reddy, Tyler",
                "Cournapeau, David",
                "Burovski, Evgeni",
                "Peterson, Pearu",
                "Weckesser, Warren",
                "Bright, Jonathan",
                "van der Walt, Stéfan J.",
                "Brett, Matthew",
                "Wilson, Joshua",
                "Millman, K. Jarrod",
                "Mayorov, Nikolay",
                "Nelson, Andrew R. J.",
                "Jones, Eric",
                "Kern, Robert",
                "Larson, Eric",
                "Carey, C J",
                "Polat, İlhan",
                "Feng, Yu",
                "Moore, Eric W.",
                "VanderPlas, Jake",
                "Laxalde, Denis",
                "Perktold, Josef",
                "Cimrman, Robert",
                "Henriksen, Ian",
                "Quintero, E. A.",
                "Harris, Charles R.",
                "Archibald, Anne M.",
                "Ribeiro, Antônio H.",
                "Pedregosa, Fabian",
                "van Mulbregt, Paul",
                "SciPy 1.0 Contributors",
            ],
            "year": 2020,
            "doi": "10.1038/s41592-019-0686-2",
            "journal": "Nature Methods",
        }
    ],
    "matplotlib": [
        {
            "id": "matplotlib:paper:2007",
            "type": "article",
            "title": "Matplotlib: A 2D Graphics Environment",
            "authors": [
                "Hunter, John D.",
            ],
            "year": 2007,
            "doi": "10.1109/MCSE.2007.55",
            "journal": "Computing in Science & Engineering",
        }
    ],
    # MolSysSuite standard injections. Each is what the library's own
    # CITATION.cff asks for; PyUnitWizard ships none, so its entry carries the
    # authorship its pyproject.toml declares and nothing more.
    "pyunitwizard": [
        {
            "id": "pyunitwizard:github",
            "type": "software",
            "title": "PyUnitWizard",
            "authors": ["UIBCDF Lab"],
            "url": "https://github.com/uibcdf/pyunitwizard",
        }
    ],
    "argdigest": [
        {
            "id": "argdigest:github",
            "type": "software",
            "title": "ArgDigest",
            "authors": ["Prada-Gracia, Diego", "Moreno-Vargas, Liliana M."],
            "url": "https://github.com/uibcdf/argdigest",
        }
    ],
    "molsysmt": [
        {
            "id": "molsysmt:software",
            "type": "software",
            "title": "MolSysMT",
            "authors": ["Prada-Gracia, Diego", "Moreno-Vargas, Liliana M."],
            "doi": "10.5281/zenodo.1298752",
            "url": "https://github.com/uibcdf/molsysmt",
        }
    ],
}
