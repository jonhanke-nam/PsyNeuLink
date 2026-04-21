(learning-and-autodiff)=
# Learning and AutodiffComposition

PsyNeuLink supports learning -- the modification of connection weights during
execution -- in two complementary ways: through native {class}`LearningMechanism`
components, and through the {class}`AutodiffComposition` which delegates
learning to PyTorch. This page explains both approaches, their trade-offs, and
how to choose between them.

## Two approaches to learning

| Aspect                  | Native learning (LearningMechanisms)                  | AutodiffComposition (PyTorch)                     |
|-------------------------|-------------------------------------------------------|---------------------------------------------------|
| **Speed**               | Slower (pure Python/PsyNeuLink execution)             | Much faster (up to ~1000x via PyTorch)            |
| **Modularity**          | Full exposition of every learning component            | Learning internals are opaque (inside PyTorch)    |
| **Inspectability**      | Every signal, error, and weight update is visible      | Only inputs/outputs are visible to PsyNeuLink     |
| **Integration**         | All components are PsyNeuLink objects (loggable, modulable) | Processing pathway is translated to PyTorch   |
| **Best for**            | Story-boarding, teaching, debugging, small models      | Production simulations, large networks            |

The two approaches share the same model specification syntax: in many cases, you
can switch from native learning to AutodiffComposition simply by changing the
Composition class. This design lets you prototype and debug a model using native
learning (where every component is inspectable), then switch to
AutodiffComposition for efficient training.

## Native learning with LearningMechanisms

### How native learning works

Native learning uses three kinds of components:

1. **LearningMechanism** -- computes weight updates based on error signals.
   The specific learning rule is determined by the {class}`LearningFunction`
   assigned to the Mechanism (e.g., `Hebbian`, `Reinforcement`,
   `BackPropagation`, `TDLearning`).

2. **LearningSignal** -- a specialized {class}`OutputPort` of a
   LearningMechanism that carries the computed weight update.

3. **LearningProjection** -- transmits the weight update from a LearningSignal
   to the {class}`ParameterPort` of the {class}`MappingProjection` being
   learned, where it modifies the `matrix` parameter.

### Automatic construction

For common learning architectures, PsyNeuLink provides Composition methods
that automatically construct the full set of learning components:

- `add_backpropagation_learning_pathway()` -- creates a supervised
  backpropagation pathway, including all necessary LearningMechanisms,
  ComparatorMechanisms (for computing error at the output layer), and
  LearningProjections.
- `add_reinforcement_learning_pathway()` -- creates a reinforcement learning
  pathway.
- `add_td_learning_pathway()` -- creates a temporal difference learning
  pathway.

These methods return a dictionary of the learning components they create,
including a `TARGET_MECHANISM` that receives the target inputs during training.

### Example: XOR with backpropagation

The following implements a three-layer network that learns the XOR function
using native backpropagation:

```python
# Construct the processing pathway
input = ProcessingMechanism(name='Input', default_variable=np.zeros(2))
hidden = ProcessingMechanism(name='Hidden', default_variable=np.zeros(10),
                              function=Logistic())
output = ProcessingMechanism(name='Output', default_variable=np.zeros(1),
                              function=Logistic())

input_weights = MappingProjection(name='Input Weights',
                                   matrix=np.random.rand(2, 10))
output_weights = MappingProjection(name='Output Weights',
                                    matrix=np.random.rand(10, 1))

# Create the Composition and add a backpropagation learning pathway
xor_comp = Composition('XOR Composition')
learning_components = xor_comp.add_backpropagation_learning_pathway(
    pathway=[input, input_weights, hidden, output_weights, output]
)
target = learning_components[TARGET_MECHANISM]

# Define training data
xor_inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
xor_targets = [[0], [1], [1], [0]]

# Train
xor_comp.learn(inputs={input: xor_inputs, target: xor_targets})
```

The call to `add_backpropagation_learning_pathway` creates:

- A **ComparatorMechanism** (also called a TARGET_MECHANISM) at the output that
  computes the difference between the network's output and the target.
- A **LearningMechanism** for each MappingProjection in the pathway, each
  configured with the `BackPropagation` LearningFunction.
- **LearningProjections** from each LearningMechanism to the ParameterPort of
  its corresponding MappingProjection.
- All necessary intermediate Projections for propagating error signals backward
  through the network.

Calling `show_graph(show_learning=True)` on the Composition reveals all of
these components, which is invaluable for understanding the flow of error
signals.

### Building complex learning architectures

