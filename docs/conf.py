project = "Ackredit"
author = "UIBCDF Development Team"
copyright = "2025, UIBCDF"

# Extensions coming with Sphinx (named 'sphinx.ext.*') or custom ones.
# This list follows the shared MolSysSuite documentation setup.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "sphinx_copybutton",
    "sphinx_design",
    "myst_nb",
]

templates_path = ["_templates"]
# Sphinx scans the source directory, and MyST-NB writes its executed notebooks
# into `_build/jupyter_execute/`. Left in, the second build reads the first
# build's output as source and fails on duplicate labels, so a clean build
# passes and the next one does not.
exclude_patterns = ["_build", "**.ipynb_checkpoints"]
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]


# MyST-NB extensions and options

myst_enable_extensions = ["dollarmath", "amsmath", "deflist", "colon_fence"]

myst_heading_anchors = 3

# Notebooks are rendered as documentation, not executed during the build.
nb_execution_mode = "off"


# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "description"

# Don't show class signature with the class' name.
autodoc_class_signature = "mixed"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
