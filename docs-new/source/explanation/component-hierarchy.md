(component-hierarchy)=
# Component Hierarchy

Every object in PsyNeuLink inherits from {class}`Component`, which provides a
common interface for computation, parameterization, and logging. This page
presents the complete class hierarchy and explains when and why you would use
each type.

## The full class tree

The tree below shows every built-in Component and Composition type shipped with
PsyNeuLink. Indentation indicates inheritance.

```
Component
├── Mechanism
│   ├── ProcessingMechanism
│   │   ├── TransferMechanism
│   │   ├── IntegratorMechanism
│   │   └── ObjectiveMechanism
│   └── ModulatoryMechanism
│       ├── ControlMechanism
│       └── LearningMechanism
│
├── Projection
│   ├── PathwayProjection
│   │   ├── MappingProjection
│   │   ├── MaskedMappingProjection
│   │   └── AutoAssociativeProjection
│   └── ModulatoryProjection
│       ├── LearningProjection
│       ├── ControlProjection
│       └── GatingProjection
│
├── Port
│   ├── InputPort
│   ├── ParameterPort
│   ├── OutputPort
│   └── ModulatorySignal
│       ├── LearningSignal
│       ├── ControlSignal
│       └── GatingSignal
│
└── Function
    ├── NonStatefulFunctions
    │   ├── DistributionFunctions
    │   ├── LearningFunctions
    │   ├── ObjectiveFunctions
    │   ├── OptimizationFunctions
    │   ├── SelectionFunctions
    │   ├── TransferFunctions
    │   ├── TimerFunctions
    │   └── TransformFunctions
    ├── StatefulFunctions
    │   ├── IntegratorFunctions
    │   └── MemoryFunctions
    └── UserDefinedFunction

Composition
├── AutodiffComposition
├── CompositionFunctionApproximator
└── ParameterEstimationComposition

Services
├── Registry
├── Preferences
├── Visualization
├── Scheduling
├── Compilation
├── Report
├── Log
├── MDF
└── Graph
```

The sections below walk through each major branch.

---

## Mechanisms

A {class}`Mechanism` is the fundamental processing unit in PsyNeuLink. Every
Mechanism has one or more {class}`InputPort`s, a {class}`Function`, and one or
more {class}`OutputPort`s.

### ProcessingMechanism

{class}`ProcessingMechanism` is the base class for Mechanisms that directly
transform information. Unless you need specialized behavior, a plain
`ProcessingMechanism` with an appropriate Function is often all you need.

| Subclass                  | Purpose                                                                 | Typical use                                               |
|---------------------------|-------------------------------------------------------------------------|-----------------------------------------------------------|
| {class}`TransferMechanism`| Applies a transfer function (Linear, Logistic, etc.) with optional integration and termination | Layers in a neural network, units that settle over time   |
| {class}`IntegratorMechanism`| Integrates its input over time using an integrator function              | Leaky integration, evidence accumulation                  |
| {class}`ObjectiveMechanism`| Evaluates output of other Mechanisms using an objective function          | Monitoring conflict, computing error signals for control  |

:::{note}
The PsyNeuLink Library extends `ProcessingMechanism` with additional
specialized types such as `DDM` (drift diffusion model),
`LCAMechanism` (leaky competing accumulator), `KWTAMechanism`
(k-winners-take-all), and others. Consult the Library reference for the
full list.
:::

#### When to use each ProcessingMechanism

- **ProcessingMechanism (base):** Use when you need a simple, general-purpose
  node with a configurable Function. Works well for layers of feedforward
  networks, abstract processing stages, or as a wrapper for a custom Python
  function.

- **TransferMechanism:** Use when you need a node whose output is defined by a
  transfer function (e.g., Logistic, ReLU) and that optionally integrates its
  input over time before applying the transfer function. The
  `termination_threshold` parameter lets it run until its output stabilizes,
  which is useful for recurrent networks that need to settle.

- **IntegratorMechanism:** Use when the primary computation *is* temporal
  integration -- for example, accumulating evidence over time steps. Unlike
  TransferMechanism's optional integration mode, IntegratorMechanism's core
  Function is an integrator, making the integration parameters directly
  accessible and modulable.

- **ObjectiveMechanism:** Use when you need to evaluate the output of one or
  more other Mechanisms according to some criterion (e.g., computing energy /
  conflict, computing error relative to a target). ObjectiveMechanisms are
  commonly used as the input stage for a ControlMechanism.

### ModulatoryMechanism

{class}`ModulatoryMechanism` is the base class for Mechanisms that regulate the
operation of other Components rather than directly processing information.

