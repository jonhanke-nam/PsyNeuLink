(architecture)=
# Architecture Overview

PsyNeuLink is a block-modeling environment for constructing, simulating, and
analyzing computational models of neural and cognitive processes. This page
explains the fundamental design decisions that shape the framework and the three
core abstractions on which every model is built.

## Design philosophy

PsyNeuLink occupies a particular niche in the landscape of computational
modeling tools. It is designed to be:

- **Computationally general** -- it can represent processes that range from
  individual neurons or neural populations to abstract cognitive functions, and
  can mix levels of analysis within a single model.
- **Integrative** -- it provides a standard environment for model comparison,
  sharing, and documentation, and for composing components that rely on very
  different forms of computation (e.g., a neural network alongside a drift
  diffusion decision process).
- **Extensible** -- its API allows components from other packages (PyTorch,
  Nengo, ACT-R, etc.) to be wrapped and integrated into PsyNeuLink models.

The trade-off is that PsyNeuLink prioritizes flexibility and interpretability
over raw computational speed. For large-scale deep-learning workloads or
highly detailed biophysical simulations, specialized tools will be faster.
PsyNeuLink's strength is in letting you *compose* such models at the system
level and explore how they interact.

## The three core abstractions

Every PsyNeuLink model is built from three kinds of objects:

| Abstraction     | Role                                            | Graph analogy | Neuroscience analogy         |
|-----------------|-------------------------------------------------|---------------|------------------------------|
| **Mechanism**   | Performs a computation on its inputs             | Node          | Neural population / process  |
| **Projection**  | Transmits information between Mechanisms         | Directed edge | Synaptic pathway / connection|
| **Composition** | Groups Mechanisms and Projections into a model   | Graph         | Circuit / system             |

### Mechanisms

A {class}`Mechanism` is the fundamental unit of processing. It receives one or
more inputs (via its {class}`InputPort`s), applies a {class}`Function` to
transform or combine them, and makes the result available through its
{class}`OutputPort`s.

PsyNeuLink ships with a rich library of Mechanism types. At the highest level
they divide into two families:

- **ProcessingMechanisms** directly transmit and transform information. Examples
  include {class}`TransferMechanism` (general-purpose linear or nonlinear
  transformation), {class}`IntegratorMechanism` (temporal integration), and
  the {class}`DDM` (drift diffusion decision model).

- **ModulatoryMechanisms** modify or modulate the processing performed by other
  Components. There are two main subtypes:
  - {class}`ControlMechanism` -- adjusts parameters, inputs, or outputs of
    other Mechanisms (e.g., gain modulation).
  - {class}`LearningMechanism` -- modifies the matrices of
    {class}`MappingProjection`s to implement learning rules.

Because a Mechanism's computation is defined by a pluggable {class}`Function`,
the same Mechanism class can implement very different operations simply by
swapping functions. Any Python callable that respects the expected input shape
can be used, giving modelers enormous flexibility.

### Projections

A {class}`Projection` connects the {class}`OutputPort` of one Mechanism (or
Composition) to the {class}`InputPort` (or {class}`ParameterPort`) of another.
Like Mechanisms, Projections come in two families that mirror the processing /
modulation distinction:

- **PathwayProjections** carry information along processing pathways. The most
  common type is {class}`MappingProjection`, which applies a weight matrix to
  transform the sender's output into the receiver's input.

- **ModulatoryProjections** carry modulatory signals.
  {class}`ControlProjection` transmits control signals that modify parameters,
  and {class}`LearningProjection` transmits weight updates computed by a
  LearningMechanism.

### Compositions

A {class}`Composition` assembles Mechanisms and Projections into a directed
graph that represents a complete model (or a submodel). The Composition's graph
determines the default order of execution: information flows from `INPUT` nodes
(colored green in graph displays) through the graph to `OUTPUT` nodes (colored
red).

Key properties of Compositions:

- **Automatic wiring.** When you add Mechanisms to a Composition in a pathway
  list, PsyNeuLink automatically creates the necessary MappingProjections
  between them, choosing sensible defaults for matrix sizes and connectivity.

- **Hierarchical nesting.** A Composition can contain other Compositions as
  nodes, receiving and sending Projections just like a Mechanism. This lets you
  build models with multiple levels of organization -- for instance, a
  system-level model whose nodes are themselves neural-circuit-level
  sub-models.

