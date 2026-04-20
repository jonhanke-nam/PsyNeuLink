.. _howto-installation:

============
Installation
============

.. contents:: On this page
   :local:
   :depth: 2


From PyPI
=========

The simplest way to install PsyNeuLink:

.. code-block:: bash

   pip install psyneulink

This installs PsyNeuLink and all required dependencies.


From source (for development)
=============================

Clone the repository and use the provided Makefile:

.. code-block:: bash

   git clone https://github.com/PrincetonUniversity/PsyNeuLink.git
   cd PsyNeuLink
   make install

This creates a virtual environment in ``.venv/`` and installs PsyNeuLink
in editable mode. Activate it with:

.. code-block:: bash

   source .venv/bin/activate


Install targets
---------------

The Makefile provides several install targets:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Command
     - What it installs
   * - ``make install``
     - Core PsyNeuLink (editable)
   * - ``make install-dev``
     - Core + pytest, linting, coverage tools
   * - ``make install-tutorial``
     - Core + Jupyter and tutorial dependencies
   * - ``make install-all``
     - Everything above


Running notebooks
=================

.. code-block:: bash

   # Jupyter (opens in notebooks/ directory)
   make jupyter

   # Marimo (reactive notebooks)
   make marimo

   # Official PsyNeuLink tutorial
   make tutorial

See ``GETTING_STARTED.md`` in the repository root for full details.


System requirements
===================

- **Python**: 3.8 or later
- **OS**: macOS, Linux, Windows (via WSL recommended)
- **Optional**: `Graphviz <https://graphviz.org>`_ for model visualization


Troubleshooting
===============

**pip install fails with dependency conflicts**
   Try installing in a fresh virtual environment:

   .. code-block:: bash

      python3 -m venv .venv && source .venv/bin/activate
      pip install psyneulink

**ImportError after install**
   Make sure you activated the virtual environment where PsyNeuLink is
   installed.

**Graphviz errors with show_graph()**
   Install Graphviz separately (it is not a Python package):

   .. code-block:: bash

      # macOS
      brew install graphviz

      # Ubuntu/Debian
      sudo apt install graphviz

For additional help, email psyneulinkhelp@princeton.edu or
`file an issue <https://github.com/PrincetonUniversity/PsyNeuLink/issues>`_.