| Subclass                           | Purpose                                                            | Typical use                                        |
|------------------------------------|--------------------------------------------------------------------|----------------------------------------------------|
| {class}`ControlMechanism`          | Modulates parameters of other Mechanisms via ControlProjections    | Gain modulation, adaptive control of processing    |
| {class}`LearningMechanism`         | Modifies MappingProjection matrices via LearningProjections        | Hebbian learning, backpropagation, reinforcement   |

#### When to use each ModulatoryMechanism

- **ControlMechanism:** Use when your model needs to dynamically adjust a
  parameter of another Mechanism (such as the gain of a Logistic function, or
  the threshold of a DDM). ControlMechanisms typically receive input from an
  ObjectiveMechanism that monitors some aspect of processing (e.g., conflict,
  reward), and project ControlSignals to the ParameterPorts of the regulated
  Mechanisms. Specialized subtypes include `OptimizationControlMechanism`
  (which runs internal simulations to optimize control allocation) and
  `GatingMechanism` (which modulates the input or output of a Mechanism
  rather than a function parameter).

- **LearningMechanism:** Use when your model needs to learn -- that is, to
  modify connection weights during execution. The type of learning is
  determined by the LearningFunction assigned to the Mechanism (e.g.,
  `Hebbian`, `Reinforcement`, `BackPropagation`).

---

## Projections

A {class}`Projection` transmits information from one Component to another.
Every Projection has a `sender` (an OutputPort or ModulatorySignal) and a
`receiver` (an InputPort, ParameterPort, or other Port).

### PathwayProjection

{class}`PathwayProjection` carries information along a processing pathway.

| Subclass                          | Purpose                                                          | Typical use                                         |
|-----------------------------------|------------------------------------------------------------------|-----------------------------------------------------|
| {class}`MappingProjection`        | General-purpose weighted connection between Mechanisms            | Feedforward and recurrent connections in a network  |
| {class}`MaskedMappingProjection`  | MappingProjection with a static binary mask applied to its matrix | Sparse or structured connectivity patterns          |
| {class}`AutoAssociativeProjection`| MappingProjection from a Mechanism back to itself                 | Self-recurrent connections (e.g., in an LCA)        |

#### When to use each PathwayProjection

- **MappingProjection:** The default and most common Projection type. Use it
  whenever you need to connect two Mechanisms. Its `matrix` parameter defines
  the weight transformation. PsyNeuLink creates MappingProjections
  automatically when you specify a pathway, defaulting to full connectivity
  with unit weights.

- **MaskedMappingProjection:** Use when you need structured sparsity -- for
  example, connecting only corresponding elements of two arrays (a diagonal
  mask) or enforcing a particular wiring pattern. The mask is applied
  element-wise to the weight matrix.

- **AutoAssociativeProjection:** Use for self-recurrent connections. This is
  a convenience class: it creates a MappingProjection whose sender and
  receiver are the same Mechanism. Commonly used with recurrent network
  Mechanisms like `RecurrentTransferMechanism`.

### ModulatoryProjection

{class}`ModulatoryProjection` carries modulatory signals that regulate the
functioning of other Components.

| Subclass                    | Purpose                                                          | Typical use                                      |
|-----------------------------|------------------------------------------------------------------|--------------------------------------------------|
| {class}`ControlProjection`  | Transmits a ControlSignal to a ParameterPort                     | Adjusting gain, threshold, or noise of a Mechanism|
| {class}`GatingProjection`   | Transmits a GatingSignal to an InputPort or OutputPort           | Gating (enabling/disabling) input or output      |
| {class}`LearningProjection` | Transmits a LearningSignal to a MappingProjection's ParameterPort| Updating connection weights during learning      |

---

## Ports

A {class}`Port` is a Component that belongs to a Mechanism or Projection and
represents one of its interfaces. Ports have their own Functions, which
determine how incoming information is combined.

### Standard Ports

| Port type            | Belongs to            | Purpose                                                         |
|----------------------|-----------------------|-----------------------------------------------------------------|
| {class}`InputPort`   | Mechanism             | Receives PathwayProjections; combines them into one input item  |
| {class}`OutputPort`  | Mechanism             | Extracts a value from the Mechanism's output; sends it onward   |
| {class}`ParameterPort`| Mechanism or Projection| Represents a modulable parameter; receives ModulatoryProjections|

A Mechanism can have multiple InputPorts (each representing a distinct input
channel) and multiple OutputPorts (each representing a distinct output value).
ParameterPorts are created automatically for every modulable parameter.

### ModulatorySignals

ModulatorySignals are specialized OutputPorts that belong to ModulatoryMechanisms:

