# PsyNeuLink Documentation

*A block modeling environment for computational neuroscience and psychology*

PsyNeuLink is an open-source Python framework for building models of the
relationship between brain function, mental processes, and behavior. It lets
you construct, simulate, document, and share computational models at the
subsystem and system level.

::::{grid} 2
:gutter: 3

:::{grid-item-card} Tutorials
:link: tutorials/index
:link-type: doc

Step-by-step guides for learning PsyNeuLink from scratch.
Start here if you are new.
:::

:::{grid-item-card} How-To Guides
:link: howto/index
:link-type: doc

Practical recipes for common tasks: building models, running
simulations, fitting parameters, and more.
:::

:::{grid-item-card} API Reference
:link: reference/index
:link-type: doc

Complete reference for all PsyNeuLink classes, functions, and
modules. Auto-generated from source code.
:::

:::{grid-item-card} Explanation
:link: explanation/index
:link-type: doc

In-depth discussion of PsyNeuLink's architecture, design decisions,
and the computational concepts it implements.
:::

::::

## Quick install

```bash
pip install psyneulink
```

Or for local development (see {doc}`howto/installation`):

```bash
git clone https://github.com/PrincetonUniversity/PsyNeuLink.git
cd PsyNeuLink
make install
```

## Hello, PsyNeuLink

```python
import psyneulink as pnl

# Create two processing layers
input_layer = pnl.TransferMechanism(name='input', function=pnl.Linear)
output_layer = pnl.TransferMechanism(name='output', function=pnl.Logistic)

# Connect them in a composition
model = pnl.Composition(name='my_model')
model.add_linear_processing_pathway([input_layer, output_layer])

# Run
result = model.run(inputs={input_layer: [1.0]})
print(result)  # [[0.73105858]]
```

## What PsyNeuLink is for

PsyNeuLink is designed for building models that integrate different levels of
analysis — from neural populations to cognitive functions to behavior:

- **Subsystem and system-level models** of brain function and behavior
- **Integrating disparate components** (neural networks, decision processes,
  control mechanisms) into a unified simulation
- **Documenting and sharing** models in a standard, executable format
- **Exploring interactions** between processes at different time scales

For large-scale deep learning, use PyTorch or TensorFlow directly (PsyNeuLink
can wrap PyTorch models via `AutodiffComposition`). For detailed biophysical
neuron models, see NEURON or Nengo.

```{toctree}
:maxdepth: 2
:hidden:

tutorials/index
howto/index
reference/index
explanation/index
```
