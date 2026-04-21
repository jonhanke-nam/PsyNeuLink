(learning-tutorial)=
# Learning

PsyNeuLink supports learning in two ways: a native implementation using
{class}`LearningMechanisms <LearningMechanism>`, and an integrated PyTorch-based
implementation using {class}`AutodiffComposition`. This tutorial covers both approaches
with complete examples.

## Two Approaches to Learning

| Approach | Best for | Speed |
|----------|----------|-------|
| {class}`LearningMechanism` (native) | Story-boarding, understanding algorithm flow, small models | Slower |
| {class}`AutodiffComposition` (PyTorch) | Large-scale training, production models | Much faster (up to 1000x) |

The native approach exposes every component of the learning algorithm as explicit
PsyNeuLink objects, making the flow of signals and errors visible and inspectable. The
AutodiffComposition approach delegates computation to PyTorch while maintaining the same
PsyNeuLink model specification.

## Native Learning with LearningMechanisms

### How It Works

A {class}`LearningMechanism` receives a target and/or error signal and uses a
{ref}`LearningFunction <LearningFunctions>` to compute weight updates. The updates are
sent via {class}`LearningProjections <LearningProjection>` to the
{class}`MappingProjections <MappingProjection>` being trained.

The components are:

- **LearningMechanism** -- computes weight updates using a learning rule
- **LearningSignal** -- an {class}`OutputPort` of the LearningMechanism that sends updates
- **LearningProjection** -- carries the update to the MappingProjection's matrix
- **ComparatorMechanism** -- compares actual output to target (for supervised learning)

PsyNeuLink provides methods that create all of these automatically.

### Supported Learning Rules

| Function | Algorithm |
|----------|-----------|
| {class}`BackPropagation` | Backpropagation of error |
| {class}`Hebbian` | Hebbian (unsupervised correlation-based) learning |
| {class}`Reinforcement` | Reinforcement learning |
| {class}`TDLearning` | Temporal difference learning |

### XOR Example

The classic XOR problem demonstrates backpropagation learning in a three-layer network.
The network must learn a non-linear mapping that cannot be solved by a single layer:

| Input | Target |
|-------|--------|
| [0, 0] | [0] |
| [0, 1] | [1] |
| [1, 0] | [1] |
| [1, 1] | [0] |

Here is the complete implementation:

```python
import numpy as np
import psyneulink as pnl

# Construct Processing Mechanisms and Projections
input = pnl.ProcessingMechanism(name='Input', default_variable=np.zeros(2))
hidden = pnl.ProcessingMechanism(name='Hidden', default_variable=np.zeros(10),
                                  function=pnl.Logistic())
output = pnl.ProcessingMechanism(name='Output', default_variable=np.zeros(1),
                                  function=pnl.Logistic())
input_weights = pnl.MappingProjection(name='Input Weights',
                                       matrix=np.random.rand(2, 10))
output_weights = pnl.MappingProjection(name='Output Weights',
                                        matrix=np.random.rand(10, 1))

# Create Composition and add learning pathway
xor_comp = pnl.Composition('XOR Composition')
learning_components = xor_comp.add_backpropagation_learning_pathway(
    pathway=[input, input_weights, hidden, output_weights, output]
)
target = learning_components[pnl.TARGET_MECHANISM]
```

The call to {meth}`~Composition.add_backpropagation_learning_pathway` does all the work:
it creates the ComparatorMechanism, LearningMechanisms, and all necessary Projections.
It returns a dictionary of the learning components, including the `TARGET_MECHANISM` that
you need to provide target values during training.

### Visualizing Learning Components

```python
xor_comp.show_graph(show_learning=True)
```

```{figure} ../_static/BasicsAndPrimer_XOR_Model_fig.svg
:width: 100%

**XOR Model.** Items in orange are learning components created by `add_backpropagation_learning_pathway`.
Diamonds represent MappingProjections shown as nodes so that the LearningProjections to them are visible.
```

### Training the XOR Model

Provide input stimuli and corresponding targets, then call {meth}`~Composition.learn`:

```python
# Define training data
xor_inputs = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
xor_targets = np.array([[0], [1], [1], [0]])

# Identify the target mechanism
target_mech = learning_components[pnl.TARGET_MECHANISM]

# Train the model
result = xor_comp.learn(
    inputs={input: xor_inputs, target_mech: xor_targets},
    num_trials=2
)
```

The `learn` method runs the model with learning enabled. Each trial presents one
input-target pair and updates the weights of the MappingProjections.

### Running Without Learning

After training, you can run the model in inference mode:

```python
result = xor_comp.run(
    inputs={input: [[0, 1]]},
    # Learning is disabled by default when using run() instead of learn()
)
print(result)
```

## The Rumelhart Semantic Network

The XOR model demonstrates learning on a simple linear pathway. But PsyNeuLink can handle
complex, branching architectures by making multiple calls to the learning pathway methods.

