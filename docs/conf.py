# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'BehaveX'
copyright = '2024, hrcorval'
author = 'hrcorval'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

# The master toctree document.
master_doc = 'index'

# The suffix(es) of source filenames.
source_suffix = ['.rst', '.md']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'

# -- MyST Parser configuration -----------------------------------------------
myst_enable_extensions = [
    "colon_fence",
]
