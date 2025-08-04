# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
project = 'BehaveX'
copyright = '2023, hrcorval'
author = 'hrcorval'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
    'autoapi.extension',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# The master toctree document.
master_doc = 'index'

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
templates_path = ['_templates']

# -- MyST Parser configuration -----------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
    "substitution",
    "linkify",
]

# -- AutoAPI configuration ---------------------------------------------------
autoapi_dirs = ['../behavex']
autoapi_type = 'python'
autoapi_template_dir = '_autoapi_templates'
autoapi_generate_api_docs = True
autoapi_add_toctree_entry = False  # We'll add it manually to control placement

# -- HTML output options ----------------------------------------------------
html_static_path = []
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True