The following implements the semantic network from
[Rumelhart & Todd, 1993](https://psycnet.apa.org/record/1993-97600-001), which has
multiple output branches sharing a common hidden representation:

```text
#  Represention  Property  Quality  Action
#           \________\_______/_______/
#                        |
#                 Relations_Hidden
#                   _____|_____
#                  /           \
#   Representation_Hidden  Relations_Input
#               /
#   Representation_Input
```

```python
import psyneulink as pnl

# Construct Mechanisms
rep_in = pnl.ProcessingMechanism(input_shapes=10, name='REP_IN')
rel_in = pnl.ProcessingMechanism(input_shapes=11, name='REL_IN')
rep_hidden = pnl.ProcessingMechanism(input_shapes=4, function=pnl.Logistic, name='REP_HIDDEN')
rel_hidden = pnl.ProcessingMechanism(input_shapes=5, function=pnl.Logistic, name='REL_HIDDEN')
rep_out = pnl.ProcessingMechanism(input_shapes=10, function=pnl.Logistic, name='REP_OUT')
prop_out = pnl.ProcessingMechanism(input_shapes=12, function=pnl.Logistic, name='PROP_OUT')
qual_out = pnl.ProcessingMechanism(input_shapes=13, function=pnl.Logistic, name='QUAL_OUT')
act_out = pnl.ProcessingMechanism(input_shapes=14, function=pnl.Logistic, name='ACT_OUT')

# Construct Composition with learning pathways
comp = pnl.Composition(name='Rumelhart Semantic Network')
comp.add_backpropagation_learning_pathway(pathway=[rel_in, rel_hidden])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, rep_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, prop_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, qual_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, act_out])
comp.add_backpropagation_learning_pathway(pathway=[rep_in, rep_hidden, rel_hidden])

comp.show_graph(show_learning=True)
```

Each call to `add_backpropagation_learning_pathway` creates the learning components for
one segment of the network. PsyNeuLink automatically coordinates the error signals across
the shared `rel_hidden` node.

```{figure} ../_static/BasicsAndPrimer_Rumelhart_Network.svg
:width: 75%

**Rumelhart Semantic Network.** Items in orange are learning components. Diamonds represent
MappingProjections shown as nodes so that LearningProjections to them are visible.
```

## AutodiffComposition (PyTorch Integration)

Training the Rumelhart network with native LearningMechanisms can be slow due to the large
number of learning components. The {class}`AutodiffComposition` solves this by using
[PyTorch](https://pytorch.org) for the actual learning computation while maintaining the
same PsyNeuLink model specification.

### Converting to AutodiffComposition

The change is minimal -- just replace `Composition` with `AutodiffComposition`:

```python
comp = pnl.AutodiffComposition(name='Rumelhart Semantic Network')
comp.add_backpropagation_learning_pathway(pathway=[rel_in, rel_hidden])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, rep_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, prop_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, qual_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, act_out])
comp.add_backpropagation_learning_pathway(pathway=[rep_in, rep_hidden, rel_hidden])
```

### Performance

The AutodiffComposition can be as much as three orders of magnitude faster than the native
implementation, because PyTorch handles the forward and backward passes in optimized C++
code (and optionally on GPU).

### Trade-offs

| Feature | Native (Composition) | AutodiffComposition |
|---------|---------------------|---------------------|
| Speed | Slower | Much faster |
| Visibility | Full -- every learning component is a PsyNeuLink object | Learning internals are opaque |
| Flexibility | Can mix learning with custom scheduling, control, etc. | Restricted to standard backpropagation |
| Integration | All components available for inspection and logging | Trained weights are transferred back to PsyNeuLink |

See {ref}`Composition_Learning` and {ref}`Composition_Learning_AutodiffComposition` for a
complete comparison.

### Workflow

A typical workflow is:

1. **Prototype** the model using a standard Composition with native learning -- inspect
   the learning components to verify correctness.
2. **Train** the model using AutodiffComposition for speed.
3. **Integrate** the trained model back into a standard Composition if you need features
   like control, custom scheduling, or nested compositions.

## Learning Pathway Methods

A Composition provides several methods for adding learning pathways, each implementing a
different algorithm:

| Method | Algorithm |
|--------|-----------|
| {meth}`~Composition.add_backpropagation_learning_pathway` | Backpropagation of error |
| {meth}`~Composition.add_reinforcement_learning_pathway` | Reinforcement learning |
| {meth}`~Composition.add_td_learning_pathway` | Temporal difference learning |

Each method creates all the necessary LearningMechanisms, ComparatorMechanisms, and
Projections for the specified algorithm.

## The learn() Method

Training is done by calling {meth}`~Composition.learn` instead of
{meth}`~Composition.run`:

```python
comp.learn(
    inputs={input_mech: input_data, target_mech: target_data},
    num_trials=1000
)
```

Key arguments:

- **inputs** -- dictionary mapping INPUT Mechanisms and TARGET Mechanisms to their data
- **num_trials** -- how many trials to run (cycles through the input data)
- **learning_rate** -- override the default learning rate

After training, call `run()` to execute the model without learning:

```python
result = comp.run(inputs={input_mech: test_data})
```

## Next Steps

- {doc}`control` -- combining learning with control mechanisms
- {doc}`basics-and-primer` -- comprehensive reference covering all topics