Multiple calls to learning pathway methods can be combined to build complex
architectures. For example, the Rumelhart Semantic Network
([Rumelhart & Todd, 1993](https://psycnet.apa.org/record/1993-97600-001))
has a branching structure with one input path splitting into multiple output
paths:

```python
comp = Composition(name='Rumelhart Semantic Network')
comp.add_backpropagation_learning_pathway(pathway=[rel_in, rel_hidden])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, rep_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, prop_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, qual_out])
comp.add_backpropagation_learning_pathway(pathway=[rel_hidden, act_out])
comp.add_backpropagation_learning_pathway(pathway=[rep_in, rep_hidden, rel_hidden])
```

PsyNeuLink correctly wires the learning components across all pathways,
ensuring that error signals from multiple output branches are properly
backpropagated through shared hidden layers.

### Unsupervised learning

Native learning also supports unsupervised rules. For example, Hebbian
learning can be configured by assigning the `Hebbian` LearningFunction to a
LearningMechanism. In unsupervised learning, there is no target signal; the
weight update depends only on the activations of the connected Mechanisms.

### Running with and without learning

A Composition with learning components can be run in two modes:

- `comp.learn(inputs=...)` -- executes the model *with* learning enabled;
  weight updates are applied after each trial.
- `comp.run(inputs=...)` -- executes the model *without* learning; weights
  remain fixed. This is useful for testing a trained model.

## AutodiffComposition and PyTorch integration

### Why AutodiffComposition exists

For networks of any appreciable size, native learning in PsyNeuLink is slow.
Each LearningMechanism, LearningProjection, and error Projection is a
full PsyNeuLink Component, executed in Python. This is excellent for
transparency and debugging, but for training a network on thousands of trials,
the overhead is prohibitive.

{class}`AutodiffComposition` solves this by translating the processing pathway
into a [PyTorch](https://pytorch.org) model and delegating the
forward pass and backpropagation to PyTorch's optimized C++/CUDA backend. This
can yield speedups of up to three orders of magnitude.

### How to use AutodiffComposition

In many cases, switching to AutodiffComposition requires only changing the
Composition class:

```python
# Instead of:
comp = Composition(name='Rumelhart Semantic Network')

# Use:
comp = AutodiffComposition(name='Rumelhart Semantic Network')
```

The rest of the model specification -- adding pathways, specifying Mechanisms
and Projections -- remains identical. The `learn` method works the same way.

### What AutodiffComposition handles

When `learn` is called on an AutodiffComposition:

1. The processing pathway is translated into an equivalent PyTorch `nn.Module`.
2. MappingProjection matrices become PyTorch parameter tensors.
3. Mechanism Functions are mapped to their PyTorch equivalents (e.g.,
   `Logistic` becomes `torch.sigmoid`).
4. PyTorch handles the forward pass, loss computation, and backpropagation.
5. After training, the updated weights are written back to the PsyNeuLink
   MappingProjection matrices.

### What AutodiffComposition does NOT handle

Because PyTorch handles execution internally, some PsyNeuLink features are not
available during AutodiffComposition learning:

- Individual LearningMechanisms and their signals are not created or visible.
- Logging of intermediate learning computations is not available.
- Custom Conditions on the Scheduler do not apply to the PyTorch execution.
- Modulatory mechanisms (control, gating) that target components within the
  learning pathway are not active during PyTorch execution.

However, when the AutodiffComposition is run (without learning) using its `run`
method, it reverts to standard PsyNeuLink execution, and all of these features
become available again.

## Choosing between native learning and AutodiffComposition

Use **native learning** when:

- You are prototyping a model and want to inspect every learning component.
- You need to teach or demonstrate how a learning algorithm works.
- The model is small enough that training speed is not a concern.
- You need to modulate learning components with control mechanisms.
- You are implementing a custom or unusual learning rule that is not
  easily expressed in PyTorch.

Use **AutodiffComposition** when:

- You need to train a model on large datasets or for many epochs.
- The learning algorithm is standard (backpropagation with standard
  optimizers).
- You want to integrate a trained neural network into a larger PsyNeuLink
  model that includes control, scheduling, or other non-learning components.

A common workflow is:

1. Build the model using native learning to verify correctness.
2. Switch to AutodiffComposition for efficient training.
3. Embed the trained AutodiffComposition as a node in a larger Composition
   that includes control or other components.

## Summary

- **Native learning** uses LearningMechanisms, LearningSignals, and
  LearningProjections to implement learning rules as transparent, inspectable
  PsyNeuLink Components. Methods like `add_backpropagation_learning_pathway`
  automate the construction of complex learning architectures.
- **AutodiffComposition** delegates learning to PyTorch for dramatically
  faster execution, using the same model specification syntax.
- The two approaches are complementary: native learning prioritizes
  **modularity and exposition**, while AutodiffComposition prioritizes
  **computational efficiency**.
- Models can be prototyped with native learning, trained with
  AutodiffComposition, and then integrated into larger system-level models
  that include control and multi-timescale scheduling.
