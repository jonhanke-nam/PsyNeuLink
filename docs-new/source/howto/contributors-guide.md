# Contributors guide

Thank you for your interest in contributing to PsyNeuLink! This page compiles
helpful information for new contributors that may not be covered in the user
documentation.

## File structure

The most relevant directories and files in the repository:

- **`psyneulink/`** -- the source code of PsyNeuLink.

  Within this directory, the `library/` folder contains non-core objects
  (custom Mechanisms, Projections, etc.), while the other folders hold the
  core framework. Custom components belong in `library/`.

- **`docs/`** -- the legacy Sphinx/RST documentation files.

  - `source/` -- Sphinx source files used to generate HTML documentation.
  - `build/` -- generated HTML output (not committed to the repository).

- **`docs-new/`** -- the modernized MyST Markdown documentation site.

  - `source/` -- Sphinx + MyST source files.
  - `Makefile` -- build targets for the new documentation (see below).

- **`tests/`** -- the test suite, actively maintained.

- **`CONVENTIONS.md`** -- coding conventions that contributors must follow
  (documentation style, variable naming, etc.).

## Environment setup

PsyNeuLink is written in Python 3 and requires Python 3.9 or later.

### 1. Clone the repository

```bash
git clone https://github.com/PrincetonUniversity/PsyNeuLink.git
cd PsyNeuLink
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

This installs PsyNeuLink in editable mode along with all development
dependencies (pytest, sphinx, linters, etc.). Alternatively:

```bash
pip install -r requirements.txt
pip install -r dev_requirements.txt
```

### 4. Verify the setup

```bash
pytest tests/ -x --timeout=60
```

## Building documentation

The documentation site under `docs-new/` uses a Makefile with these targets:

| Target      | Description                                     |
|-------------|-------------------------------------------------|
| `make html`     | Build HTML docs into `build/html/`          |
| `make livehtml` | Build and serve with auto-reload on changes |
| `make clean`    | Remove build artifacts                      |

```bash
cd docs-new
make html
# Open build/html/index.html in your browser
```

:::{note}
Do not commit built HTML files to the repository. They are for local
preview only.
:::

The legacy documentation under `docs/` can still be built with
`make html` from within that directory, but new documentation work should
target `docs-new/`.

## Contribution checklist

This is the general workflow for contributing:

1. **Create a branch** off of the `devel` branch:

   ```bash
   git checkout devel
   git pull origin devel
   git checkout -b my-feature
   ```

2. **Make your changes.** Ideally, notify the PsyNeuLink team in advance of
   what you intend to do so they can provide relevant guidance.

   :::{tip}
   Keep pulling from `devel` periodically while working on your branch.
   PsyNeuLink is under active development and substantial changes are still
   being made.
   :::

3. **Add tests** that verify your feature or bugfix works as expected. This
   protects your code from being accidentally broken by future changes.

4. **Run the test suite** and confirm all tests pass:

   ```bash
   pytest tests/
   ```

   If you encounter unexpected failures, notify the PsyNeuLink team.

5. **Submit a pull request** to the `devel` branch. The team will review your
   changes.

The `devel` branch is periodically merged into `master`, which is the branch
most users install from.

## Components overview

Most PsyNeuLink objects are {class}`Component` subclasses. All {class}`Function`,
{class}`Mechanism`, {class}`Projection`, and {class}`Port` types inherit from
Component and share common initialization and execution patterns.

### Overriding Component methods

Subclasses override Component methods to implement their own functionality.
**Every override must call `super()`** with the same arguments. For example,
to instantiate a Projection's receiver after its function is instantiated:

```python
class Projection_Base(Projection):
    def _instantiate_attributes_after_function(self, context=None):
        self._instantiate_receiver(context=context)
        super()._instantiate_attributes_after_function(context=context)
```

### The `context` argument

`context` is a string argument passed among PsyNeuLink functions to provide
information about when and why a function is being called. If you modify
`context`, you should **append** to it rather than overwriting it.

## Compositions overview

A {class}`Composition` combines {class}`Mechanism` and {class}`Projection`
objects into a graph. The graph's nodes are Mechanisms (or nested
Compositions) and edges are Projections. Execution order is determined by the
graph topology and can be customized using {class}`Condition` objects assigned
to the Composition's {class}`Scheduler`.

## Scheduler

When a Composition is run, its {class}`Scheduler` controls the execution of
its components. By default, each node executes once per pass in topological
order. You can assign {class}`Condition` objects to customize execution timing
-- for example, making one mechanism wait until another has executed a certain
number of times, or until a convergence criterion is met.

## Testing

PsyNeuLink uses [pytest](https://docs.pytest.org/en/latest/index.html) for
testing. Tests live in the `tests/` directory and are organized by component
type.

Run the full suite:

```bash
pytest tests/
```

Run a specific test file:

```bash
pytest tests/mechanisms/test_transfer_mechanism.py
```

Run tests matching a keyword:

```bash
pytest tests/ -k "stroop"
```

## Documentation conventions

Documentation is built with [Sphinx](https://www.sphinx-doc.org/) using the
[MyST Markdown](https://myst-parser.readthedocs.io/) parser (for `docs-new/`)
or reStructuredText (for the legacy `docs/`).

- Online documentation for `master` is at
  [https://princetonuniversity.github.io/PsyNeuLink/](https://princetonuniversity.github.io/PsyNeuLink/)
- Online documentation for `devel` is at
  [https://princetonuniversity.github.io/PsyNeuLink/branch/devel/index.html](https://princetonuniversity.github.io/PsyNeuLink/branch/devel/index.html)

When editing documentation, generate a local build to preview your changes
before pushing. See the "Building documentation" section above.

To understand Sphinx syntax, start with the
[reStructuredText primer](http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
or the [MyST Markdown guide](https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html).
