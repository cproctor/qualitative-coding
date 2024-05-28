.. Qualitative Coding documentation master file, created by
   sphinx-quickstart on Tue May 28 09:51:22 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

`qc`: A tool for qualitative data analysis designed to support computational thinking
=====================================================================================

``qc`` is a free, open-source command-line-based tool for qualitative
data analysis designed to support computational thinking. In addition to
making qualitative data analysis process more efficient, computational
thinking can contribute to the richness of subjective interpretation.
Although numerous powerful software packages exist for qualitative data
analysis, they are generally designed to protect users from complexity
rather than providing affordances for engaging with complexity via
algorithms and data structures. 

Installation
------------

``qc`` is distributed via the Python Package Index (PYPI), and can be
installed on any POSIX system (Linux, Unix, Mac OS, or Windows Subsystem
for Linux) which has Python 3.9 or higher installed. If you want to
install ``qc`` globally on your system, the cleanest approach is to use
`pipx <https://pipx.pypa.io/stable/>`__.

::

   pipx install qualitative-coding

If your research project is already contained within a Python package
and you want to install ``qc`` as a local dependency, simply add
``qualitative-coding`` to ``pyproject.toml`` or ``requirements.txt``.

``qc`` relies on `Pandoc <https://pandoc.org/>`__ for converting between
file formats, so make sure that is installed as well. ``qc`` uses a text
editor for coding; you should install Visual Studio Code, the default
editor, unless you prefer a different editor such as emacs or vim.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   manuscript
