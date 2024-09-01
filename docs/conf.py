"""Configure Sphinx configuration."""

import os
import sys
from typing import Any
from datetime import datetime

# Insert the parent directory into the path
sys.path.insert(0, os.path.abspath(".."))

extensions = [
    "myst_parser",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
]
source_suffix = ".md"
master_doc = "index"

project = "cpi"
year = datetime.now().year
copyright = f"{year} palewire"

exclude_patterns = ["_build"]

html_theme = "palewire"
html_sidebars: dict[Any, Any] = {}
html_theme_options: dict[str, Any] = {
    "canonical_url": f"https://palewi.re/docs/{project}/",
    "nosidebar": True,
}
