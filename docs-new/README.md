# PsyNeuLink Documentation (New)

This is the modernized version of the PsyNeuLink documentation. The original
docs remain in `docs/` and are unmodified.

## What's different

| Aspect | `docs/` (original) | `docs-new/` (this) |
|--------|--------------------|--------------------|
| **Theme** | Custom `psyneulink_sphinx_theme` | PyData Sphinx Theme |
| **Organization** | Flat list of RST files | Diátaxis: tutorials, how-to, reference, explanation |
| **Landing page** | Text-heavy welcome page | Card grid with clear entry points |
| **Cross-references** | Internal only | + intersphinx (NumPy, SciPy, PyTorch, Python) |
| **Code examples** | Inline RST blocks | Copy button, syntax highlighting |
| **API docs** | Same autodoc approach | Same autodoc approach |

## Organization (Diátaxis framework)

- **Tutorials** (`tutorials/`) -- Learning-oriented, step-by-step guides
- **How-To Guides** (`howto/`) -- Task-oriented recipes for specific goals
- **API Reference** (`reference/`) -- Auto-generated from source docstrings
- **Explanation** (`explanation/`) -- Understanding-oriented discussion

## Building

```bash
# Install doc dependencies
pip install -r requirements.txt

# Build HTML
make html

# Or with live-reload during development
make livehtml
```

The built docs will be in `build/html/`. Open `build/html/index.html` to view.

## Status

This is a scaffolding commit. Currently:
- Landing page and section structure are complete
- Getting Started tutorial is fully written
- Installation how-to guide is fully written
- Architecture explanation is fully written
- API reference pages use the same autodoc directives as the original docs
- Most tutorial, how-to, and explanation pages are placeholders

Pages will be filled in incrementally as content is migrated and improved
from the original docs.

## Conventions

- Use `.. seealso::` to cross-reference between sections (e.g., tutorial
  links to reference, reference links back to tutorial)
- API reference pages should include a brief intro paragraph before the
  automodule directive
- Placeholder pages use `.. note::` blocks explaining what content is planned
- File names use lowercase with hyphens (e.g., `transfer-mechanism.rst`)
- Labels use the format `_ref-name` for reference pages, `_tutorial-name`
  for tutorials, `_howto-name` for how-to guides
