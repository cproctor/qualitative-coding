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

.. _installation:

Installation
------------

Prerequisites
~~~~~~~~~~~~~

``qc`` runs on the command line (also called a shell or a terminal), so you will 
need to be familiar with using a command line in order to use ``qc``.

* `Python 3.9 <https://www.python.org/downloads/>`__ or higher.
* `Pandoc <https://pandoc.org/>`__. ``qc`` relies on Pandoc for converting between
  file formats.
* A code editor. You should install 
  `Visual Studio Code <https://code.visualstudio.com/>`__, the default
  editor, unless you prefer a different editor such as emacs or vim.
* The `Sync Scroll <https://marketplace.visualstudio.com/items?itemName=dqisme.sync-scroll>`__
  extension for Visual Studio Code.

Install with pip or pipx
~~~~~~~~~~~~~~~~~~~~~~~~

``qc`` is distributed via the Python Package Index (PYPI). If you want to
install ``qc`` globally on your system, the cleanest approach is to use
`pipx <https://pipx.pypa.io/stable/>`__.

.. note::

   The command below (and others throughout this documentation)
   is intended to be entered into a terminal. 
   The ``%`` character is the command prompt indicating that the
   terminal is ready for input; don't type it into your terminal.
   Don't worry if your terminal uses a different command prompt 
   such as ``$``.

.. code-block:: console

   % pipx install qualitative-coding

.. note::

   Some ``qc`` commands depend on a langauge model which is included
   as an optional dependency. If you wish to install the langauge 
   model, add ``--with models`` to the command above.


Install as a dependency
~~~~~~~~~~~~~~~~~~~~~~~

If your research project is already contained within a Python package
and you want to install ``qc`` as a local dependency, simply add
``qualitative-coding`` to ``pyproject.toml`` or ``requirements.txt``.

Stuck?
~~~~~~

If you get stuck installing ``qc``, feel free to email 
Chris Proctor (chrisp@buffalo.edu), the project lead.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   manuscript