| Signal type            | Belongs to            | Sends                   | Receives by              |
|------------------------|-----------------------|-------------------------|--------------------------|
| {class}`ControlSignal` | ControlMechanism      | {class}`ControlProjection`| ParameterPort, InputPort, or OutputPort |
| {class}`GatingSignal`  | GatingMechanism       | {class}`GatingProjection` | InputPort or OutputPort  |
| {class}`LearningSignal`| LearningMechanism     | {class}`LearningProjection`| ParameterPort of a MappingProjection |

---

## Functions

A {class}`Function` is the most fundamental unit of computation in PsyNeuLink.
Every Component has at least one Function. Functions wrap a callable together
with persistent parameters, making those parameters available for modulation
and logging.

### Non-stateful Functions

These Functions produce the same output for the same input regardless of
history:

| Category                    | Examples                                                     | Typical use                                     |
|-----------------------------|--------------------------------------------------------------|-------------------------------------------------|
| {class}`TransferFunctions`  | `Linear`, `Logistic`, `ReLU`, `SoftMax`, `Gaussian`          | Activation functions in neural network layers   |
| {class}`TransformFunctions` | `LinearMatrix`, `MatrixTransform`                            | Weight matrices, coordinate transforms          |
| {class}`DistributionFunctions`| `NormalDist`, `UniformDist`, `ExponentialDist`             | Stochastic inputs, noise generation             |
| {class}`ObjectiveFunctions` | `Stability`, `Energy`, `Distance`                            | Evaluating network states, computing error      |
| {class}`LearningFunctions`  | `Hebbian`, `Reinforcement`, `BackPropagation`, `TDLearning`  | Weight update rules                             |
| {class}`OptimizationFunctions`| `GradientOptimization`, `GridSearch`                       | Parameter optimization in control               |
| {class}`SelectionFunctions` | `OneHot`, `Threshold`                                        | Winner-take-all, thresholding                   |
| {class}`TimerFunctions`     | Various timer utilities                                      | Time-dependent computations                     |

### Stateful Functions

These Functions maintain internal state that evolves across executions:

| Category                    | Examples                                                     | Typical use                                     |
|-----------------------------|--------------------------------------------------------------|-------------------------------------------------|
| {class}`IntegratorFunctions`| `AdaptiveIntegrator`, `DriftDiffusionIntegrator`, `LeakyCompetingIntegrator`| Evidence accumulation, temporal smoothing |
| {class}`MemoryFunctions`    | `Buffer`, `ContentAddressableMemory`, `DictionaryMemory`     | Working memory, episodic memory retrieval       |

### UserDefinedFunction

{class}`UserDefinedFunction` wraps any Python callable as a PsyNeuLink
Function. When you assign a plain Python function to a Mechanism's `function`
parameter, PsyNeuLink automatically wraps it in a UserDefinedFunction. This
makes the function's keyword arguments available as modulable parameters.

```python
def my_function(variable, gain=1.0, bias=0.0):
    return gain * variable + bias

mech = ProcessingMechanism(function=my_function)
# gain and bias are now modulable parameters
```

---

## Compositions

While Components perform individual computations, {class}`Composition` objects
assemble them into executable models.

| Composition type                        | Purpose                                                               |
|-----------------------------------------|-----------------------------------------------------------------------|
| {class}`Composition`                    | General-purpose model container; supports processing, control, learning|
| {class}`AutodiffComposition`            | Uses PyTorch for accelerated learning (up to 1000x faster)            |
| {class}`CompositionFunctionApproximator`| Used internally by OptimizationControlMechanism for function approximation|
| {class}`ParameterEstimationComposition` | Wraps a Composition for parameter estimation and model fitting        |

#### When to use each Composition type

- **Composition:** The default choice for any model. Supports all PsyNeuLink
  features, including native learning with full exposition of learning
  components, control, and nested compositions.

- **AutodiffComposition:** Use when your model includes learning and you
  need computational efficiency. It translates the processing pathway into a
  PyTorch model for execution, providing dramatic speedups while retaining
  the ability to interface with other PsyNeuLink components.

- **ParameterEstimationComposition:** Use when you need to fit model
  parameters to empirical data. It wraps a model Composition and provides
  methods for parameter estimation and optimization.

---

## Choosing the right component

When building a model, the following decision process is a useful guide:

1. **What computation does the node perform?** This determines the Mechanism
   type and its Function.
2. **How are nodes connected?** This determines the Projection type and matrix.
3. **Does any node need to regulate another?** If so, add a
   ModulatoryMechanism (Control or Learning) with appropriate
   ModulatoryProjections.
4. **Do different parts of the model run on different time scales?** If so,
   configure Conditions on the Composition's Scheduler (see
   {doc}`scheduling-and-execution`).
5. **Does the model need to learn?** If so, choose between native
   LearningMechanisms (for modularity and exposition) and
   AutodiffComposition (for speed). See {doc}`learning-and-autodiff`.
