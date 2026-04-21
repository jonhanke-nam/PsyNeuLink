(getting-started)=
# Getting Started with PsyNeuLink

This tutorial walks you through installing PsyNeuLink, understanding its core
concepts, and building your first model.

## Installation

Install PsyNeuLink from PyPI:

```bash
pip install psyneulink
```

To verify the installation, open a Python interpreter and import the library:

```python
import psyneulink as pnl
print(pnl.__version__)
```

If you plan to use GPU-accelerated learning with PyTorch integration, install
PyTorch separately following the instructions at <https://pytorch.org>.

## Core Concepts

PsyNeuLink models are built from three kinds of objects:

**Mechanisms** are the computational units ("blocks") of a model. A Mechanism
receives input, applies a {class}`Function` to transform it, and produces output.
There are two broad categories:

- {class}`ProcessingMechanism` -- transforms and transmits information directly
  (for example, a layer in a neural network or a decision process).
- {class}`ModulatoryMechanism` -- modifies or regulates the processing performed by
  other Mechanisms (for example, a {class}`ControlMechanism` that adjusts gain).

**Projections** are the connections ("links") between Mechanisms. A Projection
transmits the output of one Mechanism to the input of another. The most common type
is a {class}`MappingProjection`, which carries a weight matrix that determines how
values are mapped from sender to receiver.

**Compositions** assemble Mechanisms and Projections into an executable model.
A {class}`Composition` defines the computational graph -- Mechanisms are the nodes,
Projections are the directed edges. Compositions can be nested inside other
Compositions to build hierarchical models.

## Creating Your First Mechanism

A {class}`TransferMechanism` is the simplest kind of ProcessingMechanism. It takes
an input array, applies a transfer function, and produces an output:

```python
import psyneulink as pnl

# Create a mechanism with a 3-element input that uses a Logistic function
my_mech = pnl.TransferMechanism(
    name='my_mechanism',
    input_shapes=3,
    function=pnl.Logistic()
)

# Execute it standalone with a sample input
result = my_mech.execute([0.0, 1.0, 2.0])
print(result)
# Output: [[0.5, 0.73105858, 0.88079708]]
```

Key things to notice:

- `input_shapes=3` tells PsyNeuLink that this Mechanism expects a 1-d array of
  length 3 as its input.
- `function=pnl.Logistic()` assigns the logistic (sigmoid) function as the
  transfer function.
- Calling `execute()` runs the Mechanism once and returns the result. The output
  shape matches the input shape.

## Building a Simple Composition

Now let's connect three Mechanisms into a feedforward pathway and wrap them in a
Composition:

```python
import numpy as np
import psyneulink as pnl

# Create three processing layers
input_layer = pnl.ProcessingMechanism(input_shapes=5, name='Input')
hidden_layer = pnl.ProcessingMechanism(input_shapes=2, function=pnl.Logistic, name='Hidden')
output_layer = pnl.ProcessingMechanism(input_shapes=5, function=pnl.Logistic, name='Output')

# Assemble them into a Composition
my_network = pnl.Composition(
    pathways=[[input_layer, hidden_layer, output_layer]]
)
```

PsyNeuLink automatically creates {class}`MappingProjection` objects to connect each
pair of adjacent Mechanisms in the pathway. By default it uses full-connectivity
matrices (every element of the sender connects to every element of the receiver with
weight 1).

## Running the Composition

Call the {meth}`~Composition.run` method with an input array sized for the first
Mechanism in the pathway:

```python
result = my_network.run([1, 4.7, 3.2, 6, 2])
print(result)
# Output: [array([0.88079707, 0.88079707, 0.88079707, 0.88079707, 0.88079707])]
```

The result is the output of the last Mechanism in the pathway (the `output_layer`)
after a single trial of execution.

You can also run multiple trials by passing a list of inputs:

```python
results = my_network.run(
    inputs={input_layer: [[1, 0, 0, 0, 0],
                          [0, 1, 0, 0, 0],
                          [0, 0, 1, 0, 0]]}
)
print(my_network.results)
```

## Visualizing the Graph

Every Composition can display its computational graph using the
{meth}`~ShowGraph.show_graph` method:

```python
my_network.show_graph()
```

This opens a graphical representation of the model. `INPUT` nodes are colored
green, and `OUTPUT` nodes are colored red. This makes it easy to inspect the
structure of your model and verify that the connectivity is correct.

You can pass options to show additional detail:

```python
# Show the internal port structure of each Mechanism
my_network.show_graph(show_node_structure=True)
```

## Next Steps

Now that you can create Mechanisms, connect them in a Composition, run the model,
and visualize its graph, you are ready to explore the more detailed tutorials:

- {doc}`mechanisms-and-functions` -- deeper dive into Mechanism types and Functions
- {doc}`projections-and-pathways` -- specifying custom Projections and building pathways
- {doc}`compositions` -- advanced Composition features including nesting and scheduling
- {doc}`control` -- adding control and monitoring to your models
- {doc}`learning` -- training networks with backpropagation and AutodiffComposition
