# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
sys.path.insert(0, os.path.abspath("../../../packages/server"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "lmms-server"
author = "lmms-lean-runner"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static", "../../../docs/assets"]
html_logo = "../../../docs/assets/logo/logo-wt.webp"
html_favicon = "../../../docs/assets/logo/logo-wt.webp"

# Furo theme options for better logo handling
html_theme_options = {
    "light_logo": "logo/logo-wt.webp",
    "dark_logo": "logo/logo-wt-dark.webp",
}

# This is the critical setting for deploying to a subdirectory
html_baseurl = "/dev/docs/server/"


# -- Options for sphinx-pydantic -----------------------------------------
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_field_list_validators = False