- **Graph export.** The Composition's graph is stored in a standard dependency
  dictionary format and can be exported to JSON (using the emerging
  [MDF](https://github.com/ModECI/MDF) standard), or submitted to graph
  analysis libraries like NetworkX or igraph.

## Processing vs. modulation

One of the most important architectural distinctions in PsyNeuLink is between
*processing* and *modulation*:

```
Processing pathway          Modulatory pathway
==================          ===================
ProcessingMechanism  -----> ControlMechanism
        |                         |
  PathwayProjection         ModulatoryProjection
        |                         |
        v                         v
ProcessingMechanism         ParameterPort of
                            a ProcessingMechanism
```

**Processing** is the direct flow of information through the model -- inputs
are transformed by Mechanisms, transmitted by MappingProjections, and
ultimately produce outputs.

**Modulation** is a secondary flow that *regulates* processing. A
ControlMechanism evaluates some aspect of the processing (e.g., conflict
between competing responses) and adjusts a parameter (e.g., the gain of a
Logistic function) via a ControlProjection to the relevant ParameterPort. This
separation mirrors the neuroscience distinction between feedforward information
processing and neuromodulatory regulation.

LearningMechanisms provide a third kind of modulation -- they modify the
*connection weights* (matrix parameters) of MappingProjections rather than the
operating parameters of Mechanisms.

## The execution model

When a Composition is run (via its `run` method), its components are executed
under the control of a {class}`Scheduler`. Understanding the execution model is
essential for building models that operate across multiple time scales.

### Time-scale hierarchy

PsyNeuLink defines a hierarchy of time scales, from coarsest to finest:

| Time scale       | Description                                                      |
|------------------|------------------------------------------------------------------|
| `TimeScale.RUN`  | A complete call to `Composition.run`, encompassing all trials.   |
| `TimeScale.TRIAL`| A single presentation of one input to the Composition.           |
| `TimeScale.PASS` | One iteration through the graph in which each node gets the opportunity to execute. |
| `TimeScale.TIME_STEP` | A single execution of a single node within a PASS.          |

These time scales nest: a RUN contains one or more TRIALs, each TRIAL contains
one or more PASSes, and each PASS contains one or more TIME_STEPs.

### Scheduler and Conditions

By default, the Scheduler executes every node exactly once per PASS, in the
topological order determined by the graph's edges. However, you can assign
{class}`Condition`s to individual nodes to create more complex execution
patterns:

- Execute a node only after another node has executed a certain number of
  times (e.g., `EveryNExecutions(task, 10)`).
- Execute a node only when a convergence criterion is met (e.g., using a
  custom function that checks whether a recurrent network has settled).
- Terminate a TRIAL when a particular node signals completion (e.g.,
  `WhenFinished(decision)` for a DDM that integrates to threshold).

Conditions can reference pre-specified classes provided by PsyNeuLink, or
arbitrary Python functions. This makes it possible to express virtually any
logically coherent schedule of execution.

### How execution proceeds

1. The Composition's `run` method is called with a dictionary of inputs (one
   entry per `INPUT` node) and, optionally, termination conditions.
2. For each TRIAL, the Scheduler iterates PASSes. In each PASS it walks
   through the graph and checks each node's Conditions. Nodes whose
   Conditions are satisfied execute; others wait.
3. Each node that executes receives input from its afferent Projections,
   runs its Function, and posts its output.
4. The TRIAL ends when the TRIAL termination Condition is met (by default,
   when every node has executed at least once).
5. After all TRIALs, results are collected in `Composition.results`.

If the Composition has a `controller`, it executes at the end (or beginning) of
each TRIAL, evaluating processing outcomes and adjusting parameters for
subsequent processing.

## Hierarchical composition

A powerful consequence of PsyNeuLink's graph-based architecture is that
Compositions can be nested to arbitrary depth. A nested Composition behaves as
a single node in its enclosing Composition: it receives Projections, executes
its internal graph, and sends its outputs onward.

This supports a natural modeling workflow:

1. Build and validate a sub-model (e.g., a visual processing circuit) as a
   standalone Composition.
2. Embed it as a node inside a larger system-level Composition alongside
   other sub-models (e.g., a decision-making module, a motor-planning module).
3. Add modulatory components (control, learning) at the system level that
   operate over the nested Compositions.

Because each nested Composition retains its own Scheduler and internal
structure, it can operate at its own time scale -- for example, a recurrent
network that settles over many PASSes before passing information to a
downstream decision node that integrates over a different time scale.

## Summary

The architecture of PsyNeuLink rests on a small set of interlocking ideas:

- **Mechanisms** compute, **Projections** connect, **Compositions** organize.
- **Processing** and **modulation** are cleanly separated, mirroring the
  neuroscience distinction between information flow and neuromodulatory
  regulation.
- A **Scheduler** with composable **Conditions** governs execution across
  multiple time scales.
- **Hierarchical nesting** of Compositions allows system-level models to be
  assembled from validated sub-models.

These principles combine to give PsyNeuLink its distinctive character: a
framework that is simple enough to express a three-layer feedforward network in
a few lines, yet powerful enough to compose heterogeneous, multi-timescale
models of brain and behavior.
