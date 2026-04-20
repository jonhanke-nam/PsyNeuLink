# PsyNeuLink Documentation (New) - Sphinx Configuration
#
# This is the modernized documentation build for PsyNeuLink.
# The original docs remain in docs/ and are unmodified.

import os
import sys

# Add project root so autodoc can find psyneulink
sys.path.insert(0, os.path.abspath('../../'))
# Enable the technical_note extension (shared with original docs)
sys.path.insert(0, os.path.abspath('../../docs/source/_ext'))

import psyneulink._version

# -- Project information -----------------------------------------------------

project = 'PsyNeuLink'
copyright = '2016-2026, Jonathan D. Cohen'
author = 'Jonathan D. Cohen'

release = psyneulink._version.get_versions()['version']
version = '.'.join(release.split('.')[:4])

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',
    'technical_note',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
exclude_patterns = ['_build']

# Cross-reference without explicit roles (same as original docs)
default_role = 'any'

# Autodoc settings (match original behavior)
autodoc_member_order = 'bysource'
autodoc_typehints = 'none'

# Napoleon settings for Google/NumPy docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

# Intersphinx: link to external project documentation
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'torch': ('https://pytorch.org/docs/stable/', None),
}

# Copy button: don't copy prompts
copybutton_prompt_text = r'>>> |\.\.\. |\$ '
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------------

html_theme = 'pydata_sphinx_theme'

html_theme_options = {
    'navigation_depth': 4,
    'show_toc_level': 2,
    'github_url': 'https://github.com/PrincetonUniversity/PsyNeuLink',
    'icon_links': [],
    'use_edit_page_button': False,
    'show_prev_next': True,
    'navbar_align': 'left',
    'header_links_before_dropdown': 6,
    'secondary_sidebar_items': ['page-toc', 'edit-this-page'],
    'pygments_light_style': 'default',
    'pygments_dark_style': 'monokai',
}

html_static_path = ['_static']
html_css_files = ['css/custom.css']
html_title = f'PsyNeuLink v{version}'
html_show_sourcelink = False

# -- Autodoc filtering (same as original docs) ------------------------------

from sphinx.ext.autodoc import between

def setup(app):
    # Exclude docstring sections marked with COMMENT tags
    app.connect('autodoc-process-docstring', between('^.*COMMENT.*$', exclude=True))
    return app
