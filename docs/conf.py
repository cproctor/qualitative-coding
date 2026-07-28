# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Qualitative Coding'
copyright = '2024, Chris Proctor'
author = 'Chris Proctor'
release = '1.7.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
# Publishes docs/skills/SKILL.md verbatim to the site root (e.g.
# https://qualitative-coding.readthedocs.io/en/latest/SKILL.md), so it can be
# fetched directly as a Claude Code skill.
html_extra_path = ['skills']
html_logo = '../qc_lockup.v0.png'
html_theme_options = {
    'logo_only': True,
    'display_version': False,
}
