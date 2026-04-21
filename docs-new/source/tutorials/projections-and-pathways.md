(projections-and-pathways)=
# Projections and Pathways

This tutorial covers how Mechanisms are connected together: **Projections** transmit
information between Mechanisms, and **pathways** organize sequences of Mechanisms and
Projections into linear chains that can be added to a Composition.

## Projections

A {class}`Projection` is a directed connection from one Mechanism to another. It takes
the output of its {attr}`sender <Projection.sender>` and delivers it to the input of its
{attr}`receiver <Projection.receiver>`.

Projections come in two categories, mirroring the two categories of Mechanisms:

- **PathwayProjections** (most commonly {class}`MappingProjection`) transmit information
  between ProcessingMechanisms.
- **ModulatoryProjections** ({class}`ControlProjection`, {class}`LearningProjection`) carry
  modulatory signals that regulate parameters of other Components.

This tutorial focuses on MappingProjections. ModulatoryProjections are covered in the
{doc}`control` and {doc}`learning` tutorials.

## MappingProjections

A {class}`MappingProjection` connects the output of one Mechanism to the input of another.
It carries a {attr}`matrix <Projection_Base.matrix>` parameter that specifies the weights
mapping from sender to receiver.

### Automatic Creation

PsyNeuLink creates MappingProjections automatically when you list Mechanisms in a pathway.
By default, it uses a `FULL_CONNECTIVITY_MATRIX`, connecting every element of the sender's
output to every element of the receiver's input with weight 1:

```python
import psyneulink as pnl

input_layer = pnl.ProcessingMechanism(input_shapes=5, name='Input')
hidden_layer = pnl.ProcessingMechanism(input_shapes=2, function=pnl.Logistic, name='Hidden')
output_layer = pnl.ProcessingMechanism(input_shapes=5, function=pnl.Logistic, name='Output')

# PsyNeuLink automatically creates MappingProjections between adjacent Mechanisms
my_network = pnl.Composition(pathways=[[input_layer, hidden_layer, output_layer]])
```

In this example, PsyNeuLink creates:
- A 5x2 MappingProjection from `input_layer` to `hidden_layer`
- A 2x5 MappingProjection from `hidden_layer` to `output_layer`

### Explicit Creation

You can create a MappingProjection explicitly and specify its weight matrix:

```python
import numpy as np
import psyneulink as pnl

my_projection = pnl.MappingProjection(
    matrix=(.2 * np.random.rand(2, 5)) - .1
)
```

This creates a Projection with a 2x5 matrix of random weights between -0.1 and +0.1.

### Inserting Projections in Pathways

You can place a Projection between two Mechanisms in a pathway list to specify which
Projection connects them:

```python
input_layer = pnl.ProcessingMechanism(input_shapes=5, name='Input')
hidden_layer = pnl.ProcessingMechanism(input_shapes=2, function=pnl.Logistic, name='Hidden')
output_layer = pnl.ProcessingMechanism(input_shapes=5, function=pnl.Logistic, name='Output')

my_projection = pnl.MappingProjection(matrix=(.2 * np.random.rand(2, 5)) - .1)

my_network = pnl.Composition()
my_network.add_linear_processing_pathway(
    [input_layer, my_projection, hidden_layer, output_layer]
)
```

You can also insert a raw matrix directly -- PsyNeuLink will create a MappingProjection
from it:

```python
my_network.add_linear_processing_pathway(
    [input_layer, (.2 * np.random.rand(2, 5)) - .1, hidden_layer, output_layer]
)
```

### Specifying Sender and Receiver

When creating a Projection outside of a pathway list, you can explicitly specify its
sender and receiver:

```python
recurrent_projection = pnl.MappingProjection(
    sender=output_layer,
    receiver=hidden_layer
)
my_network.add_projection(recurrent_projection)
```

## Pathways

A **pathway** is an ordered list of Mechanisms (and optionally Projections and/or matrices)
that defines a linear chain of processing. PsyNeuLink uses pathways as the primary way
to build up the structure of a Composition.

### Simple Linear Pathways

The simplest pathway is a list of Mechanisms, with PsyNeuLink filling in the Projections:

```python
pathway = [input_layer, hidden_layer, output_layer]
```

### Pathways with Explicit Weights

Matrices or Projections can be interleaved between Mechanisms:

```python
input_to_hidden_wts = np.array([[2, -2], [-2, 2]])
hidden_to_output_wts = np.array([[2, -2], [-2, 2]])
pathway = [input_layer, input_to_hidden_wts, hidden_layer, hidden_to_output_wts, output_layer]
```

