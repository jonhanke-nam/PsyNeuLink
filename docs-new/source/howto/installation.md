# Installation

This guide covers every way to install PsyNeuLink, from a quick `pip install`
to a full development setup using the project Makefile.

## System requirements

- **Python 3.9+** (3.11 recommended)
- **pip** (bundled with modern Python installers)
- **Operating system:** macOS, Linux, or Windows

Optional dependencies are pulled in automatically for most features. For LLVM
compilation you will also need:

- **llvmlite** (installed automatically with `pip install psyneulink`)

For PyTorch-based learning ({class}`AutodiffComposition`):

- **PyTorch 1.13+** -- install separately following the
  [PyTorch instructions](https://pytorch.org/get-started/locally/)

## Install from PyPI

The simplest path. This installs the latest release and all required
dependencies:

```bash
pip install psyneulink
```

To include optional dependencies for graphing and display:

```bash
pip install psyneulink[display]
```

:::{tip}
Use a virtual environment to avoid conflicts with other packages:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
pip install psyneulink
```
:::

## Install from source

Clone the repository and install in editable mode so that changes to the
source code are immediately reflected:

```bash
git clone https://github.com/PrincetonUniversity/PsyNeuLink.git
cd PsyNeuLink
pip install -e ".[dev]"
```

### Using the Makefile

The project provides a `docs-new/Makefile` for building the documentation site.
Common targets:

| Target      | Description                                         |
|-------------|-----------------------------------------------------|
| `html`      | Build HTML documentation into `build/html/`         |
| `livehtml`  | Build and serve with auto-reload on changes         |
| `clean`     | Remove build artifacts                              |

Example:

```bash
cd docs-new
make html
# Open build/html/index.html in your browser
```

### Development dependencies

If you are contributing code, install the development dependencies:

```bash
pip install -e ".[dev]"
# or equivalently:
pip install -r requirements.txt
pip install -r dev_requirements.txt
```

This gives you `pytest`, `sphinx`, linting tools, and everything needed to run
the test suite and build docs.

## Running notebooks

PsyNeuLink ships with example notebooks that can be run in several
environments.

### Jupyter

```bash
pip install jupyter
jupyter notebook
```

Navigate to the `Scripts/` or `tests/` directory and open any `.ipynb` file.

### Marimo

[Marimo](https://marimo.io/) is a reactive notebook environment for Python:

```bash
pip install marimo
marimo edit my_notebook.py
```

You can convert an existing Jupyter notebook to a Marimo notebook with:

```bash
marimo convert my_notebook.ipynb > my_notebook.py
```

### Google Colab

To use PsyNeuLink in [Google Colab](https://colab.research.google.com/), add
this cell to the top of your notebook:

```python
!pip install psyneulink
import psyneulink as pnl
```

:::{note}
Colab uses a pre-configured Python environment. If you need a specific
PsyNeuLink version, pin it: `!pip install psyneulink==0.x.y`.
:::

## Verifying the installation

After installation, verify that PsyNeuLink loads correctly:

```python
import psyneulink as pnl
print(pnl.__version__)
```

Run a minimal model to confirm everything works end-to-end:

```python
mech = pnl.TransferMechanism(name='test')
comp = pnl.Composition(pathways=[mech])
result = comp.run(inputs={mech: [1.0]})
print(result)  # [[1.0]]
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'psyneulink'`**
: Make sure you activated your virtual environment before running Python.
  Re-run `pip install psyneulink` inside the active environment.

**`ImportError: llvmlite`**
: The LLVM compilation backend requires `llvmlite`. It is installed
  automatically, but on some systems you may need to install LLVM system
  libraries first. On macOS: `brew install llvm`.

**`ImportError: torch`**
: PyTorch is an optional dependency. Install it separately following
  [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/).

**Graphviz errors when calling `show_graph()`**
: The {class}`ShowGraph` display engine requires the Graphviz system package.
  Install it with your system package manager:

  ```bash
  # macOS
  brew install graphviz
  # Ubuntu / Debian
  sudo apt-get install graphviz
  # Windows (via Chocolatey)
  choco install graphviz
  ```

**Tests fail after a fresh install**
: Make sure you installed the dev dependencies (`pip install -e ".[dev]"`) and
  that you are on a supported Python version (3.9+).  Run the test suite with:

  ```bash
  pytest tests/
  ```
