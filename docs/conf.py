project = "Ackredit"
author = "UIBCDF Development Team"
copyright = "2025, UIBCDF"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
]
templates_path = ["_templates"]
exclude_patterns = []
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
myst_enable_extensions = [
    "colon_fence",
    "dollarmath",
    "deflist",
    "linkify",
]
