from __future__ import annotations

# Dictionary of standard injections for the scientific ecosystem.
# format: package_name -> [list of items (dict)]
STANDARD_INJECTIONS = {
    "numpy": [
        {
            "id": "numpy:paper:2020",
            "type": "article",
            "title": "Array programming with NumPy",
            "authors": ["Harris, C. R.", "et al."],
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
            "authors": ["Virtanen, P.", "et al."],
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
            "authors": ["Hunter, J. D."],
            "year": 2007,
            "doi": "10.1109/MCSE.2007.55",
            "journal": "Computing in Science & Engineering",
        }
    ],
    # MolSysSuite standard injections
    "pyunitwizard": [
        {
            "id": "pyunitwizard:github",
            "type": "repo",
            "title": "PyUnitWizard: A library to manage units of physical quantities",
            "authors": ["UIBCDF Development Team"],
            "url": "https://github.com/uibcdf/pyunitwizard",
        }
    ],
    "argdigest": [
        {
            "id": "argdigest:github",
            "type": "repo",
            "title": "ArgDigest: Argument validation for scientific Python",
            "authors": ["UIBCDF Development Team"],
            "url": "https://github.com/uibcdf/argdigest",
        }
    ],
    "molsysmt": [
        {
            "id": "molsysmt:paper:2024",
            "type": "article",
            "title": "MolSysMT: A modern tool for molecular systems analysis",
            "authors": ["Diego", "et al."],
            "year": 2024,
        }
    ],
}