### Adding Pathways to a Composition

There are two main ways to add pathways to a Composition:

**Via the constructor:**

```python
comp = pnl.Composition(pathways=[[input_layer, hidden_layer, output_layer]])
```

**Via pathway addition methods:**

```python
comp = pnl.Composition()
comp.add_linear_processing_pathway([input_layer, hidden_layer, output_layer])
```

The {ref}`pathway addition methods <Composition_Pathway_Addition_Methods>` are preferred
for complex models, because they allow you to build up the graph incrementally by adding
one pathway at a time.

## Building Complex Models with Multiple Pathways

Real models typically have multiple pathways that converge, diverge, or share Mechanisms.
The Stroop model from the {doc}`basics-and-primer` is a good example. Here is a simplified
version showing the technique:

```python
import numpy as np
import psyneulink as pnl

# Shared output mechanism
output = pnl.ProcessingMechanism(name='OUTPUT', input_shapes=2, function=pnl.Logistic)

# Color naming pathway
color_input = pnl.ProcessingMechanism(name='COLOR INPUT', input_shapes=2)
color_hidden = pnl.ProcessingMechanism(name='COLOR HIDDEN', input_shapes=2,
                                        function=pnl.Logistic(bias=-4))
color_input_to_hidden_wts = np.array([[2, -2], [-2, 2]])
color_hidden_to_output_wts = np.array([[2, -2], [-2, 2]])
color_pathway = [color_input, color_input_to_hidden_wts, color_hidden,
                 color_hidden_to_output_wts, output]

# Word reading pathway (shares the same output mechanism)
word_input = pnl.ProcessingMechanism(name='WORD INPUT', input_shapes=2)
word_hidden = pnl.ProcessingMechanism(name='WORD HIDDEN', input_shapes=2,
                                       function=pnl.Logistic(bias=-4))
word_input_to_hidden_wts = np.array([[3, -3], [-3, 3]])
word_hidden_to_output_wts = np.array([[3, -3], [-3, 3]])
word_pathway = [word_input, word_input_to_hidden_wts, word_hidden,
                word_hidden_to_output_wts, output]

# Build the Composition
model = pnl.Composition(name='Two-Pathway Model')
model.add_linear_processing_pathway(color_pathway)
model.add_linear_processing_pathway(word_pathway)

model.show_graph()
```

The two pathways converge on the shared `output` Mechanism. PsyNeuLink recognizes that
`output` already exists in the graph and creates additional Projections to it rather
than duplicating it.

## Recurrent Projections

A recurrent (feedback) Projection sends the output of a Mechanism back to an earlier
Mechanism in the pathway. There are two ways to create one:

**By repeating a Mechanism in the pathway list:**

```python
# output_layer sends its output back to hidden_layer
comp.add_linear_processing_pathway([input_layer, hidden_layer, output_layer, hidden_layer])
```

**By explicitly creating and adding the Projection:**

```python
comp.add_linear_processing_pathway([input_layer, hidden_layer, output_layer])
recurrent_projection = pnl.MappingProjection(
    sender=output_layer,
    receiver=hidden_layer
)
comp.add_projection(recurrent_projection)
```

Both approaches produce the same result. The first is more concise; the second gives you
more control over the Projection's parameters (such as its weight matrix).

## Pathway Addition Methods

A Composition provides several methods for adding pathways, each designed for a specific
type of processing:

| Method | Purpose |
|--------|---------|
| {meth}`~Composition.add_linear_processing_pathway` | Add a chain of ProcessingMechanisms |
| {meth}`~Composition.add_backpropagation_learning_pathway` | Add a pathway with backpropagation learning |
| {meth}`~Composition.add_reinforcement_learning_pathway` | Add a pathway with reinforcement learning |
| {meth}`~Composition.add_td_learning_pathway` | Add a pathway with temporal-difference learning |
| {meth}`~Composition.add_nodes` | Add individual Mechanisms (not as a pathway) |
| {meth}`~Composition.add_projection` | Add a single Projection between existing nodes |

The learning pathway methods automatically create all the LearningMechanisms and
LearningProjections needed for the specified learning algorithm. See {doc}`learning` for
details.

## Next Steps

- {doc}`compositions` -- running and inspecting the models you build
- {doc}`control` -- adding control mechanisms to regulate processing
- {doc}`learning` -- training pathways with learning algorithms
